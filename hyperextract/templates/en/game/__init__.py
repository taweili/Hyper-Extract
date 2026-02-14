"""Game domain templates for knowledge extraction."""

from .game_item_compendium import GameItemCompendium
from .game_character_compendium import GameCharacterCompendium
from .game_monster_compendium import GameMonsterCompendium
from .patch_note_changelog import PatchNoteChangelog
from .lore_faction_network import LoreFactionNetwork

__all__ = [
    "GameItemCompendium",
    "GameCharacterCompendium",
    "GameMonsterCompendium",
    "PatchNoteChangelog",
    "LoreFactionNetwork",
]
