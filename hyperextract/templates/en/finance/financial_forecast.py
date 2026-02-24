"""Financial Forecast - Extracts projected financial data from equity research reports.

Extracts revenue, EPS, PE, and other financial projections for future periods
from analyst reports for consensus analysis and financial modeling.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class ForecastItem(BaseModel):
    """
    A single financial projection for a specific metric and period.
    """

    metric: str = Field(
        description="Financial metric being projected (e.g., 'Revenue', 'EPS', 'EBITDA', 'Operating Margin', 'Free Cash Flow')."
    )
    period: str = Field(
        description="Forecast period (e.g., 'FY2025E', 'Q1 2025E', 'CY2026E')."
    )
    estimate: str = Field(
        description="Projected value (e.g., '$120.5B', '$6.25', '35.2%')."
    )
    prior_estimate: Optional[str] = Field(
        None, description="Previous estimate if revised (e.g., '$115.0B')."
    )
    consensus: Optional[str] = Field(
        None, description="Street consensus estimate for comparison (e.g., '$118.2B')."
    )
    growth_rate: Optional[str] = Field(
        None,
        description="Implied growth rate (e.g., '+15% YoY', 'flat').",
    )
    assumptions: Optional[str] = Field(
        None,
        description="Key assumptions underlying the estimate (e.g., 'assumes 5M unit increase').",
    )
    source_firm: Optional[str] = Field(
        None, description="Research firm providing the estimate."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a financial analyst building earnings models. Extract all financial projections "
    "and estimates from this equity research report.\n\n"
    "Rules:\n"
    "- Extract every projected metric with its specific time period.\n"
    "- Capture both current and prior estimates when revisions are noted.\n"
    "- Extract consensus estimates when compared.\n"
    "- Capture growth rates and key assumptions.\n"
    "- Extract EVERY forecast independently as a separate item.\n\n"
    "### Source Text:\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class FinancialForecast(AutoList[ForecastItem]):
    """
    Applicable to: Equity Research Reports, Earnings Estimates, Financial Models,
    Consensus Estimate Reports, Analyst Forecasts.

    Template for extracting projected financial data from analyst reports. Each
    forecast is captured as an independent list item, enabling consensus analysis,
    estimate revision tracking, and financial model building.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> forecast = FinancialForecast(llm_client=llm, embedder=embedder)
        >>> report = "We raise our FY2025 revenue estimate to $120.5B (from $115B)..."
        >>> forecast.feed_text(report)
        >>> forecast.show()
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
        Initialize the Financial Forecast template.

        Args:
            llm_client (BaseChatModel): The LLM for estimate extraction.
            embedder (Embeddings): Embedding model for indexing.
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoList.
        """
        super().__init__(
            item_schema=ForecastItem,
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
        Visualize the financial forecast list.

        Args:
            top_k_for_search (int): Items for search. Default 3.
            top_k_for_chat (int): Items for chat context. Default 3.
        """

        def label_extractor(item: ForecastItem) -> str:
            return f"{item.metric} ({item.period}): {item.estimate}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
