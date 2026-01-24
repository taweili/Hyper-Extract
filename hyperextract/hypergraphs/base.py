"""Hypergraph Knowledge Pattern - extracts hypergraphs where edges connect multiple nodes.

Key Difference from AutoGraph:
- Edges are "Hyperedges" that connect arbitrary numbers of nodes (not just source/target).
- Consistency validation checks if *ALL* participants in a hyperedge exist in the node registry.
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
Edge = TypeVar("Edge", bound=BaseModel)  # Represents a Hyperedge


# ============================================================================
# Default Extraction Prompts
# ============================================================================

DEFAULT_HYPERGRAPH_PROMPT = """You are an expert hypergraph knowledge extraction assistant. 
Extract all entities (nodes) and their complex relationships (hyperedges) from the following text.

CRITICAL RULES:
1. Extract comprehensive Nodes (entities).
2. Extract Hyperedges that connect multiple (2 or more) nodes simultaneously.
3. STRUCTURAL CONSISTENCY: Every participant in a hyperedge MUST be present in the extracted Nodes list.
4. Do not create hyperedges involving entities that are not in the Nodes list.
5. A Hyperedge represents a Grouping, Event, or Complex Relation involving the listed participants.

### Source Text:
"""

DEFAULT_NODE_PROMPT = """Extract all distinct entities from the text. 
Entities will serve as participants in complex events later.

### Source Text:
"""

DEFAULT_EDGE_PROMPT = """You are an expert hypergraph extraction assistant. 
Extract complex relationships (hyperedges) that involve MULTIPLE entities simultaneously.

CRITICAL RULES:
1. A hyperedge can connect 2, 3, or more entities (e.g., a meeting with multiple people).
2. Identify ALL participants for each relationship.
3. ONLY use entities from the provided 'Known Entities' list.
4. If an entity is not in the list, exclude it from the hyperedge.

