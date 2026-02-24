"""Analyst Q&A Graph - Maps analyst questions to management responses.

Extracts the question-and-answer interactions from earnings call Q&A sessions,
capturing concerns raised and commitments made for analyst focus analysis.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class QAParticipant(BaseModel):
    """
    A participant in the earnings call Q&A session.
    """

    name: str = Field(
        description="Name of the participant (e.g., analyst name, CEO, CFO)."
    )
    role: str = Field(
        description="Role: 'Analyst', 'CEO', 'CFO', 'COO', 'CTO', 'IR Head', 'Other Management'."
    )
    firm: Optional[str] = Field(
        None,
        description="Firm affiliation (e.g., 'JPMorgan', 'Goldman Sachs') for analysts.",
    )


class QAInteraction(BaseModel):
    """
    A question-answer interaction between analyst and management.
    """

    source: str = Field(description="The questioner's name (analyst).")
    target: str = Field(description="The responder's name (management).")
    topic: str = Field(
        description="Topic of the question (e.g., 'Margin outlook', 'AI strategy', 'Capital allocation')."
    )
    question_summary: str = Field(
        description="Concise summary of the analyst's question."
    )
    answer_summary: str = Field(
        description="Concise summary of management's response."
    )
    sentiment: Optional[str] = Field(
        None,
        description="Tone of the exchange: 'Constructive', 'Pressing', 'Reassuring', 'Evasive', 'Direct'.",
    )
    commitment_made: Optional[str] = Field(
        None,
        description="Any specific commitment from management (e.g., 'will provide update next quarter').",
    )
    follow_up: Optional[bool] = Field(
        None,
        description="Whether the analyst asked a follow-up question on the same topic.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an earnings call analyst. Extract the Q&A interactions between analysts and management "
    "from this earnings call transcript.\n\n"
    "Rules:\n"
    "- Identify each analyst and management participant.\n"
    "- Summarize each question and its corresponding answer.\n"
    "- Capture the topic and sentiment of each exchange.\n"
    "- Note any commitments management makes.\n"
    "- Track follow-up questions on the same topic."
)

_NODE_PROMPT = (
    "You are an earnings call analyst. Extract all Q&A participants (Nodes).\n\n"
    "Extraction Rules:\n"
    "- Identify analysts by name and firm.\n"
    "- Identify management participants by name and role.\n"
    "- DO NOT extract Q&A interactions at this stage."
)

_EDGE_PROMPT = (
    "You are an earnings call analyst. Given the participants, extract Q&A interactions (Edges).\n\n"
    "Extraction Rules:\n"
    "- Connect each analyst question to the management response.\n"
    "- Summarize both the question and answer concisely.\n"
    "- Capture the topic, sentiment, and any commitments.\n"
    "- Only create edges between nodes that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class AnalystQAGraph(AutoGraph[QAParticipant, QAInteraction]):
    """
    Applicable to: Earnings Call Transcripts (Q&A section), Investor Day Q&A,
    Annual Meeting Q&A, Analyst Day Transcripts.

    Template for mapping analyst questions to management responses in earnings calls.
    Enables analyst focus analysis, commitment tracking, and identification of
    key concerns across the analyst community.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> qa = AnalystQAGraph(llm_client=llm, embedder=embedder)
        >>> transcript = "Analyst: Can you discuss your margin outlook? CEO: We expect margins to..."
        >>> qa.feed_text(transcript)
        >>> qa.show()
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
        Initialize the Analyst Q&A Graph template.

        Args:
            llm_client (BaseChatModel): The LLM for Q&A extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoGraph.
        """
        super().__init__(
            node_schema=QAParticipant,
            edge_schema=QAInteraction,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}|{x.topic.lower()}|{x.target.strip().lower()}"
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
        Visualize the analyst Q&A graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of participants to retrieve. Default 3.
            top_k_edges_for_search (int): Number of Q&A interactions to retrieve. Default 3.
            top_k_nodes_for_chat (int): Participants for chat context. Default 3.
            top_k_edges_for_chat (int): Interactions for chat context. Default 3.
        """

        def node_label_extractor(node: QAParticipant) -> str:
            firm = f" @ {node.firm}" if node.firm else ""
            return f"{node.name} ({node.role}{firm})"

        def edge_label_extractor(edge: QAInteraction) -> str:
            sentiment = f" [{edge.sentiment}]" if edge.sentiment else ""
            return f"{edge.topic}{sentiment}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
