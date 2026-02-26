from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definition
# ==============================================================================


class SafetyEntity(BaseModel):
    """
    Safety control entity, including hazard sources, risk points, control measures, responsible persons, etc.
    """

    name: str = Field(description="Entity name (e.g., high temperature high pressure equipment, electric shock risk, wear protective equipment, safety supervisor).")
    category: str = Field(
        description='Category: hazard source, risk point, control measure, responsible person.'
    )
    description: Optional[str] = Field(
        None,
        description="Description of this entity.",
    )


class SafetyRelation(BaseModel):
    """
    Safety control relationship.
    """

    source: str = Field(description="Source entity name (hazard source or risk point).")
    target: str = Field(description="Target entity name (control measure or responsible person).")
    relation_type: str = Field(
        description='Relation type: controls, responsible for. Use "controls" for hazard source/risk point to control measure, "responsible for" for control measure to responsible person.'
    )
    control_measure: Optional[str] = Field(
        None,
        description="Specific content of control measure.",
    )
    responsible_person: Optional[str] = Field(
        None,
        description="Name of responsible person or department.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an industrial safety management analysis expert. Extract hazard sources, risk points, and control measures from safety procedure documents to build safety control relationships.\n\n"
    "Rules:\n"
    "- Identify hazard sources (e.g., high temperature high pressure equipment, electrical equipment, chemicals).\n"
    "- Identify risk points (e.g., electric shock risk, burn risk, mechanical injury).\n"
    "- Identify control measures (e.g., wear protective equipment, regular maintenance, ventilation).\n"
    "- Identify responsible persons (e.g., safety supervisor, equipment person in charge).\n"
    "- Establish relationships from hazard sources/risk points to control measures/responsible persons.\n"
)

_NODE_PROMPT = (
    "You are an industrial safety management analysis expert. Extract all entities (nodes) from safety procedure documents.\n\n"
    "Extraction Rules:\n"
    "- Identify hazard source names.\n"
    "- Identify risk point names.\n"
    "- Identify control measure names.\n"
    "- Identify responsible person names.\n"
    "- Assign category for each entity (hazard source/risk point/control measure/responsible person).\n"
    "- Do not establish relationships between entities.\n"
)

_EDGE_PROMPT = (
    "You are an industrial safety management analysis expert. Based on the entity list, extract safety control relationships (edges).\n\n"
    "Extraction Rules:\n"
    "- Identify association from hazard source to control measure.\n"
    "- Identify association from risk point to control measure.\n"
    "- Identify association from control measure to responsible person.\n"
    "- Record specific content of control measures.\n"
    "- Record responsible person information.\n"
    "- Only establish relationships within the provided entity list.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class SafetyControlGraph(AutoGraph[SafetyEntity, SafetyRelation]):
    """
    Applicable Documents: Safety procedures, safety risk assessment reports, occupational health and safety manuals.

    This template extracts hazard sources, risk points, and control measures from safety procedures to build safety control relationships.
    It uses category to distinguish heterogeneous nodes and identifies the correspondence between safety risks and control responsibilities.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> safety = SafetyControlGraph(llm_client=llm, embedder=embedder)
        >>> doc = "High temperature equipment has burn risk, need to wear protective gloves. Equipment person in charge is responsible for supervision and inspection..."
        >>> safety.feed_text(doc)
        >>> safety.show()
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
        Initialize Safety Control Graph template.

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
            node_schema=SafetyEntity,
            edge_schema=SafetyRelation,
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
        Visualize safety control graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of relationships to retrieve. Default 3.
            top_k_nodes_for_chat (int): Number of entities in chat context. Default 3.
            top_k_edges_for_chat (int): Number of relationships in chat context. Default 3.
        """

        def node_label_extractor(node: SafetyEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: SafetyRelation) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
