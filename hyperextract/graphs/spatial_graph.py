"""Generic spatial graph implementation supporting custom schemas with location-aware extraction."""

from typing import Type, Callable, Tuple, Any, List
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.embeddings import Embeddings
from ontomem.merger import MergeStrategy, BaseMerger

from .base import (
    AutoGraph,
    NodeSchema,
    EdgeSchema,
    NodeListSchema,
    EdgeListSchema,
    AutoGraphSchema,
)
from ..utils.logging import logger

# ==============================================================================
# Prompt Definition - Spatial "Sandwich" Injection
# ==============================================================================

# Node Extraction Prompts
DEFAULT_SPATIAL_NODE_ROLE_PREFIX = """
You are a professional spatial entity extraction specialist.
Your task is to extract all important entities (Nodes) from the text, resolving their location attributes accurately.
"""

DEFAULT_SPATIAL_NODE_RULES_SUFFIX = """
# Core Principles
1. **Comprehensiveness**: Extract persons, organizations, facilities, events, and objects.
2. **Location as Attribute**: Extract location/coordinates as fields of the entity, NOT as separate nodes.
3. **Exclude Pure Spatial Markers**: **NEVER** extract abstract directions, coordinates, or pointers (e.g., "here", "nearby", "left side", "34.05N") as independent entity nodes!
   Spatial context is an attribute of the entity itself.

# Spatial Resolution Rules
Current Observation Location/Reference: {observation_location}

1. **Relative Location Resolution**: You MUST resolve relative location expressions based on the Observation Location.
   - "here" / "local" / "this place" -> {observation_location}
   - "nearby" / "adjacent" -> In the vicinity of {observation_location}
   - "north of here" / "south of this place" -> Resolve direction relative to {observation_location}

2. **Explicit Locations**: Keep explicit addresses or coordinates consistent with the source text.

3. **Missing Location**: If no location information is applicable for an entity, leave location fields empty. DO NOT hallucinate locations.

### Source Text:
"""

# Edge Extraction Prompts
DEFAULT_SPATIAL_EDGE_ROLE_PREFIX = """
You are an expert knowledge extraction specialist.
Extract meaningful relationships (edges) between the provided entities.
"""

DEFAULT_SPATIAL_EDGE_RULES_SUFFIX = """
### General Constraints
1. ONLY extract edges connecting entities from the known entity list provided below.
   - Do NOT abbreviate or modify the entity identifiers.
2. DO NOT create edges involving entities that are not listed.
3. Keep the graph structure clean and focused on valid relationships.

"""

# One-Stage Graph Extraction Prompts
DEFAULT_SPATIAL_GRAPH_ROLE_PREFIX = """
You are a professional spatial knowledge graph extraction specialist.
Your task is to extract spatial entities (Nodes) and their relationships (Edges) from the text.
"""

DEFAULT_SPATIAL_GRAPH_RULES_SUFFIX = """
# Core Principles for Nodes
1. Extract persons, organizations, facilities, and objects.
2. **NEVER** extract pure spatial markers (coordinates, "here", directions) as independent nodes. Location is an attribute.
3. Resolve relative locations ("here", "local") based on the Observation Location below.

# Core Principles for Edges
1. Extract explicit relationships between the extracted entities.
2. Ensure edge consistency: only link entities that you have extracted.

# Spatial Reference
Current Observation Location: {observation_location}

### Source Text:
"""


