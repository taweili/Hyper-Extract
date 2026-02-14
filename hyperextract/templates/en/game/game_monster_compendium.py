"""Game Monster Compendium - Extracts unique game monsters from various sources.

This template builds a comprehensive monster database by automatically merging
information from guides, wikis, and bestiary entries.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# Schema Definition
# ==============================================================================

class GameMonsterSchema(BaseModel):
    """Schema for individual game monsters in the compendium."""

    monster_name: str = Field(
        ..., description="The standard name of the monster, e.g., 'Goblin Warrior'"
    )
    type: str = Field(
        ...,
        description="Monster species and rarity classification (e.g., 'Undead / Boss', 'Beast / Common')",
    )
    habitat: Optional[str] = Field(
        None, description="Map areas or regions where this monster typically appears"
    )
    abilities: Optional[str] = Field(
        None,
        description="Combat stats (HP/ATK), special skills, weaknesses, and encounter difficulty",
    )
    loot_and_lore: Optional[str] = Field(
        None,
        description="Items dropped, respawn mechanics, and background lore/flavor text",
    )


# ==============================================================================
# Extraction Prompt
# ==============================================================================

_PROMPT = """You are an expert game bestiary and monster guide author.
Your task is to extract structured information about game monsters from the provided text.

For each monster mentioned, extract these consolidated fields:
1. **monster_name**: The official name of the monster
2. **type**: The species/race combined with rarity tier (e.g., Dragon/Legendary)
3. **habitat**: Locations where found
4. **abilities**: 
   - Combat stats (HP/ATK)
   - Unique skills or attacks
   - Elemental weaknesses
   - Strategy or difficulty rating
5. **loot_and_lore**:
   - Dropped items and probabilities
   - Respawn timers or mechanics
   - Background lore and description

Extract only information explicitly mentioned. Keep descriptions concise but complete.

### Source Text:
"""


# ==============================================================================
# Template Class
# ==============================================================================

class GameMonsterCompendium(AutoSet[GameMonsterSchema]):
    """Applicable to: Monster guides, Bestiary entries, Farming guides, Patch notes

    Extracts a comprehensive game monster database by automatically deduplicating
    and merging monster information from multiple sources.

    This template is particularly useful for:
    - Building unified monster databases from scattered wiki information
    - Merging monster data from multiple farming or hunting guides
    - Consolidating stat information and drop tables
    - Creating detailed monster profiles by combining data from multiple sources

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.en.game import GameMonsterCompendium
        >>>
        >>> llm = ChatOpenAI(model="gpt-4", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>>
        >>> monsters = GameMonsterCompendium(
        ...     llm_client=llm,
        ...     embedder=embedder
        ... )
        >>>
        >>> # Feed multiple sources
        >>> monsters.feed_text(
        ...     "The Goblin Warrior is a melee fighter with 150 HP and 45 attack power. "
        ...     "Found in the Dark Forest zone, they respawn every 5 minutes."
        ... )
        >>> monsters.feed_text(
        ...     "Goblin Warriors are weak to Fire damage. They can use Shield Bash and Cleave attacks."
        ... )
        >>> monsters.feed_text(
        ...     "When defeated, Goblin Warriors drop: Leather Armor (20% chance), "
        ...     "Iron Sword (5% chance), and Gold Coins (100%)."
        ... )
        >>>
        >>> # All info automatically merged into single Goblin Warrior profile
        >>> monsters.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        """Initialize the Game Monster Compendium template.

        Args:
            llm_client: Language model for monster extraction (e.g., ChatOpenAI).
            embedder: Embedding model for semantic indexing (e.g., OpenAIEmbeddings).
            chunk_size: Maximum characters per text chunk (default 2048).
            chunk_overlap: Overlapping characters between chunks (default 256).
            **kwargs: Additional arguments passed to AutoSet parent class.
        """
        super().__init__(
            item_schema=GameMonsterSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.monster_name.strip().lower(),
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
        """Display the game monster compendium as an interactive knowledge base.

        Args:
            top_k_for_search: Number of top results for semantic search.
            top_k_for_chat: Number of top results for chat context.
        """

        def monster_label_extractor(item: GameMonsterSchema) -> str:
            """Extract display label: name with type."""
            type_label = f" ({item.type})" if item.type else ""
            return f"{item.monster_name}{type_label}"

        super().show(
            item_label_extractor=monster_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
