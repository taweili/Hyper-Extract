from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definition
# ==============================================================================


class InspectionEntity(BaseModel):
    """
    Inspection entity, including equipment and inspection items.
    """

    name: str = Field(description="Entity name (e.g., CNC machining center, robotic arm system, motor operation status, bearing temperature inspection).")
    category: str = Field(
        description='Category: equipment, inspection item.'
    )
    description: Optional[str] = Field(
        None,
        description="Description of this entity.",
    )


class InspectionHierarchy(BaseModel):
    """
    Hierarchy relationship between inspection entities.
    """

    source: str = Field(description="Parent entity (whole/equipment) name.")
    target: str = Field(description="Child entity (inspection item/part) name.")
    relation_type: str = Field(
        description='Relation type: belongs to, subclass. Use "belongs to" to indicate inspection item belongs to a specific equipment.'
    )
    details: Optional[str] = Field(
        None,
        description="Detailed description of the relationship.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an industrial equipment inspection analysis expert. Extract equipment and inspection items from inspection records to build inspection hierarchy.\n\n"
    "Rules:\n"
    "- Identify major equipment (e.g., CNC machining center, robotic arm system, material handling system).\n"
    "- Identify inspection items under each equipment (e.g., motor operation status, bearing temperature, coolant level).\n"
    "- Establish belonging relationship (Part-Of) between inspection items and equipment.\n"
)

_NODE_PROMPT = (
    "You are an industrial equipment inspection analysis expert. Extract all entities (nodes) from inspection records.\n\n"
    "Extraction Rules:\n"
    "- Identify equipment names (main categories).\n"
    "- Identify inspection item names (specific check points).\n"
    "- Assign category for each entity (equipment/inspection item).\n"
    "- Do not establish relationships between entities.\n"
)

_EDGE_PROMPT = (
    "You are an industrial equipment inspection analysis expert. Based on the entity list, extract hierarchy relationships between entities (edges).\n\n"
    "Extraction Rules:\n"
    "- Identify belonging relationship (Part-Of) between inspection items and equipment.\n"
    "- For example: motor operation status belongs to CNC machining center.\n"
    "- Only establish relationships within the provided entity list.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class InspectionRecordGraph(AutoGraph[InspectionEntity, InspectionHierarchy]):
    """
    Applicable Documents: Inspection record books, equipment operation records, inspection daily reports, equipment point inspection forms.

    This template extracts equipment and inspection items from inspection records to build inspection hierarchy.
    It identifies the belonging relationship (Part-Of) between equipment and inspection items.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> inspection = InspectionRecordGraph(llm_client=llm, embedder=embedder)
        >>> doc = "March 15, 2024, daily inspection of Line A. CNC machining center: motor operating normally..."
        >>> inspection.feed_text(doc)
        >>> inspection.show()
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
        Initialize Inspection Record Graph template.

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
            node_schema=InspectionEntity,
            edge_schema=InspectionHierarchy,
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
        Visualize inspection record graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of relationships to retrieve. Default 3.
            top_k_nodes_for_chat (int): Number of entities in chat context. Default 3.
            top_k_edges_for_chat (int): Number of relationships in chat context. Default 3.
        """

        def node_label_extractor(node: InspectionEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: InspectionHierarchy) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
