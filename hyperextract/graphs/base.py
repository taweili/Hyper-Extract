"""Graph Knowledge Pattern - extracts knowledge graphs with nodes and edges from text.

Provides automatic deduplication for both nodes and edges using OMem.
Supports single-stage and two-stage extraction strategies with consistency validation.
"""

from typing import (
    Any,
    List,
    Type,
    Tuple,
    Callable,
    TypeVar,
    Generic,
    TYPE_CHECKING,
)
from pathlib import Path
from pydantic import BaseModel, Field, create_model
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from ontomem import OMem
from ontomem.merger import MergeStrategy, create_merger, BaseMerger

from ..core.base import BaseAutoType
from ..utils.logging import logger


Node = TypeVar("Node", bound=BaseModel)
Edge = TypeVar("Edge", bound=BaseModel)


class AutoGraphSchema(BaseModel, Generic[Node, Edge]):
    """Generic schema container for graph-based knowledge patterns."""

    nodes: List[Node] = Field(default_factory=list, description="Graph nodes/entities")
    edges: List[Edge] = Field(
        default_factory=list, description="Graph edges/relationships"
    )


class NodeListSchema(BaseModel, Generic[Node]):
    """Intermediate schema for batch node extraction."""

    items: List[Node] = Field(
        default_factory=list,
        description="List of identified entities or nodes found in the text.",
    )


class EdgeListSchema(BaseModel, Generic[Edge]):
    """Intermediate schema for batch edge extraction."""

    items: List[Edge] = Field(
        default_factory=list,
        description="List of identified relationships or edges found in the text.",
    )