class AutoSpatialGraph(AutoGraph[NodeSchema, EdgeSchema]):
    """
    Generic Spatial Graph Extractor (AutoSpatialGraph).

    A flexible implementation supporting user-defined Node schemas with spatial awareness:
    - **Location Injection**: Observation Location is injected to resolve relative spatial references (e.g., "local", "nearby").
    - **Spatial Attribute Focus**: Prompts enforce treating location as a Node attribute rather than a separate Node.
    - **Spatial Identity**: Nodes are uniquely identified by BOTH Name and Location. The same entity at different locations
      is treated as spatially distinct (e.g., "Dr. Chen @ Airlock" vs "Dr. Chen @ MedBay" are different node identities).
    - **Schema Agnosticism**: Support any user-defined Node and Edge Pydantic models.

    Example:
        >>> from pydantic import BaseModel, Field
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>>
        >>> class SpatialEntity(BaseModel):
        ...     name: str
        ...     entity_type: str
        ...     location: str | None = None
        ...
        >>> class Relation(BaseModel):
        ...     source: str
        ...     target: str
        ...     relation_type: str
        >>>
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>>
        >>> graph = AutoSpatialGraph(
        ...     node_schema=SpatialEntity,
        ...     edge_schema=Relation,
        ...     # Split identity extraction: base name and location
        ...     node_key_extractor=lambda x: x.name,
        ...     location_in_node_extractor=lambda x: x.location,
        ...     edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
        ...     nodes_in_edge_extractor=lambda x: (x.source, x.target),
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     observation_location="New York City, NY",
        ...     extraction_mode="two_stage"
        ... )
    """

    def __init__(
        self,
        node_schema: Type[NodeSchema],
        edge_schema: Type[EdgeSchema],
        node_key_extractor: Callable[[NodeSchema], str],
        location_in_node_extractor: Callable[[NodeSchema], str],
        edge_key_extractor: Callable[[EdgeSchema], str],
        nodes_in_edge_extractor: Callable[[EdgeSchema], Tuple[str, str]],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_location: str | None = None,
        extraction_mode: str = "two_stage",
        node_strategy_or_merger: "MergeStrategy | BaseMerger" = MergeStrategy.LLM.BALANCED,
        edge_strategy_or_merger: "MergeStrategy | BaseMerger" = MergeStrategy.LLM.BALANCED,
        prompt_for_node_extraction: str = "",
        prompt_for_edge_extraction: str = "",
        prompt: str = "",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        node_fields_for_index: List[str] | None = None,
        edge_fields_for_index: List[str] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize AutoSpatialGraph.

        **Required Arguments:**

        Args:
            node_schema: User-defined Node Pydantic model class. Defines the structure of
                        extracted entities. Should include fields for entity attributes and optional
                        location information (e.g., name, type, location, coordinates).
                        Example: class Entity(BaseModel): name: str; location: str | None = None

            edge_schema: User-defined Edge Pydantic model class. Defines the structure of
                        relationships between nodes. Must include fields to specify source and
                        target nodes.
                        Example: class Relation(BaseModel): source: str; target: str; relation_type: str

            node_key_extractor: Callable function to extract the BASE unique identifier from a node,
                               excluding location (e.g., just the name logic).
                               Example: lambda x: x.name

            location_in_node_extractor: Callable function to extract the location string from a node.
                                       Example: lambda x: x.location

            edge_key_extractor: Callable function to extract a unique key/identifier from each edge.
                               Used for edge deduplication and matching.
                               Example: lambda x: f"{x.source}-{x.relation_type}-{x.target}"

            nodes_in_edge_extractor: Function to extract (source_key, target_key) node keys from an edge for validation.

            llm_client: LangChain BaseChatModel instance (e.g., ChatOpenAI, ChatAnthropic).
                       Responsible for extracting nodes and edges from text via LLM calls.

            embedder: LangChain Embeddings instance (e.g., OpenAIEmbeddings, HuggingFaceEmbeddings).
                     Used for semantic similarity matching and vector indexing of nodes and edges.

        **Optional Keyword Arguments:**

        Args:
            observation_location: A string describing the reference location for relative spatial
                                 resolution (e.g., "New York City, NY", "Building A, Room 101",
                                 "37.7749,-122.4194"). Used by the LLM to resolve expressions like
                                 "here", "nearby", "local" to actual locations.
                                 Default: "Unknown Location"

            extraction_mode: Extraction strategy - either "one_stage" or "two_stage".
                            - "one_stage": Extracts nodes and edges simultaneously (faster, less precise).
                            - "two_stage": Extracts nodes first, then edges with node context (more accurate).
                            Default: "two_stage"

            node_strategy_or_merger: Merge strategy for deduplicating nodes (when multiple chunks
                                    have duplicate nodes). Can be a MergeStrategy enum value
                                    (e.g., MergeStrategy.LLM.BALANCED, MergeStrategy.SIMPLE) or a
                                    custom BaseMerger instance.
                                    Default: MergeStrategy.LLM.BALANCED

            edge_strategy_or_merger: Merge strategy for deduplicating edges. Similar to
                                    node_strategy_or_merger.
                                    Default: MergeStrategy.LLM.BALANCED

            prompt_for_node_extraction: Additional user-specific prompt/context to append to the
                                       node extraction system prompt. This allows customization of
                                       node extraction behavior without replacing the full prompt.
                                       Example: "Focus on extracting only companies and their headquarters."
                                       Default: ""

            prompt_for_edge_extraction: Additional user-specific prompt/context to append to the
                                       edge extraction system prompt.
                                       Default: ""

            prompt: Additional user-specific prompt/context to append to the one-stage graph extraction
                   system prompt. Only used when extraction_mode="one_stage".
                   Default: ""

            chunk_size: Maximum character length of each text chunk for batch processing. Larger texts
                       are split into chunks for parallel extraction.
                       Default: 2048

            chunk_overlap: Number of overlapping characters between consecutive chunks to preserve
                          context at chunk boundaries.
                          Default: 256

            max_workers: Maximum number of parallel LLM calls during batch extraction. Higher values
                        improve speed but increase API usage and cost.
                        Default: 10

            verbose: Whether to print verbose logging messages during extraction, merging, and indexing.
                    Default: False

            node_fields_for_index: List of node field names to include in the vector index. If None,
                                  all fields are indexed. Useful for focusing semantic search on
                                  specific attributes (e.g., ["name", "location"]).
                                  Default: None

            edge_fields_for_index: List of edge field names to include in the vector index. If None,
                                  all fields are indexed.
                                  Default: None

            **kwargs: Additional keyword arguments passed to ontomem.merger.create_merger() when
                     node_strategy_or_merger or edge_strategy_or_merger are MergeStrategy enums.
                     Ignored if they are BaseMerger instances.
        """
        # Set observation location
        self.observation_location = observation_location or "Unknown Location"
        self._constructor_kwargs = kwargs

        # Store split extractors
        self.raw_node_key_extractor = node_key_extractor
        self.location_in_node_extractor = location_in_node_extractor

        # Create combined extractor for unique identification in memory
        # CRITICAL FOR SPATIAL: Format becomes "Name @ Location" (or just Name if no location)
        def spatial_node_key_extractor(node: NodeSchema) -> str:
            raw_key = node_key_extractor(node)
            loc = location_in_node_extractor(node)
            return f"{raw_key} @ {loc}" if loc else raw_key

        # -----------------------------------------------------------
        # Construct Prompts
        # -----------------------------------------------------------

        # 1. Node Extraction Prompt (Spatial logic lives here)
        full_node_prompt = DEFAULT_SPATIAL_NODE_ROLE_PREFIX
        if prompt_for_node_extraction:
            full_node_prompt += (
                f"\n### Context & Instructions:\n{prompt_for_node_extraction}\n"
            )
        full_node_prompt += DEFAULT_SPATIAL_NODE_RULES_SUFFIX

        # 2. Edge Extraction Prompt
        full_edge_prompt = DEFAULT_SPATIAL_EDGE_ROLE_PREFIX
        if prompt_for_edge_extraction:
            full_edge_prompt += (
                f"\n### Context & Instructions:\n{prompt_for_edge_extraction}\n"
            )
        full_edge_prompt += DEFAULT_SPATIAL_EDGE_RULES_SUFFIX

        # 3. One-Stage Graph Extraction Prompt
        full_graph_prompt = DEFAULT_SPATIAL_GRAPH_ROLE_PREFIX
        if prompt:
            full_graph_prompt += f"\n### Context & Instructions:\n{prompt}\n"
        full_graph_prompt += DEFAULT_SPATIAL_GRAPH_RULES_SUFFIX

        # Initialize parent AutoGraph
        super().__init__(
            node_schema=node_schema,
            edge_schema=edge_schema,
            node_key_extractor=spatial_node_key_extractor,
            edge_key_extractor=edge_key_extractor,
            nodes_in_edge_extractor=nodes_in_edge_extractor,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            node_strategy_or_merger=node_strategy_or_merger,
            edge_strategy_or_merger=edge_strategy_or_merger,
            prompt_for_node_extraction=full_node_prompt,
            prompt_for_edge_extraction=full_edge_prompt,
            prompt=full_graph_prompt,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            node_fields_for_index=node_fields_for_index,
            edge_fields_for_index=edge_fields_for_index,
            **kwargs,
        )
        self._node_memory.create_lookup("id", node_key_extractor)

    # ==============================================================================
    # Override Extraction Methods to Dynamically Inject Observation Location
    # ==============================================================================

    def _extract_nodes_batch(
        self, chunks: List[str]
    ) -> List[NodeListSchema[NodeSchema]]:
        """
        Override: Inject observation_location into NODE extraction (Two-Stage).

        Unlike TemporalGraph (which injects into Edges), SpatialGraph injects into Nodes
        because location is an attribute of the Node. The observation_location placeholder
        in the prompt is replaced with the actual location value.

        Args:
            chunks: List of text chunks to extract nodes from.

        Returns:
            List of NodeListSchema containing extracted nodes from each chunk.
        """
        # The prompt string (self.node_prompt) contains {observation_location} placeholder
        prompt_template = ChatPromptTemplate.from_template(
            f"{self.node_prompt}{{chunk_text}}"
        )
        llm_chain = prompt_template | self.llm_client.with_structured_output(
            self.node_list_schema
        )

        inputs = [
            {
                "chunk_text": chunk,
                "observation_location": self.observation_location,
            }
            for chunk in chunks
        ]
        return llm_chain.batch(inputs, config={"max_concurrency": self.max_workers})

    def _extract_edges_batch(
        self, chunks: List[str], node_lists: List[NodeListSchema[NodeSchema]]
    ) -> List[EdgeListSchema[EdgeSchema]]:
        """
        Batch extract edges using corresponding node lists as context.

        Override: Use raw_node_key_extractor (base name only) instead of the combined
        spatial_node_key_extractor (name @ location).

        **CRITICAL**: This method uses raw_node_key_extractor (base name only) instead of the
        combined spatial_node_key_extractor (name @ location). This is intentional to provide
        clean entity references during edge extraction. The LLM will extract edges with source/target
        referring to these base names, which will be matched against the combined keys later.

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
                # CRITICAL: Use raw_node_key_extractor (base keys without location) for entity references.
                # This prevents location suffixes from cluttering the prompt and allows the LLM to focus on relationships.
                # The edge extraction will reference these clean names, not the full "Name @ Location" identifiers.
                node_keys = [self.raw_node_key_extractor(n) for n in nodes]
                node_context = "Known entities: " + ", ".join(node_keys)

            inputs.append({"chunk_text": chunk, "node_context": node_context})

        prompt_template = ChatPromptTemplate.from_template(
            f"{self.edge_prompt}{{node_context}}\n\n### Source Text:\n{{chunk_text}}"
        )
        llm_chain = prompt_template | self.llm_client.with_structured_output(
            self.edge_list_schema
        )

        return llm_chain.batch(inputs, config={"max_concurrency": self.max_workers})

    def _extract_data_by_one_stage(self, text: str) -> Any:
        """
        Override: Inject observation_location into one-stage extraction.

        For single-stage extraction, processes entire text (or chunks if too long)
        and injects observation_location into the prompt template.

        Args:
            text: Full text to extract from.

        Returns:
            AutoGraphSchema containing extracted nodes and edges.
        """
        template_str = f"{self.prompt}{{chunk_text}}"
        prompt_template = ChatPromptTemplate.from_template(template_str)
        llm_chain = prompt_template | self.llm_client.with_structured_output(
            self.graph_schema
        )

        if len(text) <= self.chunk_size:
            inp = {
                "chunk_text": text,
                "observation_location": self.observation_location,
            }
            graph = llm_chain.invoke(inp)
            graph_list = [graph]
        else:
            chunks = self.text_splitter.split_text(text)
            inputs = [
                {"chunk_text": chunk, "observation_location": self.observation_location}
                for chunk in chunks
            ]
            graph_list = llm_chain.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )

        return self.merge_batch_data(graph_list)

    def _prune_dangling_edges(
        self, graph: AutoGraphSchema[NodeSchema, EdgeSchema]
    ) -> AutoGraphSchema[NodeSchema, EdgeSchema]:
        """Override: Prune edges connecting to non-existent nodes using RAW keys.

        **Reason for Override**:
        In AutoSpatialGraph, the primary node storage uses a combined key ("Name @ Location")
        to distinguish spatially distinct entities. However, edges are extracted using
        only the raw entity name (to avoid location confusion in relationships).

        Therefore, standard validation would fail because "Name" != "Name @ Location".
        We must validate edge endpoints against the 'raw name' using the auxiliary lookup
        index created in __init__ (self._node_memory.create_lookup("id", node_key_extractor)).

        Args:
            graph: Raw graph containing nodes and edges from the current extraction batch.

        Returns:
            Graph with only valid edges where both source and target exist in the node set
            (verified via raw name lookup).
        """
        valid_nodes = graph.nodes
        valid_node_keys = {self.raw_node_key_extractor(n) for n in valid_nodes}

        refined_edges = []
        dropped_count = 0

        for edge in graph.edges:
            src_key, dst_key = self.nodes_in_edge_extractor(edge)

            # Check if endpoints exist in CURRENT batch OR in global memory using the ID lookup.
            # The lookup checks against the 'id' (raw name) extractor defined in __init__,
            # NOT the combined "Name @ Location" key used in the primary node storage.
            src_exists = (
                src_key in valid_node_keys
                or self._node_memory.get_by_lookup("id", src_key) != []
            )
            dst_exists = (
                dst_key in valid_node_keys
                or self._node_memory.get_by_lookup("id", dst_key) != []
            )

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

    def _create_empty_instance(self) -> "AutoSpatialGraph[NodeSchema, EdgeSchema]":
        """
        Override: Recreate instance with spatial attributes preserved.

        Used during serialization/deserialization to ensure all spatial configuration
        is maintained when creating a fresh instance.

        Returns:
            New AutoSpatialGraph instance with identical configuration.
        """
        return self.__class__(
            node_schema=self.node_schema,
            edge_schema=self.edge_schema,
            node_key_extractor=self.raw_node_key_extractor,
            location_in_node_extractor=self.location_in_node_extractor,
            edge_key_extractor=self.edge_key_extractor,
            nodes_in_edge_extractor=self.nodes_in_edge_extractor,
            llm_client=self.llm_client,
            embedder=self.embedder,
            observation_location=self.observation_location,
            extraction_mode=self.extraction_mode,
            node_strategy_or_merger=self.node_merger,
            edge_strategy_or_merger=self.edge_merger,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            max_workers=self.max_workers,
            verbose=self.verbose,
            node_fields_for_index=self.node_fields_for_index,
            edge_fields_for_index=self.edge_fields_for_index,
            **self._constructor_kwargs,
        )
