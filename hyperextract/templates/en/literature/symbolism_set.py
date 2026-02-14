from typing import List, Optional, Any, Callable
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class ImagerySymbol(BaseModel):
    """An image or symbol in a literary work."""
    symbol_name: str = Field(description="The name of the symbol/image (e.g., 'The Ocean', 'The Red Room', 'The Mockingbird').")
    literal_meanings: List[str] = Field(description="Literal references or descriptions of the image in the text.")
    metaphorical_meanings: List[str] = Field(description="Implicit symbolic meanings or deep metaphors associated with the image.")
    contexts: List[str] = Field(description="Key textual snippets or chapter summaries where the symbol appears.")
    thematic_connection: Optional[str] = Field(description="The connection between the symbol and the overall themes of the work.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an expert literary critic. Your task is to identify and analyze recurring imagery and symbols within the text.\n\n"
    "Analysis Guidelines:\n"
    "1. **Normalization**: Ensure that variations of the same symbol (e.g., 'moonlight' and 'the moon') are grouped under a single standard symbol name to allow for information accumulation.\n"
    "2. **Layered Interpretation**: Distinguish between the literal description of the image and its symbolic significance.\n"
    "3. **Synthesis**: If a symbol appears in multiple parts of the text, continuously enrich its entry with new layers of meaning, context, and thematic significance.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class SymbolismSet(AutoSet[ImagerySymbol]):
    """
    Applicable to: [Poetry, Modernist Novels, Literary Criticism, Essays]

    Knowledge pattern for aggregating and deeply analyzing literary imagery and symbols.

    Leveraging AutoSet's key-accumulation mechanism, this template automatically merges information 
    about the same symbol (literal descriptions, metaphors, thematic links) from across the entire work into a single enriched entry.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # Initialize template
        >>> symbolism = SymbolismSet(llm_client=llm, embedder=embedder)
        >>> # Feed text from different chapters
        >>> symbolism.feed_text("The green light at the end of the dock symbolizes Gatsby's hopes and dreams.")
        >>> symbolism.feed_text("Gatsby reached out towards the green light, representing the unattainable past.")
        >>> symbolism.show()
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
        Initialize SymbolismSet template.

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
            item_schema=ImagerySymbol,
            key_extractor=lambda x: x.symbol_name.strip().lower(), # Exact key match for normalization
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
        Visualize the symbolism and imagery repository.

        Args:
            top_k_for_search: Items to retrieve for search.
            top_k_for_chat: Items to retrieve for chat.
        """
        def item_label_extractor(item: ImagerySymbol) -> str:
            return item.symbol_name

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
