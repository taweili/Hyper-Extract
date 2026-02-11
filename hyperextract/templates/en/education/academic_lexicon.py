from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class AcademicTerm(BaseModel):
    """
    A standardized academic term, concept, or definition aggregated from multiple sources.
    """

    term: str = Field(
        description="The primary name of the academic term/concept. Acts as the unique identifier."
    )
    domain: str = Field(
        description="Field of study or academic domain (e.g., 'Thermodynamics', 'Linguistics')."
    )
    definition: str = Field(
        description="A comprehensive, synthesized definition of the term."
    )
    synonyms: List[str] = Field(
        default_factory=list, description="Alternative names or closely related terms."
    )
    key_expression: Optional[str] = Field(
        None,
        description="A formula, notation, or iconic expression associated with this term.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

ACADEMIC_LEXICON_PROMPT = (
    "You are a Lexicographer and Academic Encyclopedia Editor. Your goal is to extract standardize academic definitions.\n\n"
    "Extraction Rules:\n"
    "- Identify unique academic terms and their highly precise definitions.\n"
    "- Search for alternative names or synonyms within the text.\n"
    "- If multiple descriptions of the same term exist, prioritize the one that is most mathematically or logically rigorous."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class AcademicLexiconSet(AutoSet[AcademicTerm]):
    """
    Educational template for building a deduplicated, synthesized dictionary of academic terms.
    Leverages AutoSet to merge conflicting or complementary definitions from multiple text sources.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.en.education.academic_lexicon import AcademicLexiconSet
        >>> lexicon = AcademicLexiconSet(llm_client, embedder)
        >>> lexicon.feed_text("Source 1: Photosynthesis is a process used by plants...")
        >>> lexicon.feed_text("Source 2: Photosynthesis converts light energy into chemical energy...")
        >>> lexicon.extract() # Will merge definitions of "Photosynthesis"
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",  # For AutoSet, this is standard
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize the Academic Lexicon Template.

        Args:
            llm_client (BaseChatModel): The LLM used for extraction.
            embedder (Embeddings): The embedding model for entity deduplication and merging.
            extraction_mode (str): Mode of extraction.
            chunk_size (int): Size of text chunks for processing large documents.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable verbose logging.
            **kwargs: Additional parameters for AutoSet.
        """
        super().__init__(
            item_schema=AcademicTerm,
            key_extractor=lambda x: x.term.strip().lower(),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=ACADEMIC_LEXICON_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """
        Visualize the collection using OntoSight.

        Args:
            top_k_for_search (int): Number of items to retrieve for search context. Default 3.
            top_k_for_chat (int): Number of items to retrieve for chat context. Default 3.
        """

        def item_label_extractor(item: AcademicTerm) -> str:
            return f"{item.term}"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
