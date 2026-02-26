from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definition
# ==============================================================================


class SystemEntity(BaseModel):
    """
    System topology entity, including factory, system, subsystem, equipment, etc.
    """

    name: str = Field(description="Entity name (e.g., Factory A, Manufacturing Workshop A, CNC machining system, cooling system).")
    category: str = Field(
        description='Category: factory, system, subsystem, equipment.'
    )
    function: Optional[str] = Field(
        None,
        description="Function description.",
    )
    capacity: Optional[str] = Field(
        None,
        description="Capacity or scale.",
    )


class SystemHierarchy(BaseModel):
    """
    System hierarchy relationship.
    """

    source: str = Field(description="Parent entity name (factory or system).")
    target: str = Field(description="Child entity name (system or subsystem or equipment).")
    relation_type: str = Field(
        description='Relation type: contains, belongs to, subordinate. Use "contains" to indicate parent contains child.'
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an industrial system architecture analysis expert. Extract hierarchy relationships between factory, system, subsystem, and equipment from system manuals.\n\n"
    "Rules:\n"
    "- Identify factories (e.g., Factory A, Factory B).\n"
    "- Identify production systems (e.g., manufacturing workshop, processing workshop).\n"
    "- Identify subsystems (e.g., CNC machining system, cooling system, material handling system).\n"
    "- Identify specific equipment (e.g., CNC machining center, robotic arm, pump).\n"
    "- Establish hierarchical inclusion relationships between upper and lower levels.\n"
)

_NODE_PROMPT = (
    "You are an industrial system architecture analysis expert. Extract all entities (nodes) from system manuals.\n\n"
    "Extraction Rules:\n"
    "- Identify factory names.\n"
    "- Identify production system names.\n"
    "- Identify subsystem names.\n"
    "- Identify specific equipment names.\n"
    "- Assign category for each entity (factory/system/subsystem/equipment).\n"
    "- Do not establish relationships between entities.\n"
)

_EDGE_PROMPT = (
    "You are an industrial system architecture analysis expert. Based on the entity list, extract system hierarchy relationships (edges).\n\n"
    "Extraction Rules:\n"
    "- Identify inclusion relationship between factory and system.\n"
    "- Identify inclusion relationship between system and subsystem.\n"
    "- Identify inclusion relationship between subsystem and equipment.\n"
    "- Record hierarchy type.\n"
    "- Only establish relationships within the provided entity list.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class SystemTopologyGraph(AutoGraph[SystemEntity, SystemHierarchy]):
    """
    Applicable Documents: System manuals, factory layout diagrams, system architecture documents.

    This template extracts hierarchy relationships between factory, system, subsystem, and equipment from system manuals.
    It constructs a complete factory system architecture view.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> topology = SystemTopologyGraph(llm_client=llm, embedder=embedder)
        >>> doc = "Factory A contains Manufacturing Workshop A, Manufacturing Workshop A includes CNC machining system and material handling system..."
        >>> topology.feed_text(doc)
        >>> topology.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize System Topology Graph template.

        Args:
            llm_client (BaseChatModel): LLM for entity and relationship extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage". Default is "two_stage".
            chunk_size (int): Maximum characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Number of parallel processing worker threads.
            verbose (bool): Enable progress logging.
            **kwargs: Additional AutoGraph parameters.
        """
        super().__init__(
            node_schema=SystemEntity,
            edge_schema=SystemHierarchy,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.relation_type})-->{x.target.strip()}"
            ),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ) -> None:
        """
        Visualize system topology graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of relationships to retrieve. Default 3.
            top_k_nodes_for_chat (int): Number of entities in chat context. Default 3.
            top_k_edges_for_chat (int): Number of relationships in chat context. Default 3.
        """

        def node_label_extractor(node: SystemEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: SystemHierarchy) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
