"""Filing Financial Snapshot - Extracts key financial figures from SEC filings.

Extracts income statement, balance sheet, and cash flow data from 10-K/10-Q filings
into a single structured object for fundamental screening and database population.
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


class FilingFinancialSnapshotSchema(BaseModel):
    """
    A structured snapshot of key financial data extracted from SEC filings.
    """

    company_name: Optional[str] = Field(
        None, description="Legal name of the filing entity."
    )
    ticker: Optional[str] = Field(
        None, description="Stock ticker symbol (e.g., 'AAPL', 'MSFT')."
    )
    filing_type: Optional[str] = Field(
        None, description="Filing type: '10-K', '10-Q', '8-K', '20-F'."
    )
    filing_period: Optional[str] = Field(
        None,
        description="Fiscal period covered (e.g., 'FY2024', 'Q3 2024', 'Year ended Dec 31, 2024').",
    )
    revenue: Optional[str] = Field(
        None,
        description="Total revenue or net sales for the period (e.g., '$394.3 billion').",
    )
    cost_of_revenue: Optional[str] = Field(
        None, description="Cost of goods sold or cost of revenue."
    )
    gross_profit: Optional[str] = Field(
        None, description="Gross profit (Revenue minus Cost of Revenue)."
    )
    operating_income: Optional[str] = Field(
        None, description="Operating income or loss."
    )
    net_income: Optional[str] = Field(
        None, description="Net income attributable to common shareholders."
    )
    earnings_per_share: Optional[str] = Field(
        None, description="Diluted EPS (e.g., '$6.13')."
    )
    total_assets: Optional[str] = Field(
        None, description="Total assets from the balance sheet."
    )
    total_liabilities: Optional[str] = Field(
        None, description="Total liabilities from the balance sheet."
    )
    shareholders_equity: Optional[str] = Field(
        None, description="Total shareholders' equity."
    )
    cash_and_equivalents: Optional[str] = Field(
        None, description="Cash and cash equivalents."
    )
    operating_cash_flow: Optional[str] = Field(
        None, description="Net cash from operating activities."
    )
    capital_expenditures: Optional[str] = Field(
        None, description="Capital expenditures (CapEx)."
    )
    free_cash_flow: Optional[str] = Field(
        None, description="Free cash flow (Operating Cash Flow minus CapEx)."
    )
    dividends_per_share: Optional[str] = Field(
        None, description="Dividends declared per share."
    )
    shares_outstanding: Optional[str] = Field(
        None, description="Weighted average diluted shares outstanding."
    )
    key_ratios: Optional[List[str]] = Field(
        None,
        description="Notable financial ratios mentioned (e.g., 'Gross Margin: 45.6%', 'D/E Ratio: 1.2x').",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an expert financial analyst specializing in SEC filing analysis. "
    "Extract key financial figures from income statements, balance sheets, and cash flow statements "
    "embedded within this filing.\n\n"
    "Rules:\n"
    "- Extract exact dollar amounts as reported, preserving units (millions, billions).\n"
    "- Identify the filing entity, ticker, filing type, and fiscal period.\n"
    "- Extract both the most recent period and prior period comparisons when available.\n"
    "- Capture key ratios explicitly stated in the filing.\n"
    "- Use exact figures from tables; do not compute derived values unless explicitly stated.\n\n"
    "### Source Text:\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class FilingFinancialSnapshot(AutoModel[FilingFinancialSnapshotSchema]):
    """
    Applicable to: SEC 10-K Annual Reports, 10-Q Quarterly Reports, 20-F Foreign Filings,
    Annual Reports with embedded financial statements.

    Template for extracting a consolidated financial data snapshot from SEC filings.
    Merges financial figures from income statements, balance sheets, and cash flow statements
    across multiple sections of a filing into a single structured object.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> snapshot = FilingFinancialSnapshot(llm_client=llm, embedder=embedder)
        >>> filing_text = "Item 8. Financial Statements: Revenue was $394.3 billion..."
        >>> snapshot.feed_text(filing_text)
        >>> print(snapshot.data)
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
        Initialize the Filing Financial Snapshot template.

        Args:
            llm_client (BaseChatModel): The LLM for financial data extraction.
            embedder (Embeddings): Embedding model for indexing.
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoModel.
        """
        super().__init__(
            data_schema=FilingFinancialSnapshotSchema,
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
