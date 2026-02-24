"""Earnings Call Summary - Extracts key metrics and tone from earnings calls.

Extracts reported metrics (Revenue, EPS), management guidance, and overall call
tone from quarterly conference call transcripts for review dashboards.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from ontomem.merger import MergeStrategy
from hyperextract.types import AutoModel

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class EarningsCallSummarySchema(BaseModel):
    """
    Structured summary of an earnings conference call.
    """

    company_name: Optional[str] = Field(
        None, description="Name of the company."
    )
    ticker: Optional[str] = Field(
        None, description="Stock ticker symbol."
    )
    quarter: Optional[str] = Field(
        None, description="Reporting quarter (e.g., 'Q3 FY2024', 'Q4 2024')."
    )
    call_date: Optional[str] = Field(
        None, description="Date of the earnings call."
    )
    reported_revenue: Optional[str] = Field(
        None, description="Reported revenue for the quarter (e.g., '$94.8 billion')."
    )
    revenue_vs_consensus: Optional[str] = Field(
        None,
        description="Revenue vs. consensus (e.g., 'beat by $1.2B', 'in-line', 'missed by $500M').",
    )
    reported_eps: Optional[str] = Field(
        None, description="Reported diluted EPS (e.g., '$1.46')."
    )
    eps_vs_consensus: Optional[str] = Field(
        None, description="EPS vs. consensus (e.g., 'beat by $0.05')."
    )
    guidance_revenue: Optional[str] = Field(
        None,
        description="Forward revenue guidance (e.g., '$95-97B for Q4', 'FY2025 revenue $380-390B').",
    )
    guidance_eps: Optional[str] = Field(
        None, description="Forward EPS guidance if provided."
    )
    overall_tone: Optional[str] = Field(
        None,
        description="Overall tone of the call: 'Positive', 'Cautiously Optimistic', 'Neutral', 'Cautious', 'Negative'.",
    )
    key_highlights: Optional[List[str]] = Field(
        None,
        description="Top 3-5 highlights from management's prepared remarks.",
    )
    key_concerns: Optional[List[str]] = Field(
        None,
        description="Top concerns raised by management or analysts during Q&A.",
    )
    strategic_priorities: Optional[List[str]] = Field(
        None,
        description="Strategic priorities emphasized by management.",
    )
    ceo_name: Optional[str] = Field(
        None, description="CEO or primary presenter name."
    )
    cfo_name: Optional[str] = Field(
        None, description="CFO name."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a buy-side analyst reviewing an earnings call transcript. "
    "Extract the key financial metrics, guidance, and overall tone.\n\n"
    "Rules:\n"
    "- Extract exact reported figures (Revenue, EPS) and compare to consensus.\n"
    "- Capture forward guidance for revenue and earnings.\n"
    "- Assess the overall tone of the call (management's language, analyst reactions).\n"
    "- List key highlights from prepared remarks and concerns from Q&A.\n"
    "- Identify strategic priorities management emphasized.\n\n"
    "### Source Text:\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class EarningsCallSummary(AutoModel[EarningsCallSummarySchema]):
    """
    Applicable to: Quarterly Earnings Call Transcripts, Earnings Press Releases,
    Investor Day Transcripts, Annual Meeting Transcripts.

    Template for extracting a structured summary from earnings call transcripts.
    Produces a single consolidated view of reported metrics, guidance, tone, and
    key themes for quarterly review dashboards and consensus tracking.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> summary = EarningsCallSummary(llm_client=llm, embedder=embedder)
        >>> transcript = "Good afternoon. Q3 revenue was $94.8 billion, beating consensus..."
        >>> summary.feed_text(transcript)
        >>> print(summary.data)
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
        Initialize the Earnings Call Summary template.

        Args:
            llm_client (BaseChatModel): The LLM for transcript extraction.
            embedder (Embeddings): Embedding model for indexing.
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoModel.
        """
        super().__init__(
            data_schema=EarningsCallSummarySchema,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=MergeStrategy.LLM.BALANCED,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )
