"""Game Character Compendium - Extracts unique game characters from various sources.

This template builds a comprehensive character encyclopedia by automatically
merging information from multiple sources: official lore, strategy guides,
character guides, and patch notes.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# Schema Definition
# ==============================================================================

class GameCharacterSchema(BaseModel):
    """Schema for individual game characters in the compendium."""

    character_name: str = Field(
        ..., description="The standard name of the character, e.g., 'Yasuo'"
    )
    character_class: str = Field(
        ...,
        description="Character class/role: 'Swordsman', 'Mage', 'Archer', 'Tank', 'Support', etc.",
    )
    background_story: Optional[str] = Field(
        None, description="Character lore, origin story, and background"
    )
    signature_abilities: Optional[str] = Field(
        None,
        description="List of main/signature skills and abilities this character possesses",
    )
    base_stats: Optional[str] = Field(
        None,
        description="Base attributes: HP, mana, attack, defense, speed, etc. with numerical values",
    )
    recommended_playstyle: Optional[str] = Field(
        None,
        description="How to effectively play this character: positioning, combos, item builds, etc.",
    )
    origin_region: Optional[str] = Field(
        None, description="The region/world area this character comes from"
    )
    faction_affiliation: Optional[str] = Field(
        None, description="Which faction, team, or organization this character belongs to"
    )
    voice_actor: Optional[str] = Field(
        None,
        description="Official voice actor name(s) for this character in different languages",
    )


# ==============================================================================
# Extraction Prompt
# ==============================================================================

_PROMPT = """You are an expert game lore specialist and character guide author.
Your task is to extract comprehensive information about game characters from the provided text.

For each character mentioned, extract:
1. **character_name**: The official name of the character
2. **character_class**: The combat role/class of the character
3. **background_story**: Origin story, lore, and character background
4. **signature_abilities**: Main and special abilities/skills this character has
5. **base_stats**: Core numerical attributes: HP, mana, attack power, defense, etc.
6. **recommended_playstyle**: Strategic guidance on how to effectively play this character
7. **origin_region**: Which region or world area the character is from
8. **faction_affiliation**: Which team, organization, or faction the character belongs to
9. **voice_actor**: The official voice actor's name(s) if mentioned

Extract only information explicitly stated in the text. If a field is not mentioned, leave it empty.
Be comprehensive and capture all character details mentioned, even if scattered across the text.

### Source Text:
"""


# ==============================================================================
# Template Class
# ==============================================================================

class GameCharacterCompendium(AutoSet[GameCharacterSchema]):
    """Applicable to: Character background stories, Skill guides, Official character bio, Strategy guides

    Extracts a comprehensive game character encyclopedia by automatically
    deduplicating and merging character information from multiple sources.

    Information about the same character from different sources (official lore,
    strategy guides, patch notes) is automatically combined into a single
    enriched character profile.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.en.game import GameCharacterCompendium
        >>>
        >>> llm = ChatOpenAI(model="gpt-4", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>>
        >>> characters = GameCharacterCompendium(
        ...     llm_client=llm,
        ...     embedder=embedder
        ... )
        >>>
        >>> # Feed multiple sources
        >>> characters.feed_text(
        ...     "Yasuo was a swordsman of great honor from the Ionian isles. "
        ...     "He wields a blade with unmatched precision and speed."
        ... )
        >>> characters.feed_text(
        ...     "Yasuo's abilities include: Steel Tempest (Q), Wind Wall (W), Sweeping Blade (E), Last Breath (R). "
        ...     "Stats: 550 HP, 50 attack, 25 armor."
        ... )
        >>> characters.feed_text(
        ...     "As an ADC (attack-carry), Yasuo works best with items that increase attack speed "
        ...     "and critical chance. Position carefully in teamfights."
        ... )
        >>>
        >>> # All info automatically merged into single Yasuo profile
        >>> characters.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        """Initialize the Game Character Compendium template.

        Args:
            llm_client: Language model for character extraction (e.g., ChatOpenAI).
            embedder: Embedding model for semantic indexing (e.g., OpenAIEmbeddings).
            chunk_size: Maximum characters per text chunk (default 2048).
            chunk_overlap: Overlapping characters between chunks (default 256).
            **kwargs: Additional arguments passed to AutoSet parent class.
        """
        super().__init__(
            item_schema=GameCharacterSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.character_name.strip().lower(),
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
        """Display the game character compendium as an interactive knowledge graph.

        Args:
            top_k_for_search: Number of top results for semantic search.
            top_k_for_chat: Number of top results for chat context.
        """

        def character_label_extractor(item: GameCharacterSchema) -> str:
            """Extract display label: name with class."""
            class_label = f" ({item.character_class})" if item.character_class else ""
            return f"{item.character_name}{class_label}"

        super().show(
            item_label_extractor=character_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
