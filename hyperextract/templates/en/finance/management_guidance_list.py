"""Management Guidance List - Extracts forward-looking statements from earnings calls.

Extracts projected figures, strategic priorities, and qualitative outlook from
management's forward guidance for tracking and expectation management.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class GuidanceItem(BaseModel):
    """
    A single forward-looking guidance statement from management.
    """

    guidance_topic: str = Field(
        description="Topic of the guidance (e.g., 'Q4 Revenue', 'FY2025 CapEx', 'Gross Margin Outlook', 'Hiring Plans')."
    )
    guidance_type: str = Field(
        description="Type: 'Quantitative', 'Qualitative', 'Strategic', 'Operational'."
    )
    guidance_value: str = Field(
        description="The guidance statement or projected value (e.g., '$95-97B', 'expanding into 5 new markets', "
        "'expect margin improvement in H2')."
    )
    prior_guidance: Optional[str] = Field(
        None,
        description="Previous guidance for the same metric if revised (e.g., '$90-93B').",
    )
    direction: Optional[str] = Field(
        None,
        description="Direction vs prior guidance or consensus: 'Raised', 'Lowered', 'Maintained', 'Initiated'.",
    )
    time_period: Optional[str] = Field(
        None,
        description="Period the guidance covers (e.g., 'Q4 2024', 'FY2025', 'Next 12 months').",
    )
    confidence_language: Optional[str] = Field(
        None,
        description="Management's conviction language (e.g., 'we expect', 'we are confident', 'we anticipate').",
    )
    speaker: Optional[str] = Field(
        None,
        description="Who provided the guidance (e.g., 'CEO', 'CFO', 'COO').",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an analyst tracking management guidance from earnings calls. "
    "Extract all forward-looking statements and guidance from this transcript.\n\n"
    "Rules:\n"
    "- Extract every distinct guidance item (quantitative figures, strategic plans, outlook statements).\n"
    "- Note if guidance was raised, lowered, or maintained vs. prior.\n"
    "- Capture the time period each guidance covers.\n"
    "- Preserve management's confidence language.\n"
    "- Identify who provided each guidance item.\n"
    "- Extract EVERY guidance statement independently.\n\n"
    "### Source Text:\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class ManagementGuidanceList(AutoList[GuidanceItem]):
    """
    Applicable to: Earnings Call Transcripts, Investor Day Presentations,
    Guidance Updates, Management Commentary sections.

    Template for extracting forward-looking guidance from earnings calls and
    management presentations. Each guidance item is captured independently
    for tracking revisions and managing expectations.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> guidance = ManagementGuidanceList(llm_client=llm, embedder=embedder)
        >>> transcript = "For Q4, we expect revenue in the range of $95-97 billion..."
        >>> guidance.feed_text(transcript)
        >>> guidance.show()
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
        Initialize the Management Guidance List template.

        Args:
            llm_client (BaseChatModel): The LLM for guidance extraction.
            embedder (Embeddings): Embedding model for indexing.
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoList.
        """
        super().__init__(
            item_schema=GuidanceItem,
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
        Visualize the management guidance list.

        Args:
            top_k_for_search (int): Items for search. Default 3.
            top_k_for_chat (int): Items for chat context. Default 3.
        """

        def label_extractor(item: GuidanceItem) -> str:
            direction = f" [{item.direction}]" if item.direction else ""
            return f"{item.guidance_topic}{direction}: {item.guidance_value[:50]}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