class AutoGraph(BaseAutoType[AutoGraphSchema[Node, Edge]], Generic[Node, Edge]):
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
        ...     nodes_in_edge_extractor=lambda x: (x.source, x.target),
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     extraction_mode="two_stage"
        ... )
    """

    if TYPE_CHECKING:
        graph_schema: Type[AutoGraphSchema[Node, Edge]]

    def __init__(
        self,
        node_schema: Type[Node],
        edge_schema: Type[Edge],
        node_key_extractor: Callable[[Node], str],
        edge_key_extractor: Callable[[Edge], str],
        nodes_in_edge_extractor: Callable[[Edge], Tuple[str, str]],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",
        node_strategy_or_merger: MergeStrategy
        | BaseMerger = MergeStrategy.LLM.BALANCED,
        edge_strategy_or_merger: MergeStrategy
        | BaseMerger = MergeStrategy.LLM.BALANCED,
        prompt: str = "",
        prompt_for_node_extraction: str = "",
        prompt_for_edge_extraction: str = "",
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
        max_workers: int = 10,
        show_progress: bool = True,
        **kwargs: Any,
    ):
        """Initialize AutoGraph with node/edge schemas and configuration.

        Args:
            node_schema: Pydantic BaseModel for nodes/entities.
            edge_schema: Pydantic BaseModel for edges/relationships.
            node_key_extractor: Function to extract unique key from node (e.g., lambda x: x.id).
            edge_key_extractor: Function to extract unique key from edge (e.g., lambda x: f"{x.src}-{x.rel}-{x.dst}").
            nodes_in_edge_extractor: Function to extract (source_key, target_key) node keys from an edge for validation.
            llm_client: Language model client for extraction.
            embedder: Embedding model for vector indexing.
            extraction_mode: "one_stage" (extract nodes+edges together) or "two_stage" (nodes first, then edges).
            node_strategy_or_merger: Merge strategy for duplicate nodes (default: LLM.BALANCED).
            edge_strategy_or_merger: Merge strategy for duplicate edges (default: LLM.BALANCED).
            prompt: Custom extraction prompt for one-stage mode.
            prompt_for_node_extraction: Custom extraction prompt for two-stage node extraction.
            prompt_for_edge_extraction: Custom extraction prompt for two-stage edge extraction.
            chunk_size: Maximum characters per chunk.
            chunk_overlap: Overlapping characters between chunks.
            max_workers: Maximum concurrent extraction tasks.
            show_progress: Whether to log progress.
            **kwargs: Additional arguments passed to create_merger() when strategy_or_merger is
                      a MergeStrategy enum. Ignored if strategy_or_merger is a BaseMerger instance.
        """
        # Store schemas and extractors
        self.node_schema = node_schema
        self.edge_schema = edge_schema
        self.node_key_extractor = node_key_extractor
        self.edge_key_extractor = edge_key_extractor
        self.nodes_in_edge_extractor = nodes_in_edge_extractor
        self.extraction_mode = extraction_mode

        # Initialize prompts (use custom if provided, otherwise use defaults)
        self.node_prompt = prompt_for_node_extraction or self._default_node_prompt()
        self.edge_prompt = prompt_for_edge_extraction or self._default_edge_prompt()

        # Create dynamic GraphSchema containers
        graph_schema_name = f"{node_schema.__name__}{edge_schema.__name__}Graph"
        self.graph_schema = create_model(
            graph_schema_name,
            nodes=(List[node_schema], Field(default_factory=list)),
            edges=(List[edge_schema], Field(default_factory=list)),
        )

        # Create schema for list extraction (two-stage mode) with 'items' field
        self.node_list_schema = create_model(
            "NodeList",
            items=(
                List[node_schema],
                Field(default_factory=list, description="Extracted nodes"),
            ),
        )
        self.edge_list_schema = create_model(
            "EdgeList",
            items=(
                List[edge_schema],
                Field(default_factory=list, description="Extracted edges"),
            ),
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
                **kwargs,  # Pass additional arguments to create_merger
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
                **kwargs,  # Pass additional arguments to create_merger
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
        """Returns the default prompt for one-stage graph extraction."""
        return self._default_graph_prompt

    def _create_empty_instance(self) -> "AutoGraph[Node, Edge]":
        """Creates a new empty AutoGraph instance with the same configuration as this one.

        Overrides parent method to handle AutoGraph-specific parameters.

        Returns:
            A new empty AutoGraph instance with identical configuration.
        """
        return self.__class__(
            node_schema=self.node_schema,
            edge_schema=self.edge_schema,
            node_key_extractor=self.node_key_extractor,
            edge_key_extractor=self.edge_key_extractor,
            nodes_in_edge_extractor=self.nodes_in_edge_extractor,
            llm_client=self.llm_client,
            embedder=self.embedder,
            extraction_mode=self.extraction_mode,
            node_strategy_or_merger=self.node_merger,
            edge_strategy_or_merger=self.edge_merger,
            prompt=self.prompt,
            prompt_for_node_extraction=self.node_prompt,
            prompt_for_edge_extraction=self.edge_prompt,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            max_workers=self.max_workers,
            show_progress=self.show_progress,
        )

    @property
    def _default_graph_prompt(self) -> str:
        """Default prompt for one-stage graph extraction (nodes + edges together).

        Emphasizes comprehensive extraction and constraint enforcement.
        """
        return (
            "You are an expert knowledge graph extraction assistant. "
            "Extract all entities (nodes) and their relationships (edges) from the following text. "
            "Focus on being comprehensive and capturing the complete knowledge structure.\n\n"
            "CRITICAL CONSTRAINT: Every edge must connect two nodes that are present in the extracted nodes list. "
            "Do not create edges between entities that are not explicitly identified as nodes.\n\n"
            "### Source Text:\n"
        )

    @property
    def _default_node_prompt(self) -> str:
        """Default prompt for two-stage node extraction (Step 1).

        Emphasizes exhaustiveness and precision in entity identification.
        """
        return (
            "You are an expert information extraction assistant specialized in entity/node recognition. "
            "Extract ALL relevant entities, concepts, or nodes from the following text with high precision.\n\n"
            "Focus on:\n"
            "- Being EXHAUSTIVE: capture all entity types mentioned\n"
            "- Being PRECISE: extract exact entity names and descriptions\n"
            "- Clarity: provide clear, concise descriptions for each entity\n\n"
            "Do not attempt to extract relationships at this stage, only identify entities.\n\n"
            "### Source Text:\n"
        )

    @property
    def _default_edge_prompt(self) -> str:
        """Default prompt for two-stage edge extraction (Step 2).

        Emphasizes strict validation: only extract edges where BOTH endpoints exist in provided entities.
        Includes warnings about hallucination prevention.
        """
        return (
            "You are an expert relationship extraction assistant. "
            "Extract relationships (edges) between the provided entities.\n\n"
            "CRITICAL RULES:\n"
            "1. ONLY extract edges connecting entities from the known entity list below\n"
            "2. DO NOT invent or hallucinate new entities that are not listed\n"
            "3. If an entity in the text is not in the known list, DO NOT create edges involving it\n"
            "4. Focus on explicit relationships mentioned in the text\n\n"
        )

    @property
    def data(self) -> AutoGraphSchema[Node, Edge]:
        """Returns the current graph state (nodes and edges).

        Returns:
            AutoGraphSchema containing all nodes and edges.
        """
        return self.graph_schema(
            nodes=self._node_memory.items, edges=self._edge_memory.items
        )

    @property
    def nodes(self) -> List[Node]:
        """Returns the current node collection.

        Returns:
            List of nodes.
        """
        return self._node_memory.items

    @property
    def edges(self) -> List[Edge]:
        """Returns the current edge collection.

        Returns:
            List of edges.
        """
        return self._edge_memory.items

    def empty(self) -> bool:
        """Checks if the graph is empty (no nodes).

        Returns:
            True if node collections are empty, False otherwise.
        """
        return self._node_memory.empty()

    # ==================== State Management Lifecycle Hooks ====================

    def _init_data_state(self) -> None:
        """Initialize or reset graph data structures."""
        self._node_memory.clear()
        self._edge_memory.clear()

    def _init_index_state(self) -> None:
        """Initialize vector index to empty state."""
        self._node_memory.clear_index()
        self._edge_memory.clear_index()

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
            raw_graph = self._extract_data_by_one_stage(text)
        elif self.extraction_mode == "two_stage":
            raw_graph = self._extract_data_by_two_stage(text)
        else:
            raise ValueError(f"Invalid extraction_mode: {self.extraction_mode}")

        # Prune dangling edges to ensure graph consistency
        return self._prune_dangling_edges(raw_graph)

    def _extract_data_by_one_stage(self, text: str) -> AutoGraphSchema:
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

    def _extract_data_by_two_stage(self, text: str) -> AutoGraphSchema:
        """Extract nodes first, then edges with node context (batch processing).

        Process:
        1. Split text into chunks.
        2. Batch extract nodes for all chunks.
        3. Batch extract edges for all chunks (using chunk-specific nodes as context).
        4. Construct partial graphs (tuples of nodes/edges).
        5. Merge all partial graphs into one global graph.

        Args:
            text: Input text.

        Returns:
            Extracted and validated graph.
        """
        # 1. Prepare chunks
        if len(text) <= self.chunk_size:
            chunks = [text]
        else:
            chunks = self.text_splitter.split_text(text)

        # 2. Batch Extract Nodes (returns List[NodeListSchema])
        chunk_node_lists = self._extract_nodes_batch(chunks)

        # 3. Batch Extract Edges (Context-aware, returns List[EdgeListSchema])
        chunk_edge_lists = self._extract_edges_batch(chunks, chunk_node_lists)

        # 4. Construct Partial Graphs (Tuple format for merge optimization)
        partial_graphs = (
            [node_list.items for node_list in chunk_node_lists],
            [edge_list.items for edge_list in chunk_edge_lists],
        )

        # 5. Global Merge (passes tuples to merge_batch_data)
        return self.merge_batch_data(partial_graphs)

    def _extract_nodes_batch(self, chunks: List[str]) -> List[NodeListSchema[Node]]:
        """Batch extract nodes from multiple text chunks.

        Args:
            chunks: List of text chunks.

        Returns:
            List of NodeListSchema objects with extracted nodes.
        """
        prompt_template = ChatPromptTemplate.from_template(
            f"{self.node_prompt}{{chunk_text}}"
        )
        llm_chain = prompt_template | self.llm_client.with_structured_output(
            self.node_list_schema
        )

        inputs = [{"chunk_text": chunk} for chunk in chunks]
        return llm_chain.batch(inputs, config={"max_concurrency": self.max_workers})

    def _extract_edges_batch(
        self, chunks: List[str], node_lists: List[NodeListSchema[Node]]
    ) -> List[EdgeListSchema[Edge]]:
        """Batch extract edges using corresponding node lists as context.

        Args:
            chunks: List of text chunks.
            node_lists: List of NodeListSchema objects (one per chunk).

        Returns:
            List of EdgeListSchema objects with extracted edges.
        """
        inputs = []
        for chunk, node_list in zip(chunks, node_lists):
            nodes = node_list.items if node_list else []
            if not nodes:
                node_context = "No specific entities identified in this chunk."
            else:
                node_keys = [self.node_key_extractor(n) for n in nodes]
                node_context = "Known entities: " + ", ".join(node_keys)

            inputs.append({"chunk_text": chunk, "node_context": node_context})

        prompt_template = ChatPromptTemplate.from_template(
            f"{self.edge_prompt}{{node_context}}\n\n### Text Chunk:\n{{chunk_text}}"
        )
        llm_chain = prompt_template | self.llm_client.with_structured_output(
            self.edge_list_schema
        )

        return llm_chain.batch(inputs, config={"max_concurrency": self.max_workers})

    def _prune_dangling_edges(self, graph: AutoGraphSchema) -> AutoGraphSchema:
        """Prune edges that connect to non-existent nodes (Consistency Check).

        Ensures graph consistency by removing any edges where either endpoint
        (source or target) does not exist in the node list.

        Args:
            graph: Raw graph that may contain dangling edges.

        Returns:
            Graph with only valid edges (endpoints must strictly exist in nodes).
        """
        valid_nodes = graph.nodes
        valid_node_keys = {self.node_key_extractor(n) for n in valid_nodes}

        refined_edges = []
        dropped_count = 0

        for edge in graph.edges:
            src_key, dst_key = self.nodes_in_edge_extractor(edge)

            # Check if both endpoints exist
            src_exists = src_key in valid_node_keys or src_key in self._node_memory.keys
            dst_exists = dst_key in valid_node_keys or dst_key in self._node_memory.keys

            if src_exists and dst_exists:
                refined_edges.append(edge)
            else:
                dropped_count += 1
                logger.debug(
                    f"Pruning dangling edge: {src_key} -> {dst_key} "
                    f"(src_exists={src_exists}, dst_exists={dst_exists})"
                )

        if dropped_count > 0:
            logger.info(
                f"Pruned {dropped_count} dangling edges to ensure graph consistency."
            )

        return self.graph_schema(nodes=valid_nodes, edges=refined_edges)

    # ==================== Merge Logic ====================

    def merge_batch_data(
        self,
        data_list_or_tuple: List[AutoGraphSchema] | Tuple[List[List[Node]], List[List[Edge]]],
    ) -> AutoGraphSchema:
        """Merge multiple graphs or node/edge tuples into one.

        Supports two input formats:
        - List of AutoGraphSchema objects (standard format)
        - Tuple of (List[List[Node]], List[List[Edge]]) (optimization for batch processing)

        Args:
            data_list_or_tuple: Either a list of AutoGraphSchema objects or a tuple of 
                (nodes_lists, edges_lists) where each list contains items from multiple chunks.

        Returns:
            Merged graph.
        """
        if isinstance(data_list_or_tuple[0], self.graph_schema):
            all_nodes, all_edges = [], []

            for graph in data_list_or_tuple:
                all_nodes.extend(graph.nodes)
                all_edges.extend(graph.edges)

        else:
            assert len(data_list_or_tuple) == 2, (
                "Invalid input format for batch merging"
            )
            nodes_lists, edges_lists = data_list_or_tuple[0], data_list_or_tuple[1]
            assert isinstance(nodes_lists[0][0], self.node_schema), (
                "Invalid node list format for batch merging"
            )
            assert isinstance(edges_lists[0][0], self.edge_schema), (
                "Invalid edge list format for batch merging"
            )

            all_nodes, all_edges = [], []
            for node_list, edge_list in zip(nodes_lists, edges_lists):
                all_nodes.extend(node_list)
                all_edges.extend(edge_list)

        merged_nodes = self.node_merger.merge(all_nodes) if all_nodes else []
        merged_edges = self.edge_merger.merge(all_edges) if all_edges else []
        return self.graph_schema(nodes=merged_nodes, edges=merged_edges)

    # ==================== Indexing & Search ====================

    def build_index(self, index_nodes: bool = True, index_edges: bool = False):
        """Build vector index for graph search.

        Args:
            index_nodes: Whether to index nodes (default: True).
            index_edges: Whether to index edges (default: False).
        """
        if index_nodes:
            self.build_node_index()

        if index_edges:
            self.build_edge_index()

    def build_node_index(self) -> None:
        """Build vector index specifically for nodes."""
        if not self.empty():
            self._node_memory.build_index()

    def build_edge_index(self) -> None:
        """Build vector index specifically for edges."""
        if not self.empty():
            self._edge_memory.build_index()

    def search(
        self,
        query: str,
        top_k: int = 3,
        search_nodes: bool = True,
        search_edges: bool = False,
    ) -> List[Node] | List[Edge] | Tuple[List[Node], List[Edge]]:
        """Unified graph search interface.

        Supports searching nodes only, edges only, or both simultaneously.
        When searching both, returns a tuple of (nodes_results, edges_results).
        When searching one type, returns a flat list.

        Args:
            query: Search query string.
            top_k: Number of results to return per type (default: 3).
            search_nodes: Whether to search nodes (default: True).
            search_edges: Whether to search edges (default: False).

        Returns:
            - List[Node] if only search_nodes is True.
            - List[Edge] if only search_edges is True.
            - Tuple[List[Node], List[Edge]] if both search_nodes and search_edges are True.

        Raises:
            ValueError: If neither search_nodes nor search_edges is True.
        """
        if not search_nodes and not search_edges:
            raise ValueError(
                "At least one of search_nodes or search_edges must be True."
            )

        if search_nodes and search_edges:
            if not self._node_memory.has_index():
                raise ValueError("Node index not built. Call build_index() first.")
            if not self._edge_memory.has_index():
                raise ValueError("Edge index not built. Call build_index() first.")
            nodes = self.search_nodes(query, top_k)
            edges = self.search_edges(query, top_k)
            return (nodes, edges)

        if search_nodes:
            if not self._node_memory.has_index():
                raise ValueError("Node index not built. Call build_index() first.")
            nodes = self.search_nodes(query, top_k)
            return nodes

        if search_edges:
            if not self._edge_memory.has_index():
                raise ValueError("Edge index not built. Call build_index() first.")
            edges = self.search_edges(query, top_k)
            return edges

    def search_nodes(self, query: str, top_k: int = 3) -> List[Node]:
        """Semantic search for nodes/entities only.

        Args:
            query: Search query string.
            top_k: Number of results to return (default: 3).

        Returns:
            List of matching nodes using semantic similarity.
        """
        return self._node_memory.search(query=query, top_k=top_k)

    def search_edges(self, query: str, top_k: int = 3) -> List[Edge]:
        """Semantic search for edges/relationships only.

        Args:
            query: Search query string.
            top_k: Number of results to return (default: 3).

        Returns:
            List of matching edges using semantic similarity.
        """
        return self._edge_memory.search(query=query, top_k=top_k)

    # ==================== Serialization ====================

    def dump_index(self, folder_path: str | Path) -> None:
        """Save indices to disk."""
        folder = Path(folder_path)
        folder.mkdir(parents=True, exist_ok=True)

        # Save node index
        node_index_path = folder / "node_index"
        node_index_path.mkdir(exist_ok=True)
        try:
            self._node_memory.dump_index(str(node_index_path))
        except Exception as e:
            logger.warning(f"Failed to save node index: {e}")

        # Save edge index
        edge_index_path = folder / "edge_index"
        edge_index_path.mkdir(exist_ok=True)
        try:
            self._edge_memory.dump_index(str(edge_index_path))
        except Exception as e:
            logger.warning(f"Failed to save edge index: {e}")

    def load_index(self, folder_path: str | Path) -> None:
        """Load indices from disk."""
        folder = Path(folder_path)

        # Load node index
        node_index_path = folder / "node_index"
        if node_index_path.exists():
            try:
                self._node_memory.load_index(str(node_index_path))
            except Exception as e:
                logger.warning(f"Failed to load node index: {e}")

        # Load edge index
        edge_index_path = folder / "edge_index"
        if edge_index_path.exists():
            try:
                self._edge_memory.load_index(str(edge_index_path))
            except Exception as e:
                logger.warning(f"Failed to load edge index: {e}")