"""


class AutoHypergraphSchema(BaseModel, Generic[Node, Edge]):
    """Generic schema container for hypergraph data."""

    nodes: List[Node] = Field(default_factory=list, description="Graph nodes/entities")
    edges: List[Edge] = Field(
        default_factory=list, description="Hyperedges connecting multiple entities"
    )


class NodeListSchema(BaseModel, Generic[Node]):
    """Intermediate schema for batch node extraction."""

    items: List[Node] = Field(
        default_factory=list,
        description="List of identified entities or nodes found in the text.",
    )


class EdgeListSchema(BaseModel, Generic[Edge]):
    """Intermediate schema for batch hyperedge extraction."""

    items: List[Edge] = Field(
        default_factory=list,
        description="List of identified hyperedges found in the text.",
    )


class AutoHypergraph(
    BaseAutoType[AutoHypergraphSchema[Node, Edge]], Generic[Node, Edge]
):
    """AutoHypergraph - extracts complex relationships involving multiple entities.

    Suitable for:
    - Events with multiple participants (e.g., meetings, transactions)
    - Group memberships
    - Complex dependencies

    The `nodes_in_edge_extractor` must return a Tuple of ALL node keys involved in the edge.
    Validation uses 'Strict Mode': checks if ALL nodes in that tuple exist.

    Example:
        >>> class Person(BaseModel):
        ...     name: str
        ...
        >>> class Event(BaseModel):
        ...     label: str  # e.g., "meeting", "collaboration"
        ...     participants: List[str]  # IDs of people involved
        ...
        >>> hypergraph = AutoHypergraph(
        ...     node_schema=Person,
        ...     edge_schema=Event,
        ...     node_key_extractor=lambda x: x.name,
        ...     # CRITICAL: Sort participants to ensure {A, B} and {B, A} map to same key
        ...     edge_key_extractor=lambda x: f"{x.label}_{sorted(x.participants)}",
        ...     nodes_in_edge_extractor=lambda x: tuple(x.participants),
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     extraction_mode="two_stage"
        ... )
    """

    if TYPE_CHECKING:
        graph_schema: Type[AutoHypergraphSchema[Node, Edge]]

    def __init__(
        self,
        node_schema: Type[Node],
        edge_schema: Type[Edge],
        node_key_extractor: Callable[[Node], str],
        edge_key_extractor: Callable[[Edge], str],
        # Returns a tuple of ALL node keys involved in this hyperedge
        nodes_in_edge_extractor: Callable[[Edge], Tuple[str, ...]],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",  # Recommended for complex relations
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
        verbose: bool = True,
        node_fields_for_index: List[str] | None = None,
        edge_fields_for_index: List[str] | None = None,
        **kwargs: Any,
    ):
        """Initialize AutoHypergraph with node/edge schemas and configuration.

        Args:
            node_schema: Pydantic BaseModel for nodes/entities.
            edge_schema: Pydantic BaseModel for hyperedges/relationships.
            node_key_extractor: Function to extract unique key from node.
            edge_key_extractor: Function to extract unique key from hyperedge.
                CRITICAL: Since hyperedges are unordered sets of nodes (i.e., {A, B} == {B, A}),
                you MUST sort the participating node keys in this function to ensure consistent
                deduplication. For example:
                    lambda x: f"{x.relation_type}_{sorted(x.participants)}"
                Without sorting, two hyperedges with the same nodes in different order will
                be treated as different edges, breaking the deduplication mechanism.
            nodes_in_edge_extractor: Function to extract ALL node keys from a hyperedge
                as a tuple (e.g., lambda x: tuple(x.participants)).
            llm_client: Language model client for extraction.
            embedder: Embedding model for vector indexing.
            extraction_mode: "two_stage" (recommended) or "one_stage".
            node_strategy_or_merger: Merge strategy for duplicate nodes.
            edge_strategy_or_merger: Merge strategy for duplicate hyperedges.
            prompt: Custom extraction prompt for one-stage mode.
            prompt_for_node_extraction: Custom extraction prompt for node extraction.
            prompt_for_edge_extraction: Custom extraction prompt for hyperedge extraction.
            chunk_size: Maximum characters per chunk.
            chunk_overlap: Overlapping characters between chunks.
            max_workers: Maximum concurrent extraction tasks.
            verbose: Whether to display detailed execution logs and progress information.
            node_fields_for_index: Optional list of field names in node_schema to include in vector index.
                                   If None, all text fields are indexed by default.
                                   Example: ['name', 'properties'] (only index these node fields)
            edge_fields_for_index: Optional list of field names in edge_schema to include in vector index.
                                   If None, all text fields are indexed by default.
                                   Example: ['summary', 'type'] (only index these edge fields)
            **kwargs: Additional arguments for merger creation.
        """
        # Store schemas and extractors
        self.node_schema = node_schema
        self.edge_schema = edge_schema
        self.node_key_extractor = node_key_extractor
        self.edge_key_extractor = edge_key_extractor
        self.nodes_in_edge_extractor = nodes_in_edge_extractor
        self.extraction_mode = extraction_mode
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_workers = max_workers
        self.verbose = verbose
        self.node_fields_for_index = node_fields_for_index
        self.edge_fields_for_index = edge_fields_for_index

        self.max_workers = max_workers
        self.verbose = verbose

        # Initialize prompts
        self.node_prompt = prompt_for_node_extraction or DEFAULT_NODE_PROMPT
        self.edge_prompt = prompt_for_edge_extraction or DEFAULT_EDGE_PROMPT

        # Create dynamic HypergraphSchema
        graph_schema_name = f"{node_schema.__name__}{edge_schema.__name__}Hypergraph"
        self.graph_schema = create_model(
            graph_schema_name,
            nodes=(List[node_schema], Field(default_factory=list)),
            edges=(List[edge_schema], Field(default_factory=list)),
        )

        # Helper Schemas for Batch Extraction
        self.node_list_schema = create_model(
            f"{node_schema.__name__}List",
            items=(List[node_schema], Field(default_factory=list)),
        )
        self.edge_list_schema = create_model(
            f"{edge_schema.__name__}List",
            items=(List[edge_schema], Field(default_factory=list)),
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
                **kwargs,
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
                **kwargs,
            )

        # Initialize OMem instances
        self._node_memory = OMem(
            memory_schema=node_schema,
            key_extractor=node_key_extractor,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=self.node_merger,
            verbose=verbose,
            fields_for_index=node_fields_for_index,  # Pass node field selection to OMem
        )

        self._edge_memory = OMem(
            memory_schema=edge_schema,
            key_extractor=edge_key_extractor,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=self.edge_merger,
            verbose=verbose,
            fields_for_index=edge_fields_for_index,  # Pass edge field selection to OMem
        )

        # Initialize Base Class
        super().__init__(
            data_schema=self.graph_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt or DEFAULT_HYPERGRAPH_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )

    # ==================== Prompts ====================

    def _default_prompt(self) -> str:
        """Returns the default prompt for one-stage hypergraph extraction.

        This is the primary prompt used when extraction_mode is 'one_stage'.
        """
        return DEFAULT_HYPERGRAPH_PROMPT

    def _create_empty_instance(self) -> "AutoHypergraph[Node, Edge]":
        """Creates a new empty AutoHypergraph instance with the same configuration.

        Overrides parent method to handle AutoHypergraph-specific parameters.

        Returns:
            A new empty AutoHypergraph instance with identical configuration.
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
            verbose=self.verbose,
            node_fields_for_index=self.node_fields_for_index,  # Persist node index field configuration
            edge_fields_for_index=self.edge_fields_for_index,  # Persist edge index field configuration
        )

    # ==================== State Management Lifecycle Hooks ====================

    def _init_data_state(self) -> None:
        """Initialize or reset hypergraph data structures."""
        self._node_memory.clear()
        self._edge_memory.clear()

    def _init_index_state(self) -> None:
        """Initialize vector index to empty state."""
        self._node_memory.clear_index()
        self._edge_memory.clear_index()

    def _set_data_state(self, data: AutoHypergraphSchema) -> None:
        """Replace hypergraph data with new data (full reset)."""
        self._node_memory.clear()
        self._edge_memory.clear()

        if data.nodes:
            self._node_memory.add(data.nodes)
        if data.edges:
            self._edge_memory.add(data.edges)

        self.clear_index()

    def _update_data_state(self, incoming_data: AutoHypergraphSchema) -> None:
        """Merge incoming hypergraph data into current state."""
        if self.empty():
            self._set_data_state(incoming_data)
        else:
            if incoming_data.nodes:
                self._node_memory.add(incoming_data.nodes)
            if incoming_data.edges:
                self._edge_memory.add(incoming_data.edges)
            self.clear_index()

    @property
    def data(self) -> AutoHypergraphSchema:
        """Returns the current hypergraph state."""
        return self.graph_schema(
            nodes=self._node_memory.items, edges=self._edge_memory.items
        )

    @property
    def nodes(self) -> List[Node]:
        """Returns the current node collection."""
        return self._node_memory.items

    @property
    def edges(self) -> List[Edge]:
        """Returns the current hyperedge collection."""
        return self._edge_memory.items

    def empty(self) -> bool:
        """Checks if the hypergraph is empty."""
        return self._node_memory.empty()

    # ==================== Extraction Pipeline ====================

    def _extract_data(self, text: str) -> AutoHypergraphSchema:
        """Main extraction logic dispatcher."""
        if self.extraction_mode == "two_stage":
            raw_graph = self._extract_data_by_two_stage(text)
        elif self.extraction_mode == "one_stage":
            raise NotImplementedError(
                "Single-stage extraction not yet supported for AutoHypergraph."
            )
        else:
            raise ValueError(f"Invalid extraction_mode: {self.extraction_mode}")

        # Prune dangling hyperedges to ensure consistency
        return self._prune_dangling_edges(raw_graph)

    def _extract_data_by_two_stage(self, text: str) -> AutoHypergraphSchema:
        """Extract nodes first, then hyperedges with node context (batch processing).

        Process:
        1. Split text into chunks.
        2. Batch extract nodes for all chunks.
        3. Batch extract hyperedges for all chunks (using chunk-specific nodes as context).
        4. Merge all partial results into one global hypergraph.
        """
        # 1. Prepare chunks
        if len(text) <= self.chunk_size:
            chunks = [text]
        else:
            chunks = self.text_splitter.split_text(text)

        if self.verbose:
            logger.info(f"Extracting from {len(chunks)} chunks...")

        # 2. Batch Extract Nodes
        chunk_node_lists = self._extract_nodes_batch(chunks)

        # 3. Batch Extract Hyperedges (Context-aware)
        chunk_edge_lists = self._extract_edges_batch(chunks, chunk_node_lists)

        # 4. Construct Partial Graphs (Tuple format for merge optimization)
        partial_hypergraphs = (
            [node_list.items for node_list in chunk_node_lists],
            [edge_list.items for edge_list in chunk_edge_lists],
        )

        # 5. Global Merge
        return self.merge_batch_data(partial_hypergraphs)

    def _extract_nodes_batch(self, chunks: List[str]) -> List[NodeListSchema[Node]]:
        """Batch extract nodes from multiple text chunks."""
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
        """Batch extract hyperedges using corresponding node lists as context."""
        inputs = []
        for chunk, node_list in zip(chunks, node_lists):
            nodes = node_list.items if node_list else []
            if not nodes:
                node_context = "No entities identified in this chunk."
            else:
                node_keys = [f"- {self.node_key_extractor(n)}" for n in nodes]
                node_context = "Allowed Entities:\n" + "\n".join(node_keys)

            inputs.append({"chunk_text": chunk, "node_context": node_context})

        prompt_template = ChatPromptTemplate.from_template(
            f"{self.edge_prompt}{{node_context}}\n\n### Text Chunk:\n{{chunk_text}}"
        )
        llm_chain = prompt_template | self.llm_client.with_structured_output(
            self.edge_list_schema
        )

        return llm_chain.batch(inputs, config={"max_concurrency": self.max_workers})

    def _prune_dangling_edges(
        self, graph: AutoHypergraphSchema
    ) -> AutoHypergraphSchema:
        """Prune hyperedges where ANY participating node does not exist (Strict Consistency).

        Args:
            graph: Raw hypergraph that may contain dangling hyperedges.

        Returns:
            Hypergraph with only valid hyperedges (ALL participants must exist in nodes).
        """
        valid_nodes = graph.nodes
        valid_node_keys = {self.node_key_extractor(n) for n in valid_nodes}

        # Also check long-term memory
        if self._node_memory:
            valid_node_keys.update(self._node_memory.keys)

        refined_edges = []
        dropped_count = 0

        for edge in graph.edges:
            # Get tuple of all participant node keys
            participant_keys = self.nodes_in_edge_extractor(edge)

            # Strict mode: ALL participants must exist
            is_valid = True
            for pk in participant_keys:
                if pk not in valid_node_keys:
                    is_valid = False
                    break

            # Keep edge only if all participants exist and there's at least one participant
            if is_valid and len(participant_keys) > 0:
                refined_edges.append(edge)
            else:
                dropped_count += 1
                logger.debug(
                    f"Pruning dangling hyperedge with participants: {participant_keys}"
                )

        if dropped_count > 0:
            logger.info(
                f"Pruned {dropped_count} dangling hyperedges to ensure consistency."
            )

        return self.graph_schema(nodes=valid_nodes, edges=refined_edges)

    # ==================== Merge Logic ====================

    def merge_batch_data(
        self,
        data_list_or_tuple: List[AutoHypergraphSchema]
        | Tuple[List[List[Node]], List[List[Edge]]],
    ) -> AutoHypergraphSchema:
        """Merge multiple hypergraphs or node/edge tuples into one.

        Supports two input formats:
        - List of AutoHypergraphSchema objects (standard format)
        - Tuple of (List[List[Node]], List[List[Edge]]) (optimization for batch processing)

        Args:
            data_list_or_tuple: Either a list of AutoHypergraphSchema objects or a tuple of
                (nodes_lists, edges_lists) where each list contains items from multiple chunks.

        Returns:
            Merged hypergraph.
        """
        if isinstance(data_list_or_tuple, list) and isinstance(
            data_list_or_tuple[0], self.graph_schema
        ):
            # Format: List of AutoHypergraphSchema
            all_nodes, all_edges = [], []
            for graph in data_list_or_tuple:
                all_nodes.extend(graph.nodes)
                all_edges.extend(graph.edges)

        else:
            # Format: Tuple of (nodes_lists, edges_lists)
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
        """Build vector index for hypergraph search.

        Args:
            index_nodes: Whether to index nodes (default: True).
            index_edges: Whether to index hyperedges (default: False).
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
        """Build vector index specifically for hyperedges."""
        if not self.empty():
            self._edge_memory.build_index()

    def search(
        self,
        query: str,
        top_k: int = 3,
        search_nodes: bool = True,
        search_edges: bool = False,
    ) -> List[Node] | List[Edge] | Tuple[List[Node], List[Edge]]:
        """Unified hypergraph search interface.

        Args:
            query: Search query string.
            top_k: Number of results to return per type.
            search_nodes: Whether to search nodes.
            search_edges: Whether to search hyperedges.

        Returns:
            - List[Node] if only search_nodes is True.
            - List[Edge] if only search_edges is True.
            - Tuple[List[Node], List[Edge]] if both are True.
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
            return self.search_nodes(query, top_k)

        if search_edges:
            if not self._edge_memory.has_index():
                raise ValueError("Edge index not built. Call build_index() first.")
            return self.search_edges(query, top_k)

    def search_nodes(self, query: str, top_k: int = 3) -> List[Node]:
        """Semantic search for nodes/entities only."""
        return self._node_memory.search(query=query, top_k=top_k)

    def search_edges(self, query: str, top_k: int = 3) -> List[Edge]:
        """Semantic search for hyperedges/relationships only."""
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
