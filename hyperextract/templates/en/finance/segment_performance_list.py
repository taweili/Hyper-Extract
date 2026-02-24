"""Segment Performance List - Extracts revenue and metrics by business segment.

Extracts revenue, operating income, and key metrics by business segment or
geographic region from SEC filings for segment-level valuation and exposure analysis.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class SegmentPerformanceItem(BaseModel):
    """
    Performance data for a single business segment or geographic region.
    """

    segment_name: str = Field(
        description="Name of the business segment or geographic region (e.g., 'Americas', 'Cloud Services', 'iPhone')."
    )
    segment_type: str = Field(
        description="Type: 'Business Segment', 'Geographic Region', 'Product Line', 'Operating Segment'."
    )
    revenue: Optional[str] = Field(
        None, description="Segment revenue for the period (e.g., '$48.2 billion')."
    )
    operating_income: Optional[str] = Field(
        None, description="Segment operating income or profit."
    )
    revenue_growth: Optional[str] = Field(
        None,
        description="Year-over-year or sequential revenue growth (e.g., '+12%', '-3% YoY').",
    )
    key_metrics: Optional[List[str]] = Field(
        None,
        description="Segment-specific KPIs (e.g., ['Subscribers: 230M', 'ARPU: $14.99', 'Churn: 2.1%']).",
    )
    commentary: Optional[str] = Field(
        None,
        description="Management commentary on segment performance or outlook.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a financial analyst specializing in segment-level analysis. "
    "Extract performance data for each business segment or geographic region from SEC filings.\n\n"
    "Rules:\n"
    "- Extract revenue and operating income for each identifiable segment.\n"
    "- Capture growth rates and comparisons to prior periods.\n"
    "- Extract segment-specific KPIs and metrics.\n"
    "- Preserve management's segment commentary.\n"
    "- Extract EVERY segment independently as a separate item.\n\n"
    "### Source Text:\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class SegmentPerformanceList(AutoList[SegmentPerformanceItem]):
    """
    Applicable to: SEC 10-K/10-Q Segment Disclosures (ASC 280), Annual Reports,
    Earnings Releases with segment breakdowns.

    Template for extracting segment-level financial performance data from filings.
    Each segment is captured as an independent list item for comparative analysis
    and segment-level valuation.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> segments = SegmentPerformanceList(llm_client=llm, embedder=embedder)
        >>> filing = "Americas segment revenue was $48.2B, up 12% YoY..."
        >>> segments.feed_text(filing)
        >>> segments.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize the Segment Performance List template.

        Args:
            llm_client (BaseChatModel): The LLM for segment data extraction.
            embedder (Embeddings): Embedding model for indexing.
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoList.
        """
        super().__init__(
            item_schema=SegmentPerformanceItem,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """
        Visualize the segment performance list.

        Args:
            top_k_for_search (int): Items for search. Default 3.
            top_k_for_chat (int): Items for chat context. Default 3.
        """

        def label_extractor(item: SegmentPerformanceItem) -> str:
            rev = f" | {item.revenue}" if item.revenue else ""
            return f"{item.segment_name} ({item.segment_type}){rev}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
