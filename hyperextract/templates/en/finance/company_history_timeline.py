"""Company History Timeline - Chronological extraction of corporate milestones.

Extracts founding events, funding rounds, major pivots, and key milestones
from prospectuses and company histories for due diligence and history mapping.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class CorporateEntity(BaseModel):
    """
    An entity involved in corporate history milestones.
    """

    name: str = Field(
        description="Name of the entity (e.g., company name, founder, investor, acquiree)."
    )
    entity_type: str = Field(
        description="Type: 'Company', 'Founder', 'Investor', 'Acquiree', 'Partner', 'Regulator'."
    )
    description: Optional[str] = Field(
        None, description="Role or context (e.g., 'Series A lead', 'Acquired subsidiary')."
    )


class CorporateMilestoneEdge(BaseModel):
    """
    A corporate milestone event with temporal context.
    """

    source: str = Field(description="The acting entity name.")
    target: str = Field(description="The affected entity or milestone target.")
    event_type: str = Field(
        description="Type: 'Founding', 'Funding Round', 'Acquisition', 'Product Launch', "
        "'IPO', 'Pivot', 'Partnership', 'Expansion', 'Restructuring', 'Key Hire'."
    )
    start_timestamp: Optional[str] = Field(
        None,
        description="Date of the milestone (e.g., '2015-06', 'March 2018', '2020').",
    )
    end_timestamp: Optional[str] = Field(
        None,
        description="End date if applicable (e.g., acquisition closing date).",
    )
    description: Optional[str] = Field(
        None,
        description="Details of the milestone (e.g., '$50M Series B led by Sequoia').",
    )
    financial_details: Optional[str] = Field(
        None,
        description="Financial terms when available (e.g., valuation, deal size).",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a due diligence analyst. Extract corporate history milestones and the entities "
    "involved from this prospectus or company history document.\n\n"
    "Rules:\n"
    "- Identify founding events, funding rounds, acquisitions, pivots, and key hires.\n"
    "- Extract specific dates or time periods for each milestone.\n"
    "- Capture financial details (valuations, deal sizes) when mentioned.\n"
    "- Maintain chronological accuracy."
)

_NODE_PROMPT = (
    "You are a due diligence analyst. Extract all entities (Nodes) involved in corporate history.\n\n"
    "Extraction Rules:\n"
    "- Identify the company, founders, investors, acquired companies, and partners.\n"
    "- Classify each entity by type.\n"
    "- DO NOT extract events at this stage."
)

_EDGE_PROMPT = (
    "You are a due diligence analyst. Given the entities, extract corporate milestones (Edges) with dates.\n\n"
    "Extraction Rules:\n"
    "- Connect entities through milestone events.\n"
    "- Extract specific dates or time periods.\n"
    "- Capture financial details (deal sizes, valuations).\n"
    "- Classify each milestone by type.\n"
    "- Only create edges between nodes that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class CompanyHistoryTimeline(
    AutoTemporalGraph[CorporateEntity, CorporateMilestoneEdge]
):
    """
    Applicable to: S-1 Prospectuses (Business section), Company About pages,
    Due Diligence reports, Corporate History summaries, Investor Presentations.

    Template for chronologically extracting corporate milestones from prospectuses
    and company histories. Enables due diligence timeline construction and
    corporate evolution tracking.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> history = CompanyHistoryTimeline(llm_client=llm, embedder=embedder)
        >>> text = "Founded in 2015 by John Doe. Raised $10M Series A in 2017..."
        >>> history.feed_text(text)
        >>> history.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: str = "2024-01-01",
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize the Company History Timeline template.

        Args:
            llm_client (BaseChatModel): The LLM for milestone extraction.
            embedder (Embeddings): Embedding model for deduplication.
            observation_time (str): Reference time for resolving relative dates.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoTemporalGraph.
        """
        super().__init__(
            node_schema=CorporateEntity,
            edge_schema=CorporateMilestoneEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}|{x.event_type.lower()}|{x.target.strip().lower()}"
            ),
            time_in_edge_extractor=lambda x: x.start_timestamp or "",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
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
        Visualize the company history timeline using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of milestones to retrieve. Default 3.
            top_k_nodes_for_chat (int): Entities for chat context. Default 3.
            top_k_edges_for_chat (int): Milestones for chat context. Default 3.
        """

        def node_label_extractor(node: CorporateEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: CorporateMilestoneEdge) -> str:
            date = f" [{edge.start_timestamp}]" if edge.start_timestamp else ""
            return f"{edge.event_type}{date}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
