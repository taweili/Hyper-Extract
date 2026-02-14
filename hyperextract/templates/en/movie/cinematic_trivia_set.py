from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class CinematicTrivia(BaseModel):
    """Film elements, easter eggs, production trivia, or specific narrative elements."""
    topic: str = Field(description="The theme or name of the trivia/element (e.g., 'Homage to 2001: A Space Odyssey', 'Fourth Wall Break').")
    description: str = Field(description="Detailed content or production background of the element.")
    timestamp: Optional[str] = Field(description="Specific time point in the film where the element appears (e.g., '01:23:45').")
    significance: List[str] = Field(description="Artistic significance, narrative function, or special meaning to fans.")
    source: List[str] = Field(description="Source of the information (e.g., Director's Commentary, IMDb, specific trivia sites).")

# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an expert film critic and cinema encyclopedist. Your task is to extract structured film trivia and encyclopedic points from reviews and production notes.\n\n"
    "Analysis Guidelines:\n"
    "1. **Topic Deduplication**: Merge multiple snippets regarding the same topic (e.g., 'Stan Lee Cameo'). Ensure standardized naming.\n"
    "2. **Deep Dive**: Extract not just 'what' the element is, but also the artistic intent (significance) behind it.\n"
    "3. **Accumulation**: Enrich the same topic with descriptions, timestamps, and sources over multiple text feeds.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class CinematicTriviaSet(AutoSet[CinematicTrivia]):
    """
    Applicable to: [Production Notes, DVD Commentary, Behind-the-scenes, IMDB Trivia, Film Reviews]

    Template for building and aggregating film encyclopedias and trivia.

    This template leverages AutoSet's enrichment capabilities to aggregate scattered trivia knowledge across documents.

    Example:
        >>> trivia = CinematicTriviaSet(llm_client=llm, embedder=embedder)
        >>> trivia.feed_text("The director placed a hidden homage to Kubrick at 86 minutes.").feed_text("The red chair is a direct nod to The Shining.")
        >>> trivia.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        chunk_size: int = 2048,
        **kwargs: Any
    ):
        super().__init__(
            item_schema=CinematicTrivia,
            key_extractor=lambda x: x.topic.strip().lower(),
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            **kwargs
        )

    def show(self, **kwargs):
        def label(item: CinematicTrivia) -> str: return item.topic
        super().show(item_label_extractor=label, **kwargs)
