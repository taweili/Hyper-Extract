from typing import List, Optional, Any, Callable
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class DiagnosticCriteria(BaseModel):
    """Diagnostic criteria and clinical classification for a disease."""
    disease_name: str = Field(description="Standardized name of the disease (e.g., 'Type 2 Diabetes', 'Acute Myocardial Infarction').")
    major_criteria: List[str] = Field(description="Core mandatory conditions or major diagnostic indicators.")
    minor_criteria: List[str] = Field(description="Supporting conditions or minor diagnostic indicators.")
    exclusion_criteria: List[str] = Field(description="Conditions that, if present, exclude the diagnosis.")
    biomarkers: List[str] = Field(description="Key laboratory findings or biomarkers (e.g., 'HbA1c > 6.5%').")
    source_guideline: str = Field(description="Source of this criteria, e.g., 'ADA 2024 Guidelines', 'WHO Classification'.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an expert in parsing clinical practice guidelines. Your task is to extract structured diagnostic criteria for specific diseases from medical literature.\n\n"
    "Extraction Principles:\n"
    "1. **Normalization**: Ensure all information for the same disease is aggregated under its standard medical name.\n"
    "2. **Strict Differentiation**: Clearly distinguish between 'Major Criteria', 'Minor Criteria', and 'Exclusion Criteria'.\n"
    "3. **Cumulative Information**: If criteria for the same disease is found in different parts of the text or across multiple sessions, merge them and list all sources in the source_guideline field.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class DiagnosticCriteriaSet(AutoSet[DiagnosticCriteria]):
    """
    Applicable to: [Clinical Practice Guidelines, Specialist Consensus, Medical Textbooks]

    Knowledge pattern for aggregating and maintaining diagnostic criteria libraries from medical guidelines.

    Leveraging AutoSet's key-accumulation feature, this template merges criteria from different 
    versions or organizations into a single, comprehensive reference for clinical use.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # Initialize template
        >>> criteria_lib = DiagnosticCriteriaSet(llm_client=llm, embedder=embedder)
        >>> # Feed guidelines from different sources
        >>> criteria_lib.feed_text("ADA 2024 states HbA1c > 6.5% for T2D.").feed_text("WHO notes fasting glucose remains a key criterion.")
        >>> criteria_lib.show()
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
        **kwargs: Any
    ):
        """
        Initialize DiagnosticCriteriaSet template.

        Args:
            llm_client: Language model client.
            embedder: Embeddings model for retrieval and visualization.
            chunk_size: Max characters per processing chunk.
            chunk_overlap: Overlap between chunks.
            max_workers: Parallel workers.
            verbose: Enable detailed logging.
            **kwargs: Extra arguments for AutoSet.
        """
        super().__init__(
            item_schema=DiagnosticCriteria,
            key_extractor=lambda x: x.disease_name.strip().lower(), # Matches disease name for normalization
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """
        Visualize the diagnostic criteria library.

        Args:
            top_k_for_search: Items for search.
            top_k_for_chat: Items for chat.
        """
        def item_label_extractor(item: DiagnosticCriteria) -> str:
            return item.disease_name

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
