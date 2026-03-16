"""Display parser - generates label extraction functions from YAML config."""

from typing import Any, Callable

from .schemas import (
    VALID_AUTOTYPES,
    NaiveDisplaySchema,
    GraphDisplaySchema,
)
from .identifiers import _extractor


def parse_display(
    display: NaiveDisplaySchema | GraphDisplaySchema | None,
    autotype: VALID_AUTOTYPES,
) -> Callable[[Any], str] | tuple[Callable[[Any], str], Callable[[Any], str]] | None:
    """Parse display config and return label extractors.

    Args:
        display: display config from YAML
        autotype: auto type

    Returns:
        - For model/list/set: label_extractor
        - For graph types: (entity_label_extractor, relation_label_extractor)
    """
    if not display:
        return None

    if autotype in ("model", "list", "set"):
        return _extractor(display.label)

    entity_extractor = _extractor(display.entity_label)
    relation_extractor = _extractor(display.relation_label)
    return (entity_extractor, relation_extractor)


__all__ = [
    "parse_display",
]
