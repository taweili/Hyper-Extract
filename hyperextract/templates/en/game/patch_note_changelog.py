"""Patch Note Changelog - Extracts all individual changes from patch notes.

This template extracts a comprehensive changelog of all game changes, modifications,
and balance updates without deduplication, preserving every individual change entry.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList

# ==============================================================================
# Schema Definition
# ==============================================================================

class PatchChangeSchema(BaseModel):
    """Schema for individual patch note entries."""

    entity_name: str = Field(
        ..., description="Name of the entity modified: character name, item name, etc."
    )
    change_type: str = Field(
        ...,
        description="Type of change: 'Buff' (increase), 'Nerf' (decrease), 'Mechanic Change', 'Bug Fix', 'Rework', etc.",
    )
    old_value: Optional[str] = Field(
        None, description="Previous value or state before modification"
    )
    new_value: Optional[str] = Field(
        None, description="New value or state after modification"
    )
    patch_version: Optional[str] = Field(
        None, description="Version number or patch date when this change took effect"
    )
    developer_note: Optional[str] = Field(
        None, description="Official explanation or reasoning for the change provided by developers"
    )


# ==============================================================================
# Extraction Prompt
# ==============================================================================

_PROMPT = """You are an expert patch note analyst and game balance specialist.
Your task is to extract detailed information about each individual game change from patch notes.

For each change or modification mentioned, extract:
1. **entity_name**: What is being modified (character, item, ability, system, etc.)
2. **change_type**: The nature of the change (Buff, Nerf, Mechanic Change, Bug Fix, Rework, etc.)
3. **old_value**: The previous value, stat, or mechanic before the change
4. **new_value**: The new value, stat, or mechanic after the change
5. **patch_version**: The patch version or date when this change was implemented
6. **developer_note**: Any explanation or reasoning provided for the change

CRITICAL: Extract EVERY individual change as a separate entry. 
If an entity has multiple changes in a patch (e.g., both attack nerfed AND defense buffed),
create separate entries for each change to preserve complete change history.

Extract only information explicitly mentioned in the text.
Be comprehensive and capture all modifications, no matter how minor.

### Source Text:
"""


# ==============================================================================
# Template Class
# ==============================================================================

class PatchNoteChangelog(AutoList[PatchChangeSchema]):
    """Applicable to: Official patch notes, Version changelogs, Balance updates

    Extracts a detailed changelog of all game modifications from patch documentation.

    Unlike AutoSet which deduplicates, this template preserves EVERY individual change
    as a separate entry. This is essential for:
    - Tracking complete balance history of each entity
    - Analyzing multiple changes to the same entity in one patch
    - Auditing game design decisions over time
    - Building comprehensive patch databases without data loss

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.en.game import PatchNoteChangelog
        >>>
        >>> llm = ChatOpenAI(model="gpt-4", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>>
        >>> changelog = PatchNoteChangelog(
        ...     llm_client=llm,
        ...     embedder=embedder
        ... )
        >>>
        >>> # Feed patch notes
        >>> changelog.feed_text('''
        ... Patch 2.3.0 - Balance Update
        ... Yasuo: Attack increased from 50 to 55 (buff to late-game scaling)
        ... Yasuo: Wind Wall cooldown reduced from 25s to 20s (quality of life)
        ... Endless Blade: Attack bonus increased from 80 to 85
        ... ''')
        >>>
        >>> # Each change is preserved as separate entry, not merged
        >>> # So we get 3 entries total, even though Yasuo has 2 changes
        >>> changelog.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        """Initialize the Patch Note Changelog template.

        Args:
            llm_client: Language model for change extraction (e.g., ChatOpenAI).
            embedder: Embedding model for semantic indexing (e.g., OpenAIEmbeddings).
            chunk_size: Maximum characters per text chunk (default 2048).
            chunk_overlap: Overlapping characters between chunks (default 256).
            **kwargs: Additional arguments passed to AutoList parent class.
        """
        super().__init__(
            item_schema=PatchChangeSchema,
            llm_client=llm_client,
            embedder=embedder,
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
        """Display the patch changelog as an interactive database.

        Args:
            top_k_for_search: Number of top results for semantic search.
            top_k_for_chat: Number of top results for chat context.
        """

        def change_label_extractor(item: PatchChangeSchema) -> str:
            """Extract display label: entity with change type."""
            return f"{item.entity_name} ({item.change_type})"

        super().show(
            item_label_extractor=change_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
