from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definition
# ==============================================================================


class CaseEntity(BaseModel):
    """
    Failure case entity, including phenomena, causes, measures, lessons, etc.
    """

    name: str = Field(description="Name of the entity such as phenomenon or measure.")
    category: str = Field(
        description='Category: phenomenon, cause, measure, lesson.'
    )
    description: Optional[str] = Field(
        None,
        description="Further elaboration and explanation of the entity.",
    )
    equipment: Optional[str] = Field(
        None,
        description="Involved equipment name.",
    )


class CaseChain(BaseModel):
    """
    Relationship between failure case stages.
    """

    source: str = Field(description="Upstream stage name.")
    target: str = Field(description="Downstream stage name.")
    relation_type: str = Field(
        description='Relation type: leads to, takes, produces, discovers. Use "leads to" for cause-result, "takes" for taking measures.'
    )
    time_sequence: Optional[str] = Field(
        None,
        description="Temporal relationship: discovery, analysis, processing, summary.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an industrial equipment failure analysis expert. Extract failure phenomena, causes, handling measures, and lessons learned from failure case documents.\n\n"
    "Rules:\n"
    "- Identify failure phenomena and abnormal manifestations.\n"
    "- Analyze failure causes and root causes.\n"
    "- Extract handling measures and solutions.\n"
    "- Summarize lessons learned and improvement suggestions.\n"
    "- Establish a complete chain from discovery to processing.\n"
)

_NODE_PROMPT = (
    "You are an industrial equipment failure analysis expert. Extract all related entities (nodes) from failure case documents.\n\n"
    "Extraction Rules:\n"
    "- Identify failure phenomena and abnormal manifestations.\n"
    "- Identify failure causes and root causes.\n"
    "- Identify handling measures and solutions.\n"
    "- Identify lessons learned and improvement suggestions.\n"
    "- Record involved equipment names.\n"
    "- Do not establish relationships between stages.\n"
)

_EDGE_PROMPT = (
    "You are an industrial equipment failure analysis expert. Based on the entity list, extract relationship between failure case stages (edges).\n\n"
    "Extraction Rules:\n"
    "- Identify association from phenomenon to cause.\n"
    "- Identify association from cause to measure.\n"
    "- Identify association from measure to lesson.\n"
    "- Temporal relationship: discovery → analysis → processing → summary.\n"
    "- Only establish relationships within the provided entity list.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class FailureCaseGraph(AutoGraph[CaseEntity, CaseChain]):
    """
    Applicable Documents: Failure case library, accident analysis reports, equipment anomaly records, maintenance reports.

    This template extracts failure phenomena, causes, measures, and lessons from failure case documents.
    It identifies the complete failure evolution chain from discovery to processing,
    providing reference for equipment maintenance and prevention.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> failure_case = FailureCaseGraph(llm_client=llm, embedder=embedder)
        >>> doc = "In January 2024, the main motor of Line A suddenly emitted abnormal sounds accompanied by increased vibration. Inspection revealed severe bearing wear, immediately replaced bearing and returned to normal. This failure reminds us to strengthen daily bearing inspection."
        >>> failure_case.feed_text(doc)
        >>> failure_case.show()
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
        Initialize Failure Case Graph template.

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
            node_schema=CaseEntity,
            edge_schema=CaseChain,
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
        Visualize failure case graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of relationships to retrieve. Default 3.
            top_k_nodes_for_chat (int): Number of entities in chat context. Default 3.
            top_k_edges_for_chat (int): Number of relationships in chat context. Default 3.
        """

        def node_label_extractor(node: CaseEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: CaseChain) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
