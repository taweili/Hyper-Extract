from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definition
# ==============================================================================


class EmergencyEntity(BaseModel):
    """
    Emergency plan entity, including accident scenarios, response actions, departments, etc.
    """

    name: str = Field(description="Entity name (e.g., fire, power outage, alarm, evacuate personnel, equipment department).")
    category: str = Field(
        description='Category: accident scenario, response action, department.'
    )
    description: Optional[str] = Field(
        None,
        description="Description of this entity.",
    )


class ResponseFlow(BaseModel):
    """
    Emergency response flow relationship.
    """

    source: str = Field(description="Source entity name (accident scenario or response action).")
    target: str = Field(description="Target entity name (response action or department).")
    relation_type: str = Field(
        description='Relation type: triggers, executes, responsible for. Use "triggers" for accident triggering response, "executes" for executing response action, "responsible for" for department responsibility.'
    )
    time_limit: Optional[str] = Field(
        None,
        description="Response time requirement (e.g., within 5 minutes, within 10 minutes).",
    )
    success_criterion: Optional[str] = Field(
        None,
        description="Success criterion (e.g., personnel safely evacuated, fire controlled).",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an industrial emergency management analysis expert. Extract accident scenarios, response actions, and departments from emergency plan documents to build emergency response flows.\n\n"
    "Rules:\n"
    "- Identify accident scenarios (e.g., fire, leakage, power outage, equipment failure).\n"
    "- Identify response actions (e.g., alarm, evacuate personnel, shut off power).\n"
    "- Identify responsible departments (e.g., security department, equipment department, first aid department).\n"
    "- Establish flow relationships from accident scenarios to response actions.\n"
    "- Record time requirements and success criteria.\n"
)

_NODE_PROMPT = (
    "You are an industrial emergency management analysis expert. Extract all entities (nodes) from emergency plan documents.\n\n"
    "Extraction Rules:\n"
    "- Identify accident scenario names.\n"
    "- Identify response action names.\n"
    "- Identify responsible department names.\n"
    "- Assign category for each entity (accident scenario/response action/department).\n"
    "- Do not establish relationships between entities.\n"
)

_EDGE_PROMPT = (
    "You are an industrial emergency management analysis expert. Based on the entity list, extract emergency response flow relationships (edges).\n\n"
    "Extraction Rules:\n"
    "- Identify association from accident scenario to response action.\n"
    "- Identify association from response action to responsible department.\n"
    "- Record response time requirements.\n"
    "- Record success criteria.\n"
    "- Only establish relationships within the provided entity list.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class EmergencyResponseGraph(AutoGraph[EmergencyEntity, ResponseFlow]):
    """
    Applicable Documents: Emergency plans, emergency response plans, safety procedures.

    This template extracts accident scenarios, response actions, and departments from emergency plans to build emergency response flows.
    It uses category to distinguish heterogeneous nodes and identifies emergency response flows and responsibility division.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> emergency = EmergencyResponseGraph(llm_client=llm, embedder=embedder)
        >>> doc = "When a fire occurs, immediately alarm and activate emergency plan. Security department is responsible for evacuating personnel, equipment department is responsible for shutting off power..."
        >>> emergency.feed_text(doc)
        >>> emergency.show()
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
        Initialize Emergency Response Graph template.

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
            node_schema=EmergencyEntity,
            edge_schema=ResponseFlow,
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
        Visualize emergency response graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of relationships to retrieve. Default 3.
            top_k_nodes_for_chat (int): Number of entities in chat context. Default 3.
            top_k_edges_for_chat (int): Number of relationships in chat context. Default 3.
        """

        def node_label_extractor(node: EmergencyEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: ResponseFlow) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
