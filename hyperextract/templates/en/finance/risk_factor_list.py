"""Risk Factor List - Extracts downside risks from equity research reports.

Lists specific downside risks identified by analysts including regulatory,
FX, supply chain, and other risk categories for risk monitoring.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class RiskItem(BaseModel):
    """
    A specific downside risk identified in equity research.
    """

    risk_name: str = Field(
        description="Concise name of the risk (e.g., 'Regulatory Tightening in EU', 'FX Headwinds from Strong Dollar')."
    )
    risk_category: str = Field(
        description="Category: 'Regulatory', 'Competitive', 'Macroeconomic', 'Operational', 'FX/Currency', "
        "'Geopolitical', 'Technology', 'Legal/Litigation', 'ESG', 'Execution'."
    )
    description: str = Field(
        description="Detailed description of the risk scenario."
    )
    potential_impact: Optional[str] = Field(
        None,
        description="Estimated financial impact (e.g., '3-5% revenue downside', '$0.50 EPS risk').",
    )
    probability: Optional[str] = Field(
        None,
        description="Analyst's probability assessment: 'High', 'Medium', 'Low'.",
    )
    time_horizon: Optional[str] = Field(
        None,
        description="When the risk could materialize (e.g., 'Near-term', '2025', '12-18 months').",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a risk analyst reviewing equity research reports. Extract all downside risks "
    "and risk factors identified by the analyst.\n\n"
    "Rules:\n"
    "- Extract every distinct risk factor mentioned.\n"
    "- Categorize each risk appropriately.\n"
    "- Capture quantified impact estimates when provided.\n"
    "- Note probability assessments and time horizons.\n"
    "- Extract EVERY risk independently as a separate item.\n\n"
    "### Source Text:\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class RiskFactorList(AutoList[RiskItem]):
    """
    Applicable to: Equity Research Reports (Risk Sections), Investment Committee Memos,
    Portfolio Risk Assessments, Analyst Downgrade Notes.

    Template for extracting downside risks from equity research. Each risk is captured
    as an independent list item for risk monitoring and portfolio risk assessment.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> risks = RiskFactorList(llm_client=llm, embedder=embedder)
        >>> report = "Key risks include: 1) EU Digital Markets Act compliance costs..."
        >>> risks.feed_text(report)
        >>> risks.show()
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
        Initialize the Risk Factor List template.

        Args:
            llm_client (BaseChatModel): The LLM for risk extraction.
            embedder (Embeddings): Embedding model for indexing.
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoList.
        """
        super().__init__(
            item_schema=RiskItem,
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
        Visualize the risk factor list.

        Args:
            top_k_for_search (int): Items for search. Default 3.
            top_k_for_chat (int): Items for chat context. Default 3.
        """

        def label_extractor(item: RiskItem) -> str:
            return f"[{item.risk_category}] {item.risk_name}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
