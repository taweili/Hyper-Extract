"""Config loader and template configuration models."""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Literal, Union
from pydantic import BaseModel, Field


VALID_MERGE_STRATEGIES = Literal[
    "merge_field",
    "keep_incoming",
    "keep_existing",
    "llm_balanced",
    "llm_prefer_incoming",
    "llm_prefer_existing",
]


def parse_multi_lang(
    value: str | List[str] | Dict[str, str | List[str]],
    language: str,
) -> str:
    """Get multilingual text value, supports list format."""
    if isinstance(value, str):
        return value
    elif isinstance(value, list):
        return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(value))
    else:
        dict_value = value.get(language)
        if isinstance(dict_value, str):
            return dict_value
        if isinstance(dict_value, list):
            return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(dict_value))


class GuidelineSchema(BaseModel):
    """Extraction guideline configuration"""

    target: str | List[str] | Dict[str, str | List[str]]
    rules: str | List[str] | Dict[str, str | List[str]] | None = None
    rules_for_entities: str | List[str] | Dict[str, str | List[str]] | None = None
    rules_for_relations: str | List[str] | Dict[str, str | List[str]] | None = None
    rules_for_time: str | List[str] | Dict[str, str | List[str]] | None = None
    rules_for_location: str | List[str] | Dict[str, str | List[str]] | None = None


class FieldSchema(BaseModel):
    """Field definition"""

    name: str
    type: str
    description: str | Dict[str, str]
    required: bool = False
    default: Any | None = None


class OutputUnitSchema(BaseModel):
    """Output unit schema"""

    description: str | Dict[str, str]
    fields: List[FieldSchema] = Field(default_factory=list)

class NaiveOutputSchema(BaseModel):
    """Naive output schema"""

    description: str | Dict[str, str]
    fields: List[FieldSchema] = Field(default_factory=list)

class GraphOutputSchema(BaseModel):
    """Graph output schema"""

    description: str | Dict[str, str]
    entities: OutputUnitSchema
    relations: OutputUnitSchema

class OptionsSchema(BaseModel):
    """Runtime options"""

    chunk_size: int = 2048
    chunk_overlap: int = 256
    max_workers: int = 10
    verbose: bool = False
    # [non-graph] AutoModel, AutoList, AutoSet
    merge_strategy: VALID_MERGE_STRATEGIES = "llm_balanced"
    fields_for_search: List[str] | None = None
    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    entity_merge_strategy: VALID_MERGE_STRATEGIES = "llm_balanced"
    relation_merge_strategy: VALID_MERGE_STRATEGIES = "llm_balanced"
    extraction_mode: str | None = None
    entity_fields_for_search: List[str] | None = None
    relation_fields_for_search: List[str] | None = None
    # [graph] AutoTemporalGraph, AutoSpatioTemporalGraph
    observation_time: str | None = None
    # [graph] AutoSpatialGraph, AutoSpatioTemporalGraph
    observation_location: str | None = None


class DisplaySchema(BaseModel):
    """Display configuration"""

    # [non-graph] AutoModel, AutoList, AutoSet
    label: str | None = None
    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    entity_label: Union[str, Dict[str, str | None]] = None
    relation_label: Union[str, Dict[str, str | None]] = None


class IdentifiersSchema(BaseModel):
    """Identifier configuration"""

    # [non-graph] AutoSet
    item_id: str | None = None
    # [graph] AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
    entity_id: str | None = None
    relation_id: str | None = None
    relation_members: str | Dict[str, str | None, List[str]] | None = None
    # [graph] AutoTemporalGraph, AutoSpatioTemporalGraph
    time_field: str | None = None
    # [graph] AutoSpatialGraph, AutoSpatioTemporalGraph
    location_field: str | None = None


class RawTemplateCfg(BaseModel):
    """Template configuration - raw config loaded from YAML (multilingual)."""

    language: str | List[str] = "en"
    name: str
    type: Literal[
        "model",
        "list",
        "set",
        "graph",
        "hypergraph",
        "temporal_graph",
        "spatial_graph",
        "spatio_temporal_graph",
    ]
    tags: List[str]
    description: str | Dict[str, str]
    output: NaiveOutputSchema | GraphOutputSchema
    guideline: GuidelineSchema
    identifiers: IdentifiersSchema | None = None
    options: OptionsSchema | None = None
    display: DisplaySchema


class TemplateCfg(BaseModel):
    """Single-language version of Template configuration."""

    language: str | List[str] = "en"
    name: str
    type: Literal[
        "model",
        "list",
        "set",
        "graph",
        "hypergraph",
        "temporal_graph",
        "spatial_graph",
        "spatio_temporal_graph",
    ]
    tags: List[str]
    description: str | Dict[str, str]
    output: NaiveOutputSchema | GraphOutputSchema
    guideline: GuidelineSchema
    identifiers: IdentifiersSchema | None = None
    options: OptionsSchema | None = None
    display: DisplaySchema

def extract_specific_language_config(
    multi: RawTemplateCfg, language: str
) -> TemplateCfg:
    """Extract specific language config from multilingual config."""
    lang = multi.language
    if isinstance(lang, list):
        lang = lang[0] if lang else language
    elif lang is None:
        lang = language

    return TemplateCfg(
        language=lang,
        name=multi.name,
        type=multi.type,
        tags=multi.tags or [],
    )


class ConfigLoader:
    """Config loader."""

    @staticmethod
    def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load YAML configuration file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def load_config(file_path: Union[str, Path]) -> RawTemplateCfg:
        """Load and validate configuration."""
        data = ConfigLoader.load_yaml(file_path)
        return RawTemplateCfg(**data)

    @staticmethod
    def load_config_from_dict(data: Dict[str, Any]) -> RawTemplateCfg:
        """Load configuration from dict."""
        return RawTemplateCfg(**data)

    @staticmethod
    def get_text_value(
        value: Union[str, Dict[str, str], None], language: str = "zh"
    ) -> str | None:
        """Get multilingual text value."""
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return value.get(language) or value.get("zh") or ""
        return None

    @staticmethod
    def validate_type(type_value: str) -> bool:
        """Validate if type is valid."""
        valid_types = {
            "model",
            "list",
            "set",
            "graph",
            "hypergraph",
            "temporal_graph",
            "spatial_graph",
            "spatio_temporal_graph",
        }
        return type_value in valid_types


__all__ = [
    "parse_multi_lang",
    "GuidelineSchema",
    "GuidelineSchemaMono",
    "FieldSchema",
    "FieldsDefinition",
    "OutputSchema",
    "OutputSchemaMono",
    "OptionsSchema",
    "DisplaySchema",
    "DisplaySchemaMono",
    "IdentifiersSchema",
    "TemplateSchema",
    "RawTemplateCfg",
    "TemplateCfg",
    "ConfigLoader",
]
