"""Proceeds Usage - Extracts fund allocation details from prospectuses.

Extracts project names, allocated amounts, and estimated timelines for IPO
proceeds or debt offering fund usage for post-IPO monitoring.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class ProceedsItem(BaseModel):
    """
    A single use-of-proceeds allocation item.
    """

    use_category: str = Field(
        description="Category of fund usage (e.g., 'R&D Investment', 'Debt Repayment', 'Working Capital', "
        "'Acquisitions', 'Capital Expenditures', 'General Corporate Purposes')."
    )
    project_name: Optional[str] = Field(
        None,
        description="Specific project or initiative name (e.g., 'New Data Center in Virginia', 'Platform 2.0 Development').",
    )
    allocated_amount: Optional[str] = Field(
        None,
        description="Amount allocated (e.g., '$150 million', 'approximately 30% of net proceeds').",
    )
    percentage_of_proceeds: Optional[str] = Field(
        None,
        description="Percentage of total proceeds (e.g., '30%', 'approximately one-third').",
    )
    timeline: Optional[str] = Field(
        None,
        description="Expected deployment timeline (e.g., '12-18 months', 'FY2025-2026').",
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of how funds will be used.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an IPO analyst. Extract all use-of-proceeds allocations from this prospectus "
    "or offering document.\n\n"
    "Rules:\n"
    "- Extract every distinct fund usage category and specific project.\n"
    "- Capture allocated amounts and percentages.\n"
    "- Extract deployment timelines when stated.\n"
    "- Preserve detailed descriptions of how funds will be used.\n"
    "- Extract EVERY allocation independently as a separate item.\n\n"
    "### Source Text:\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class ProceedsUsage(AutoList[ProceedsItem]):
    """
    Applicable to: S-1 Prospectuses (Use of Proceeds section), Debt Offering Memoranda,
    Secondary Offering Prospectuses, SPAC Proxy Statements.

    Template for extracting fund allocation details from prospectuses and offering
    documents. Each allocation is captured as an independent item for post-IPO
    monitoring and proceeds tracking.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> proceeds = ProceedsUsage(llm_client=llm, embedder=embedder)
        >>> prospectus = "We intend to use approximately $150M for R&D, $100M for debt repayment..."
        >>> proceeds.feed_text(prospectus)
        >>> proceeds.show()
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
        Initialize the Proceeds Usage template.

        Args:
            llm_client (BaseChatModel): The LLM for proceeds extraction.
            embedder (Embeddings): Embedding model for indexing.
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoList.
        """
        super().__init__(
            item_schema=ProceedsItem,
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
        Visualize the proceeds usage list.

        Args:
            top_k_for_search (int): Items for search. Default 3.
            top_k_for_chat (int): Items for chat context. Default 3.
        """

        def label_extractor(item: ProceedsItem) -> str:
            amount = f": {item.allocated_amount}" if item.allocated_amount else ""
            return f"{item.use_category}{amount}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
