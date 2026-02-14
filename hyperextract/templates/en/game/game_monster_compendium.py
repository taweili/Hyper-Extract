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
    monster_type: str = Field(
        ...,
        description="Monster species/racial classification: 'Goblin', 'Dragon', 'Undead', 'Beast', etc.",
    )
    rarity_tier: Optional[str] = Field(
        None,
        description="Rarity level of the monster: 'Common', 'Elite', 'Boss', 'Legendary', etc.",
    )
    habitat: Optional[str] = Field(
        None, description="Map areas or regions where this monster typically appears"
    )
    combat_stats: Optional[str] = Field(
        None,
        description="Combat attributes with numerical values: HP, attack, defense, magic resist, etc.",
    )
    special_abilities: Optional[str] = Field(
        None,
        description="Unique skills or special attacks this monster can perform",
    )
    elemental_weakness: Optional[str] = Field(
        None,
        description="Element types this monster is weak to: Fire, Ice, Wind, Holy, Dark, etc.",
    )
    drop_table: Optional[str] = Field(
        None,
        description="Items dropped when defeated, including drop probability and item names",
    )
    respawn_timer: Optional[str] = Field(
        None, description="How long it takes for this monster to respawn after defeat"
    )
    encounter_difficulty: Optional[str] = Field(
        None, description="Recommended player level or difficulty assessment for encountering this monster"
    )


# ==============================================================================
# Extraction Prompt
# ==============================================================================

_PROMPT = """You are an expert game bestiary and monster guide author.
Your task is to extract structured information about game monsters from the provided text.

For each monster mentioned, extract:
1. **monster_name**: The official name of the monster
2. **monster_type**: The species or racial type of the monster
3. **rarity_tier**: How rare or powerful this monster is
4. **habitat**: Locations where this monster can be found
5. **combat_stats**: Numerical combat attributes (HP, ATK, DEF, etc.)
6. **special_abilities**: Unique or dangerous abilities this monster has
7. **elemental_weakness**: Element types that deal extra damage to this monster
8. **drop_table**: What items this monster drops and with what probability
9. **respawn_timer**: How long after defeat before the monster respawns
10. **encounter_difficulty**: Recommended player level or challenge rating

Extract only information explicitly mentioned. If a field is not described, leave it empty.
Be comprehensive in capturing all monster details, even if scattered throughout the text.

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
            type_label = f" ({item.monster_type})" if item.monster_type else ""
            return f"{item.monster_name}{type_label}"

        super().show(
            item_label_extractor=monster_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
