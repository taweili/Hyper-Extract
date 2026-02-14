"""Game Item Compendium - Extracts unique game items from various sources.

This template builds a comprehensive item library by automatically merging
information about the same item from multiple sources (guides, wikis, patch notes).
Uses AutoSet to deduplicate and combine item attributes.

Example Sources:
- Game Wiki pages describing item properties
- Official strategy guides with item recommendations
- Patch notes mentioning item changes
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# Schema Definition
# ==============================================================================

class GameItemSchema(BaseModel):
    """Schema for individual game items in the compendium."""

    item_name: str = Field(
        ..., description="The standard name of the item"
    )
    category: str = Field(
        ...,
        description="Item classification (Weapon, Potion, Material, etc.)",
    )
    item_data: Optional[str] = Field(
        None,
        description="Stat bonuses, special effects, and crafting recipe information.",
    )
    description: Optional[str] = Field(
        None, description="Acquisition info, suitable heroes, and lore background.",
    )


# ==============================================================================
# Extraction Prompt
# ==============================================================================

_PROMPT = """You are an expert game designer and community guide author familiar with game item systems.
Your task is to extract structured information about game items from the provided text.

For each item mentioned in the text, extract:
1. **item_name**: The official or standard name of the item
2. **category**: The type/class of item (weapon, armor, consumable, etc.)
3. **item_data**: Stat bonuses, effects, and crafting recipes
4. **description**: Where to find it, recommended heroes, and background lore

Extract only information explicitly mentioned.

### Source Text:
"""


# ==============================================================================
# Template Class
# ==============================================================================

class GameItemCompendium(AutoSet[GameItemSchema]):
    """Applicable to: Game Wiki pages, Strategy guides, Official item manuals, Patch notes

    Extracts a comprehensive game item compendium by automatically deduplicating
    and merging information about items from multiple sources.

    This template is particularly useful for:
    - Building unified item databases from scattered wiki information
    - Merging item data from different strategy guides and patch notes
    - Consolidating character recommendations and item synergies
    - Creating rich item profiles by combining properties from multiple sources

    When multiple text chunks describe the same item (identified by exact name matching),
    their attributes are intelligently merged into a single enriched entry. This allows
    gradual knowledge accumulation about each item across multiple documents.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.en.game import GameItemCompendium
        >>>
        >>> llm = ChatOpenAI(model="gpt-4", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>>
        >>> compendium = GameItemCompendium(
        ...     llm_client=llm,
        ...     embedder=embedder
        ... )
        >>>
        >>> # Feed multiple sources
        >>> compendium.feed_text(
        ...     "Endless Blade is a legendary weapon that grants +80 attack power. "
        ...     "It can be crafted by combining a Long Sword and a Crystal Core."
        ... )
        >>> compendium.feed_text(
        ...     "Endless Blade synergizes perfectly with Yasuo and Aatrox, "
        ...     "enabling powerful critical strike combos with these champions."
        ... )
        >>> compendium.feed_text(
        ...     "The Endless Blade has a dark lore: forged from the tears "
        ...     "of a fallen god to prevent the eternal night."
        ... )
        >>>
        >>> # All information is automatically merged under 'Endless Blade'
        >>> compendium.show()  # Visualize the merged item compendium
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        """Initialize the Game Item Compendium template.

        Args:
            llm_client: Language model for item extraction (e.g., ChatOpenAI).
            embedder: Embedding model for semantic indexing (e.g., OpenAIEmbeddings).
            chunk_size: Maximum characters per text chunk (default 2048).
            chunk_overlap: Overlapping characters between chunks (default 256).
            **kwargs: Additional arguments passed to AutoSet parent class.
        """
        super().__init__(
            item_schema=GameItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.item_name.strip().lower(),
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """Display the game item compendium as an interactive knowledge graph.

        Args:
            top_k_for_search: Number of top results to retrieve for semantic search queries.
            top_k_for_chat: Number of top results to show in chat/dialogue context.
        """

        def item_label_extractor(item: GameItemSchema) -> str:
            """Extract display label for an item: name with category."""
            category_label = f" ({item.category})" if item.category else ""
            return f"{item.item_name}{category_label}"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
