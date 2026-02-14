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
        ..., description="The standard English or localized name of the item"
    )
    category: str = Field(
        ...,
        description="Item classification: 'Weapon', 'Armor', 'Consumable', 'Accessory', 'Material', etc.",
    )
    stat_bonuses: Optional[str] = Field(
        None,
        description="Attribute bonuses provided by this item, e.g., '+50 attack, +100 HP'",
    )
    crafting_recipe: Optional[str] = Field(
        None, description="How to craft this item from other materials or items"
    )
    drop_sources: Optional[str] = Field(
        None,
        description="Where to obtain this item: which monsters drop it, NPCs who sell it, quest rewards, etc.",
    )
    suitable_heroes: Optional[str] = Field(
        None, description="Which character classes or heroes benefit most from this item"
    )
    lore_background: Optional[str] = Field(
        None, description="The gameplay lore or in-world story of this item"
    )


# ==============================================================================
# Extraction Prompt
# ==============================================================================

_PROMPT = """You are an expert game designer and community guide author familiar with game item systems.
Your task is to extract structured information about game items from the provided text.

For each item mentioned in the text, extract:
1. **item_name**: The official or standard name of the item
2. **category**: The type/class of item (weapon, armor, consumable, etc.)
3. **stat_bonuses**: Any attribute, damage, defense, or status effect bonuses this item provides
4. **crafting_recipe**: How players can craft or combine items to create this item
5. **drop_sources**: Where/who drops this item, shops that sell it, quest rewards, etc.
6. **suitable_heroes**: Which character classes or heroes are recommended to use this item
7. **lore_background**: Any in-game story, legend, or lore associated with this item

Extract only information explicitly mentioned in the text. If a field is not described, leave it empty.
Focus on being comprehensive and capturing all items mentioned, even if only briefly.

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
