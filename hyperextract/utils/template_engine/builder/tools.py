"""Data model summary - convenient for code hints and intuitive viewing"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel


class GuidelineSchema(BaseModel):
    """Extraction guideline configuration"""

    # [all] AutoModel, AutoList, AutoSet, AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    target: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None

    # [non-graph] AutoModel, AutoList, AutoSet
    rules: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None

    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    rules_for_entities: Optional[
        Union[str, List[str], Dict[str, Union[str, List[str]]]]
    ] = None

    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    rules_for_relations: Optional[
        Union[str, List[str], Dict[str, Union[str, List[str]]]]
    ] = None

    # [temporal] AutoTemporalGraph, AutoSpatioTemporalGraph
    rules_for_time: Optional[
        Union[str, List[str], Dict[str, Union[str, List[str]]]]
    ] = None

    # [spatial] AutoSpatialGraph, AutoSpatioTemporalGraph
    rules_for_location: Optional[
        Union[str, List[str], Dict[str, Union[str, List[str]]]]
    ] = None


class FieldSchema(BaseModel):
    """Field definition"""

    # [all]
    name: str
    type: str
    description: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None


class OutputSchema(BaseModel):
    """Output definition"""

    description: Optional[str] = None

    # [non-graph] AutoModel, AutoList, AutoSet
    fields: Optional[List[FieldSchema]] = None

    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    entities: Optional[List[FieldSchema]] = None

    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    relations: Optional[List[FieldSchema]] = None


class OptionsSchema(BaseModel):
    """Runtime options"""

    # [non-graph] AutoModel, AutoSet
    merge_strategy: Optional[str] = None

    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    entity_merge_strategy: Optional[str] = None

    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    relation_merge_strategy: Optional[str] = None

    extraction_mode: Optional[str] = None

    # [temporal] AutoTemporalGraph, AutoSpatioTemporalGraph
    observation_time: Optional[str] = None

    # [spatial] AutoSpatialGraph, AutoSpatioTemporalGraph
    observation_location: Optional[str] = None

    # [all]
    chunk_size: int = 2048
    chunk_overlap: int = 256
    max_workers: int = 10
    verbose: bool = False
    fields_for_search: Optional[List[str]] = None
    entity_fields_for_search: Optional[List[str]] = None
    relation_fields_for_search: Optional[List[str]] = None


class DisplaySchema(BaseModel):
    """Display configuration"""

    # [non-graph] AutoModel, AutoList, AutoSet
    label: Optional[str] = None

    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    entity_label: Optional[str] = None

    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    relation_label: Optional[str] = None


class IdentifiersSchema(BaseModel):
    """Identifier configuration"""

    # [non-graph] AutoSet
    item_id: Optional[str] = None

    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    entity_id: Optional[str] = None

    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    relation_id: Optional[str] = None

    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    relation_members: Optional[Dict[str, str]] = None

    # [temporal] AutoTemporalGraph, AutoSpatioTemporalGraph
    time_field: Optional[str] = None

    # [spatial] AutoSpatialGraph, AutoSpatioTemporalGraph
    location_field: Optional[str] = None


class TemplateSchema(BaseModel):
    """Template configuration - corresponds to YAML configuration file"""

    language: str | List[str] = "en"
    name: str
    type: str
    tags: List[str]
    description: Optional[str] = None
    output: Optional[OutputSchema] = None
    guideline: Optional[GuidelineSchema] = None
    identifiers: Optional[IdentifiersSchema] = None
    options: Optional[OptionsSchema] = None
    display: Optional[DisplaySchema] = None


def get_text(
    value: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]],
    language: Optional[str] = None,
) -> Optional[str]:
    """Get multilingual text value, supports list format."""
    if value is None:
        return None
    elif isinstance(value, str):
        return value
    elif isinstance(value, list):
        return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(value))
    else:
        # multi-language dict
        dict_value = value.get(language)
        if isinstance(dict_value, str):
            return dict_value
        if isinstance(dict_value, list):
            return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(dict_value))


__all__ = [
    "get_text",
    "GuidelineSchema",
    "FieldSchema",
    "OutputSchema",
    "OptionsSchema",
    "DisplaySchema",
    "IdentifiersSchema",
    "TemplateSchema",
]
