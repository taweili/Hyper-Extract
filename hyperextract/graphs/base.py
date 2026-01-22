"""Graph Knowledge Pattern - extracts knowledge graphs with nodes and edges from text.

Provides automatic deduplication for both nodes and edges using OMem.
Supports single-stage and two-stage extraction strategies with consistency validation.
"""

from typing import Any, List, Type, Tuple, Callable, TypeVar, Generic, TYPE_CHECKING
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field, create_model
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from ontomem import OMem
from ontomem.merger import MergeStrategy, create_merger, BaseMerger

from ..core.base import BaseAutoType
from ..utils.logging import logger


NodeItem = TypeVar("NodeItem", bound=BaseModel)
EdgeItem = TypeVar("EdgeItem", bound=BaseModel)


class AutoGraphSchema(BaseModel, Generic[NodeItem, EdgeItem]):
    """Generic schema container for graph-based knowledge patterns."""

    nodes: List[NodeItem] = Field(default_factory=list, description="Graph nodes/entities")
    edges: List[EdgeItem] = Field(default_factory=list, description="Graph edges/relationships")


class AutoGraph(BaseAutoType[AutoGraphSchema[NodeItem, EdgeItem]], Generic[NodeItem, EdgeItem]):
    """AutoGraph - extracts knowledge graphs with nodes and edges from text.

    This pattern extracts structured knowledge graphs consisting of entities (nodes) and
    their relationships (edges). Suitable for entity relationship extraction, knowledge
    graph construction, and semantic network building.

    Key characteristics:
        - Extraction target: Graph structure with nodes and edges
        - Deduplication: Automatic deduplication for both nodes and edges using OMem
        - Node merge strategy: Configurable (LLM-powered intelligent merging by default)
        - Edge merge strategy: Configurable (simple merge by default)
        - Extraction modes:
            * one_stage: Extract nodes and edges simultaneously (faster, simpler prompt)
            * two_stage: Extract nodes first, then edges with node context (more accurate)
        - Consistency validation: Ensures edges only connect existing nodes

    Example:
        >>> class Entity(BaseModel):
        ...     name: str
        ...     type: str
        ...     properties: dict = {}
        >>>
        >>> class Relation(BaseModel):
        ...     source: str
        ...     target: str
        ...     relation_type: str
        >>>
        >>> graph = AutoGraph(
        ...     node_schema=Entity,
        ...     edge_schema=Relation,
        ...     node_key_extractor=lambda x: x.name,
        ...     edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
        ...     edge_to_nodes_extractor=lambda x: (x.source, x.target),
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     extraction_mode="two_stage"
        ... )
    """

    if TYPE_CHECKING:
        graph_schema: Type[AutoGraphSchema[NodeItem, EdgeItem]]

    def __init__(
        self,
        node_schema: Type[NodeItem],
        edge_schema: Type[EdgeItem],
        node_key_extractor: Callable[[NodeItem], str],
        edge_key_extractor: Callable[[EdgeItem], str],
        edge_to_nodes_extractor: Callable[[EdgeItem], Tuple[str, str]],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",
        node_strategy_or_merger: MergeStrategy | BaseMerger = MergeStrategy.LLM.BALANCED,
        edge_strategy_or_merger: MergeStrategy | BaseMerger = MergeStrategy.MERGE_FIELD,
        repair_strategy: str = "drop",  # "drop" or "create_ghost"
        prompt: str = "",
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
        max_workers: int = 10,
        show_progress: bool = True,
    ):
        """Initialize AutoGraph with node/edge schemas and configuration.

        Args:
            node_schema: Pydantic BaseModel for nodes/entities.
            edge_schema: Pydantic BaseModel for edges/relationships.
            node_key_extractor: Function to extract unique key from node (e.g., lambda x: x.id).
            edge_key_extractor: Function to extract unique key from edge (e.g., lambda x: f"{x.src}-{x.rel}-{x.dst}").
            edge_to_nodes_extractor: Function to extract (source_key, target_key) from edge for validation.
            llm_client: Language model client for extraction.
            embedder: Embedding model for vector indexing.
            extraction_mode: "one_stage" (extract nodes+edges together) or "two_stage" (nodes first, then edges).
            node_strategy_or_merger: Merge strategy for duplicate nodes (default: LLM.BALANCED).
            edge_strategy_or_merger: Merge strategy for duplicate edges (default: MERGE_FIELD).
            repair_strategy: How to handle dangling edges - "drop" (remove) or "create_ghost" (create minimal nodes).
            prompt: Custom extraction prompt.
            chunk_size: Maximum characters per chunk.
            chunk_overlap: Overlapping characters between chunks.
            max_workers: Maximum concurrent extraction tasks.
            show_progress: Whether to log progress.
        """
        # Store schemas and extractors
        self.node_schema = node_schema
        self.edge_schema = edge_schema
        self.node_key_extractor = node_key_extractor
        self.edge_key_extractor = edge_key_extractor
        self.edge_to_nodes_extractor = edge_to_nodes_extractor
        self.extraction_mode = extraction_mode
        self.repair_strategy = repair_strategy

        # Create dynamic GraphSchema container
        graph_schema_name = f"{node_schema.__name__}{edge_schema.__name__}Graph"
        self.graph_schema = create_model(
            graph_schema_name,
            nodes=(List[node_schema], Field(default_factory=list)),
            edges=(List[edge_schema], Field(default_factory=list)),
        )

        # Initialize Node Merger
        if isinstance(node_strategy_or_merger, BaseMerger):
            self.node_merger = node_strategy_or_merger
        else:
            self.node_merger = create_merger(
                strategy=node_strategy_or_merger,
                key_extractor=node_key_extractor,
                llm_client=llm_client,
                item_schema=node_schema,
            )

        # Initialize Edge Merger
        if isinstance(edge_strategy_or_merger, BaseMerger):
            self.edge_merger = edge_strategy_or_merger
        else:
            self.edge_merger = create_merger(
                strategy=edge_strategy_or_merger,
                key_extractor=edge_key_extractor,
                llm_client=llm_client,
                item_schema=edge_schema,
            )

        # Initialize OMem instances (Before super().__init__)
        self._node_memory = OMem(
            memory_schema=node_schema,
            key_extractor=node_key_extractor,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=self.node_merger,
            verbose=show_progress,
        )

        self._edge_memory = OMem(
            memory_schema=edge_schema,
            key_extractor=edge_key_extractor,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=self.edge_merger,
            verbose=show_progress,
        )

        # Call parent init
        super().__init__(
            data_schema=self.graph_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt or self._default_prompt(),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            show_progress=show_progress,
        )


    def _default_prompt(self) -> str:
        """Returns the default extraction prompt based on extraction mode."""
        if self.extraction_mode == "one_stage":
            return (
                "You are an expert knowledge graph extraction assistant. "
                "Extract entities (nodes) and their relationships (edges) from the following text. "
                "IMPORTANT CONSTRAINT: Every edge must connect two nodes that are present in the nodes list. "
                "Do not create edges between entities that are not explicitly listed as nodes.\n\n"
                "### Source Text:\n"
            )
        else:  # two_stage
            return (
                "You are an expert knowledge extraction assistant. "
                "Extract structured information from the following text according to the specified schema.\n\n"
                "### Source Text:\n"
            )

    @property
    def data(self) -> AutoGraphSchema[NodeItem, EdgeItem]:
        """Returns the current graph state (nodes and edges).

        Returns:
            AutoGraphSchema containing all nodes and edges.
        """
        return self.graph_schema(
            nodes=self._node_memory.items,
            edges=self._edge_memory.items
        )

    def empty(self) -> bool:
        """Checks if the graph is empty (no nodes and no edges).

        Returns:
            True if both node and edge collections are empty, False otherwise.
        """
        return len(self._node_memory.items) == 0 and len(self._edge_memory.items) == 0

    # ==================== State Management Lifecycle Hooks ====================

    def _init_data_state(self) -> None:
        """Initialize or reset graph data structures."""
        if hasattr(self, '_node_memory'):
            self._node_memory.clear()
        if hasattr(self, '_edge_memory'):
            self._edge_memory.clear()

    def _init_index_state(self) -> None:
        """Initialize vector index to empty state."""
        self._index = None

    def _set_data_state(self, data: AutoGraphSchema) -> None:
        """Replace graph data with new data (full reset).

        Args:
            data: New graph data to set.
        """
        self._node_memory.clear()
        self._edge_memory.clear()
        
        if data.nodes:
            self._node_memory.add(data.nodes)
        if data.edges:
            self._edge_memory.add(data.edges)
        
        self.clear_index()

    def _update_data_state(self, incoming_data: AutoGraphSchema) -> None:
        """Merge incoming graph data into current state.

        Args:
            incoming_data: Incremental graph data to merge.
        """
        if self.empty():
            self._set_data_state(incoming_data)
        else:
            if incoming_data.nodes:
                self._node_memory.add(incoming_data.nodes)
            if incoming_data.edges:
                self._edge_memory.add(incoming_data.edges)
            self.clear_index()

    # ==================== Extraction Pipeline ====================

    def _extract_data(self, text: str) -> AutoGraphSchema:
        """Main extraction logic dispatcher.

        Args:
            text: Input text to extract graph from.

        Returns:
            Extracted and validated graph.
        """
        if self.extraction_mode == "one_stage":
            raw_graph = self._extract_one_stage(text)
        elif self.extraction_mode == "two_stage":
            raw_graph = self._extract_two_stage(text)
        else:
            raise ValueError(f"Invalid extraction_mode: {self.extraction_mode}")

        # Validate and repair graph consistency
        return self._validate_and_repair(raw_graph)

    def _extract_one_stage(self, text: str) -> AutoGraphSchema:
        """Extract nodes and edges simultaneously using single LLM call.

        Args:
            text: Input text.

        Returns:
            Raw extracted graph (may contain inconsistencies).
        """
        prompt_template = ChatPromptTemplate.from_template(
            f"{self.prompt}{{chunk_text}}"
        )
        llm_chain = prompt_template | self.llm_client.with_structured_output(
            self.graph_schema
        )

        # Extract from single chunk or multiple chunks
        if len(text) <= self.chunk_size:
            graph = llm_chain.invoke({"chunk_text": text})
            graph_list = [graph]
        else:
            chunks = self.text_splitter.split_text(text)
            inputs = [{"chunk_text": chunk} for chunk in chunks]
            graph_list = llm_chain.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )

        # Merge multiple graphs
        return self.merge_batch_data(graph_list)

    def _extract_two_stage(self, text: str) -> AutoGraphSchema:
        """Extract nodes first, then edges with node context.

        Args:
            text: Input text.

        Returns:
            Extracted graph with validated consistency.
        """
        # Stage 1: Extract nodes
        nodes = self._extract_nodes(text)

        # Stage 2: Extract edges with node context
        edges = self._extract_edges(text, nodes)

        return self.graph_schema(nodes=nodes, edges=edges)

    def _extract_nodes(self, text: str) -> List[NodeItem]:
        """Extract only nodes from text.

        Args:
            text: Input text.

        Returns:
            List of extracted nodes.
        """
        # Create a temporary schema containing only nodes
        node_list_schema = create_model(
            "NodeList",
            nodes=(List[self.node_schema], Field(default_factory=list))
        )

        prompt_template = ChatPromptTemplate.from_template(
            "Extract all entities/nodes from the following text:\n\n{chunk_text}"
        )
        llm_chain = prompt_template | self.llm_client.with_structured_output(node_list_schema)

        if len(text) <= self.chunk_size:
            result = llm_chain.invoke({"chunk_text": text})
            node_lists = [result.nodes]
        else:
            chunks = self.text_splitter.split_text(text)
            inputs = [{"chunk_text": chunk} for chunk in chunks]
            results = llm_chain.batch(inputs, config={"max_concurrency": self.max_workers})
            node_lists = [r.nodes for r in results]

        # Merge nodes from all chunks
        all_nodes = []
        for node_list in node_lists:
            all_nodes.extend(node_list)

        # Deduplicate using temporary OMem (Reuse self.node_merger)
        temp_mem = OMem(
            memory_schema=self.node_schema,
            key_extractor=self.node_key_extractor,
            llm_client=self.llm_client,
            embedder=self.embedder,
            strategy_or_merger=self.node_merger,
            verbose=False,
        )
        temp_mem.add(all_nodes)
        return temp_mem.items

    def _extract_edges(self, text: str, nodes: List[NodeItem]) -> List[EdgeItem]:
        """Extract edges given node context.

        Args:
            text: Input text.
            nodes: List of known nodes to constrain edge extraction.

        Returns:
            List of extracted edges.
        """
        # Format node context
        node_keys = [self.node_key_extractor(n) for n in nodes]
        node_context = "Known entities: " + ", ".join(node_keys)

        # Create edge list schema
        edge_list_schema = create_model(
            "EdgeList",
            edges=(List[self.edge_schema], Field(default_factory=list))
        )

        prompt_template = ChatPromptTemplate.from_template(
            f"Extract relationships/edges from the text.\n{node_context}\n"
            "CONSTRAINT: Only extract edges between the entities listed above.\n\n"
            "Text:\n{{chunk_text}}"
        )
        llm_chain = prompt_template | self.llm_client.with_structured_output(edge_list_schema)

        if len(text) <= self.chunk_size:
            result = llm_chain.invoke({"chunk_text": text})
            edge_lists = [result.edges]
        else:
            chunks = self.text_splitter.split_text(text)
            inputs = [{"chunk_text": chunk} for chunk in chunks]
            results = llm_chain.batch(inputs, config={"max_concurrency": self.max_workers})
            edge_lists = [r.edges for r in results]

        # Merge edges
        all_edges = []
        for edge_list in edge_lists:
            all_edges.extend(edge_list)

        # Deduplicate (Reuse self.edge_merger)
        temp_mem = OMem(
            memory_schema=self.edge_schema,
            key_extractor=self.edge_key_extractor,
            llm_client=self.llm_client,
            embedder=self.embedder,
            strategy_or_merger=self.edge_merger,
            verbose=False,
        )
        temp_mem.add(all_edges)
        return temp_mem.items

    def _validate_and_repair(self, graph: AutoGraphSchema) -> AutoGraphSchema:
        """Validate graph consistency and repair dangling edges.

        Args:
            graph: Raw graph that may contain dangling edges.

        Returns:
            Validated and repaired graph.
        """
        valid_nodes = graph.nodes
        valid_node_keys = {self.node_key_extractor(n) for n in valid_nodes}

        refined_edges = []
        ghost_nodes = []

        for edge in graph.edges:
            src_key, dst_key = self.edge_to_nodes_extractor(edge)

            # Check if both endpoints exist
            src_exists = src_key in valid_node_keys
            dst_exists = dst_key in valid_node_keys

            if src_exists and dst_exists:
                refined_edges.append(edge)
            elif self.repair_strategy == "create_ghost":
                # Create ghost nodes for missing endpoints
                if not src_exists and src_key not in [self.node_key_extractor(g) for g in ghost_nodes]:
                    ghost_node = self._create_ghost_node(src_key)
                    ghost_nodes.append(ghost_node)
                    valid_node_keys.add(src_key)

                if not dst_exists and dst_key not in [self.node_key_extractor(g) for g in ghost_nodes]:
                    ghost_node = self._create_ghost_node(dst_key)
                    ghost_nodes.append(ghost_node)
                    valid_node_keys.add(dst_key)

                refined_edges.append(edge)
            else:  # repair_strategy == "drop"
                logger.warning(
                    f"Dropping dangling edge: {src_key} -> {dst_key} "
                    f"(src_exists={src_exists}, dst_exists={dst_exists})"
                )

        # Combine original nodes with ghost nodes
        all_nodes = valid_nodes + ghost_nodes

        return self.graph_schema(nodes=all_nodes, edges=refined_edges)

    def _create_ghost_node(self, node_key: str) -> NodeItem:
        """Create a minimal ghost node with only the key field populated.

        Args:
            node_key: The key value for the ghost node.

        Returns:
            Minimal node instance.
        """
        # Attempt to create minimal node with only required fields
        node_dict = {}
        for field_name, field_info in self.node_schema.model_fields.items():
            if field_info.is_required():
                # Try to populate with key if field name matches common patterns
                if field_name in ['id', 'name', 'key', 'entity', 'node_id']:
                    node_dict[field_name] = node_key
                else:
                    # Use default or empty value
                    node_dict[field_name] = ""
        
        return self.node_schema(**node_dict)

    # ==================== Merge Logic ====================

    def merge_batch_data(self, data_list: List[AutoGraphSchema]) -> AutoGraphSchema:
        """Merge multiple graphs into one.

        Args:
            data_list: List of graphs to merge.

        Returns:
            Merged graph.
        """
        if not data_list:
            return self.graph_schema()

        if len(data_list) == 1:
            return data_list[0]

        # Collect all nodes and edges
        all_nodes = []
        all_edges = []
        for graph in data_list:
            all_nodes.extend(graph.nodes)
            all_edges.extend(graph.edges)

        # Deduplicate using temporary OMem instances (Reuse mergers)
        temp_node_mem = OMem(
            memory_schema=self.node_schema,
            key_extractor=self.node_key_extractor,
            llm_client=self.llm_client,
            embedder=self.embedder,
            strategy_or_merger=self.node_merger,
            verbose=False,
        )
        temp_node_mem.add(all_nodes)

        temp_edge_mem = OMem(
            memory_schema=self.edge_schema,
            key_extractor=self.edge_key_extractor,
            llm_client=self.llm_client,
            embedder=self.embedder,
            strategy_or_merger=self.edge_merger,
            verbose=False,
        )
        temp_edge_mem.add(all_edges)

        return self.graph_schema(nodes=temp_node_mem.items, edges=temp_edge_mem.items)

    # ==================== Indexing & Search ====================

    def build_index(self, index_nodes: bool = True, index_edges: bool = False):
        """Build vector index for graph search.

        Args:
            index_nodes: Whether to index nodes (default: True).
            index_edges: Whether to index edges (default: False).
        """
        if self.empty():
            return

        # Typically we index nodes; edges are optional
        if index_nodes:
            self._node_memory.build_index()
        
        if index_edges:
            self._edge_memory.build_index()

    def search(self, query: str, top_k: int = 3, search_type: str = "nodes") -> List[Any]:
        """Search the graph using semantic similarity.

        Args:
            query: Search query.
            top_k: Number of results.
            search_type: "nodes" or "edges".

        Returns:
            List of relevant items.
        """
        if search_type == "nodes":
            return self._node_memory.retrieve(query=query, top_k=top_k)
        elif search_type == "edges":
            return self._edge_memory.retrieve(query=query, top_k=top_k)
        else:
            raise ValueError(f"Invalid search_type: {search_type}")

    # ==================== Serialization ====================

    def dump_index(self, folder_path: str | Path) -> None:
        """Save indices to disk."""
        folder = Path(folder_path)
        folder.mkdir(parents=True, exist_ok=True)
        
        # Save node index
        node_index_path = folder / "node_index"
        node_index_path.mkdir(exist_ok=True)
        try:
            self._node_memory.save_to_disk(str(node_index_path))
        except Exception as e:
            logger.warning(f"Failed to save node index: {e}")

        # Save edge index
        edge_index_path = folder / "edge_index"
        edge_index_path.mkdir(exist_ok=True)
        try:
            self._edge_memory.save_to_disk(str(edge_index_path))
        except Exception as e:
            logger.warning(f"Failed to save edge index: {e}")

    def load_index(self, folder_path: str | Path) -> None:
        """Load indices from disk."""
        folder = Path(folder_path)
        
        # Load node index
        node_index_path = folder / "node_index"
        if node_index_path.exists():
            try:
                self._node_memory.load_from_disk(str(node_index_path))
            except Exception as e:
                logger.warning(f"Failed to load node index: {e}")

        # Load edge index
        edge_index_path = folder / "edge_index"
        if edge_index_path.exists():
            try:
                self._edge_memory.load_from_disk(str(edge_index_path))
            except Exception as e:
                logger.warning(f"Failed to load edge index: {e}")
