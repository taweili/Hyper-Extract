"""Filing Risk Factor Set - Deduplicates and catalogs risk factors from SEC filings.

Extracts and normalizes risk factors disclosed in Item 1A of 10-K/10-Q filings,
tracking additions and removals between filing periods for risk evolution monitoring.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class RiskFactorItem(BaseModel):
    """
    A single risk factor disclosed in SEC filings.
    """

    risk_title: str = Field(
        description="Concise title of the risk factor (e.g., 'Cybersecurity Breach Risk', 'Foreign Currency Exposure')."
    )
    risk_category: str = Field(
        description="Category: 'Market', 'Operational', 'Regulatory', 'Financial', 'Strategic', 'Cybersecurity', 'ESG', 'Legal', 'Geopolitical'."
    )
    description: str = Field(
        description="Full description of the risk as disclosed in the filing."
    )
    potential_impact: Optional[str] = Field(
        None,
        description="Stated potential financial or operational impact (e.g., 'material adverse effect on revenue').",
    )
    affected_areas: Optional[List[str]] = Field(
        None,
        description="Business segments or functions affected (e.g., ['International Operations', 'Supply Chain']).",
    )
    mitigation_disclosed: Optional[str] = Field(
        None,
        description="Any mitigation measures or controls the company has disclosed.",
    )
    is_new: Optional[bool] = Field(
        None,
        description="Whether this risk factor appears to be newly added compared to prior filings.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a regulatory filing analyst specializing in risk disclosure analysis. "
    "Extract and catalog all individual risk factors from Item 1A (Risk Factors) or equivalent "
    "risk disclosure sections of SEC filings.\n\n"
    "Extraction Principles:\n"
    "1. **Normalization**: Aggregate related risk language under a single concise risk title.\n"
    "2. **Categorization**: Classify each risk into its primary category.\n"
    "3. **Completeness**: Extract every distinct risk factor, even if briefly mentioned.\n"
    "4. **Cumulative**: If the same risk appears with additional detail across sections, merge the information."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class FilingRiskFactorSet(AutoSet[RiskFactorItem]):
    """
    Applicable to: SEC 10-K Item 1A (Risk Factors), 10-Q Risk Factor updates,
    S-1 Prospectus Risk Sections, 20-F Risk Disclosures.

    Template for building a deduplicated registry of risk factors from regulatory filings.
    Leverages AutoSet's key-accumulation to merge risk disclosures from different sections
    or filing periods into a comprehensive risk catalog.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> risk_set = FilingRiskFactorSet(llm_client=llm, embedder=embedder)
        >>> filing = "Item 1A. Risk Factors: We face significant cybersecurity risks..."
        >>> risk_set.feed_text(filing)
        >>> risk_set.show()
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
        Initialize the Filing Risk Factor Set template.

        Args:
            llm_client (BaseChatModel): The LLM for risk factor extraction.
            embedder (Embeddings): Embedding model for retrieval.
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoSet.
        """
        super().__init__(
            item_schema=RiskFactorItem,
            key_extractor=lambda x: x.risk_title.strip().lower(),
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
        Visualize the risk factor registry.

        Args:
            top_k_for_search (int): Items for search. Default 3.
            top_k_for_chat (int): Items for chat context. Default 3.
        """

        def item_label_extractor(item: RiskFactorItem) -> str:
            return f"[{item.risk_category}] {item.risk_title}"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
