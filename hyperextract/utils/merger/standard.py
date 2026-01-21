"""Standard merge strategies for common use cases.

Provides ready-to-use merger implementations for typical merge scenarios:
- KeepNewMerger: Always keep the incoming item
- KeepOldMerger: Always keep the existing item
- FieldMerger: Merge at field level (Pydantic models)
"""

import logging
from typing import List, TypeVar
from .base import BaseMerger

try:
    from hyperextract.utils.logging import logger
except ImportError:
    logger = logging.getLogger(__name__)

T = TypeVar("T")


class KeepNewMerger(BaseMerger[T]):
    """Merger that always keeps the incoming (newer) item.

    Use case: When you want the most recent version of duplicate items.

    Example:
        >>> merger = KeepNewMerger(key_extractor=lambda x: x.id)
        >>> items = [Item(id=1, version=1), Item(id=1, version=2)]
        >>> merged = merger.merge(items)
        >>> # Result: [Item(id=1, version=2)]
    """

    def pair_merge(self, existing: T, incoming: T) -> T:
        """Keep the incoming item, discard the existing one.

        Args:
            existing: The existing item (will be discarded).
            incoming: The incoming item (will be kept).

        Returns:
            The incoming item.
        """
        return incoming


class KeepOldMerger(BaseMerger[T]):
    """Merger that always keeps the existing (older) item.

    Use case: When you want to preserve the first occurrence of duplicate items.

    Example:
        >>> merger = KeepOldMerger(key_extractor=lambda x: x.id)
        >>> items = [Item(id=1, version=1), Item(id=1, version=2)]
        >>> merged = merger.merge(items)
        >>> # Result: [Item(id=1, version=1)]
    """

    def pair_merge(self, existing: T, incoming: T) -> T:
        """Keep the existing item, discard the incoming one.

        Args:
            existing: The existing item (will be kept).
            incoming: The incoming item (will be discarded).

        Returns:
            The existing item.
        """
        return existing


class FieldMerger(BaseMerger[T]):
    """Merger that combines fields from both items (Pydantic models).

    Merge strategy:
        1. Start with incoming item as base
        2. Fill in None fields with existing item's non-None values
        3. Result: Most complete item with fields from both

    Requirements:
        - Items must be Pydantic BaseModel instances
        - Items must have compatible schemas

    Use case: Accumulating information across multiple extractions.

    Example:
        >>> from pydantic import BaseModel
        >>> class Person(BaseModel):
        ...     name: str
        ...     age: int | None = None
        ...     city: str | None = None
        >>>
        >>> merger = FieldMerger(key_extractor=lambda x: x.name)
        >>> items = [
        ...     Person(name="Alice", age=30, city=None),
        ...     Person(name="Alice", age=None, city="NYC"),
        ... ]
        >>> merged = merger.merge(items)
        >>> # Result: [Person(name="Alice", age=30, city="NYC")]
    """

    def pair_merge(self, existing: T, incoming: T) -> T:
        """Merge fields from both items, preferring non-None values.

        Strategy:
            - Start with incoming item
            - For each field in existing that is not None:
              - If incoming's field is None, use existing's value
              - Otherwise, keep incoming's value

        Args:
            existing: The existing item.
            incoming: The incoming item.

        Returns:
            Merged item with fields from both.

        Raises:
            AttributeError: If items are not Pydantic models.
        """
        try:
            # Use Pydantic's model_copy with update
            # existing.model_dump(exclude_none=True) gives all non-None fields
            # These values will override incoming's None fields
            return incoming.model_copy(update=existing.model_dump(exclude_none=True))
        except AttributeError as e:
            logger.error(
                f"FieldMerger requires Pydantic BaseModel instances. "
                f"Got types: {type(existing)}, {type(incoming)}. Error: {e}"
            )
            # Fallback to keep incoming
            return incoming
