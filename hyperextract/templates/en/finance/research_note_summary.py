"""Research Note Summary - Extracts core investment thesis from equity research reports.

Extracts ratings, target prices, and top-level investment logic from analyst research
notes for report database population and screening.
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


class ResearchNoteSummarySchema(BaseModel):
    """
    Structured summary of an equity research report.
    """

    company_name: Optional[str] = Field(
        None, description="Name of the covered company."
    )
    ticker: Optional[str] = Field(
        None, description="Stock ticker symbol (e.g., 'AAPL', 'NVDA')."
    )
    analyst_name: Optional[str] = Field(
        None, description="Name of the lead analyst."
    )
    research_firm: Optional[str] = Field(
        None, description="Name of the research firm (e.g., 'Goldman Sachs', 'Morgan Stanley')."
    )
    report_date: Optional[str] = Field(
        None, description="Publication date of the report."
    )
    rating: Optional[str] = Field(
        None,
        description="Analyst rating: 'Buy', 'Overweight', 'Hold', 'Neutral', 'Sell', 'Underweight'.",
    )
    prior_rating: Optional[str] = Field(
        None, description="Previous rating if changed."
    )
    target_price: Optional[str] = Field(
        None, description="Current price target (e.g., '$150.00')."
    )
    prior_target_price: Optional[str] = Field(
        None, description="Previous price target if changed."
    )
    current_price: Optional[str] = Field(
        None, description="Stock price at time of report."
    )
    investment_thesis: Optional[str] = Field(
        None,
        description="Core investment thesis or key argument for the rating.",
    )
    key_catalysts: Optional[List[str]] = Field(
        None,
        description="Near-term catalysts identified (e.g., ['Q4 earnings beat', 'New product launch', 'Regulatory approval']).",
    )
    key_risks: Optional[List[str]] = Field(
        None,
        description="Key risks highlighted by the analyst.",
    )
    revenue_estimate: Optional[str] = Field(
        None, description="Analyst's revenue estimate for the current/next fiscal year."
    )
    eps_estimate: Optional[str] = Field(
        None, description="Analyst's EPS estimate for the current/next fiscal year."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an equity research analyst. Extract the core investment thesis, rating, target price, "
    "and key arguments from this research report.\n\n"
    "Rules:\n"
    "- Extract the analyst's rating and any rating changes.\n"
    "- Capture target price and prior target price if changed.\n"
    "- Summarize the core investment thesis concisely.\n"
    "- List key catalysts and risks as identified by the analyst.\n"
    "- Extract financial estimates (revenue, EPS) when stated.\n\n"
    "### Source Text:\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class ResearchNoteSummary(AutoModel[ResearchNoteSummarySchema]):
    """
    Applicable to: Equity Research Reports, Analyst Notes, Rating Changes,
    Initiation of Coverage reports, Sector Research.

    Template for extracting the core investment thesis and key parameters from
    equity research reports. Produces a single structured summary per report for
    database population and screening.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> summary = ResearchNoteSummary(llm_client=llm, embedder=embedder)
        >>> report = "We upgrade AAPL to Buy with a $200 price target..."
        >>> summary.feed_text(report)
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
        Initialize the Research Note Summary template.

        Args:
            llm_client (BaseChatModel): The LLM for report extraction.
            embedder (Embeddings): Embedding model for indexing.
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoModel.
        """
        super().__init__(
            data_schema=ResearchNoteSummarySchema,
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
