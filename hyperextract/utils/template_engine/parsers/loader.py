"""Config loader and template configuration models."""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Literal, Union
from pydantic import BaseModel


VALID_MERGE_STRATEGIES = Literal[
    "merge_field",
    "keep_incoming",
    "keep_existing",
    "llm_balanced",
    "llm_prefer_incoming",
    "llm_prefer_existing",
]
AUTO_TYPES = Literal[
    "model",
    "list",
    "set",
    "graph",
    "hypergraph",
    "temporal_graph",
    "spatial_graph",
    "spatio_temporal_graph",
]


# ==============================================================
# Naive Template Configuration: AutoModel, AutoList, AutoSet
# ==============================================================
class NaiveGuidelineSchema(BaseModel):
    """Naive guideline schema"""

    target: str | List[str] | Dict[str, str | List[str]]
    rules: str | List[str] | Dict[str, str | List[str]]


class FieldSchema(BaseModel):
    """Field definition"""

    name: str
    type: Literal["str", "int", "float", "bool", "list", "dict"]
    description: str | Dict[str, str]
    required: bool = False
    default: Any | None = None


class NaiveOutputSchema(BaseModel):
    """Naive output schema"""

    description: str | Dict[str, str]
    fields: List[FieldSchema]


class NaiveOptionsSchema(BaseModel):
    """Naive runtime options"""

    chunk_size: int = 2048
    chunk_overlap: int = 256
    max_workers: int = 10
    verbose: bool = False
    merge_strategy: VALID_MERGE_STRATEGIES = "llm_balanced"
    fields_for_search: List[str] | None = None


class NaiveDisplaySchema(BaseModel):
    """Naive display configuration"""

    label: str


class NaiveIdentifierSchema(BaseModel):
    """Naive identifier configuration"""

    item_id: str | None = None


# ==============================================================
# Graph Template Configuration: AutoGraph, AutoHyperGraph
# AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph
# ==============================================================


class GraphGuidelineSchema(BaseModel):
    """Graph guideline schema"""

    target: str | List[str] | Dict[str, str | List[str]]
    rules_for_entities: str | List[str] | Dict[str, str | List[str]]
    rules_for_relations: str | List[str] | Dict[str, str | List[str]]
    # AutoTemporalGraph, AutoSpatioTemporalGraph
    rules_for_time: str | List[str] | Dict[str, str | List[str]]
    # AutoSpatialGraph, AutoSpatioTemporalGraph
    rules_for_location: str | List[str] | Dict[str, str | List[str]]


class GraphOutputSchema(BaseModel):
    """Graph output schema"""

    description: str | Dict[str, str]
    entities: NaiveOutputSchema
    relations: NaiveOutputSchema


class GraphOptionsSchema(BaseModel):
    """Graph runtime options"""

    chunk_size: int = 2048
    chunk_overlap: int = 256
    max_workers: int = 10
    verbose: bool = False
    entity_merge_strategy: VALID_MERGE_STRATEGIES = "llm_balanced"
    relation_merge_strategy: VALID_MERGE_STRATEGIES = "llm_balanced"
    extraction_mode: str | None = None
    entity_fields_for_search: List[str] | None = None
    relation_fields_for_search: List[str] | None = None
    # AutoTemporalGraph, AutoSpatioTemporalGraph
    observation_time: str | None = None
    # AutoSpatialGraph, AutoSpatioTemporalGraph
    observation_location: str | None = None


class GraphDisplaySchema(BaseModel):
    """Graph display configuration"""

    entity_label: str
    relation_label: str


class GraphIdentifiersSchema(BaseModel):
    """Graph Identifier configuration"""

    entity_id: str | None = None
    relation_id: str | None = None
    relation_members: str | Dict[str, str | None, List[str]] | None = None
    # AutoTemporalGraph, AutoSpatioTemporalGraph
    time_field: str | None = None
    # AutoSpatialGraph, AutoSpatioTemporalGraph
    location_field: str | None = None


class TemplateCfg(BaseModel):
    """Template configuration loaded from YAML."""

    language: str | List[str] = "en"
    name: str
    type: AUTO_TYPES
    tags: List[str]
    description: str | Dict[str, str]
    output: NaiveOutputSchema | GraphOutputSchema
    guideline: NaiveGuidelineSchema | GraphGuidelineSchema
    identifiers: NaiveIdentifierSchema | GraphIdentifiersSchema | None = None
    options: NaiveOptionsSchema | GraphOptionsSchema | None = None
    display: NaiveDisplaySchema | GraphDisplaySchema


# ==============================================================
# Localization Functions
# ==============================================================


def _localize_data(
    value: str | List[str] | Dict[str, str | List[str]] | None,
    language: str,
) -> str:
    """Get multilingual text value, supports list format

    Args:
        value: Multilingual value, supports string, list or dict format
        language: Target language code

    Returns:
        str: Converted string
    """
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(value))
    dict_value = value.get(language)
    if isinstance(dict_value, str):
        return dict_value
    if isinstance(dict_value, list):
        return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(dict_value))


def _localize_field(field: FieldSchema, language: str) -> FieldSchema:
    """Localize a single field."""
    return FieldSchema(
        name=field.name,
        type=field.type,
        description=_localize_data(field.description, language),
        required=field.required,
        default=field.default,
    )


def _localize_naive_output(
    output: NaiveOutputSchema, language: str
) -> NaiveOutputSchema:
    """Localize NaiveOutputSchema."""
    fields = [_localize_field(f, language) for f in output.fields]
    return NaiveOutputSchema(
        description=_localize_data(output.description, language),
        fields=fields,
    )


def _localize_output(
    output: NaiveOutputSchema | GraphOutputSchema,
    language: str,
    autotype: AUTO_TYPES | None = None,
) -> NaiveOutputSchema | GraphOutputSchema:
    """Localize output configuration."""
    if autotype in ("model", "list", "set"):
        return _localize_naive_output(output, language)
    return GraphOutputSchema(
        description=_localize_data(output.description, language),
        entities=_localize_naive_output(output.entities, language),
        relations=_localize_naive_output(output.relations, language),
    )


def _localize_guideline(
    guideline: NaiveGuidelineSchema | GraphGuidelineSchema,
    language: str,
    autotype: AUTO_TYPES | None = None,
) -> NaiveGuidelineSchema | GraphGuidelineSchema:
    """Localize guideline configuration."""
    if autotype in ("model", "list", "set"):
        return NaiveGuidelineSchema(
            target=_localize_data(guideline.target, language),
            rules=_localize_data(guideline.rules, language),
        )
    return GraphGuidelineSchema(
        target=_localize_data(guideline.target, language),
        rules_for_entities=_localize_data(guideline.rules_for_entities, language),
        rules_for_relations=_localize_data(guideline.rules_for_relations, language),
        rules_for_time=_localize_data(guideline.rules_for_time, language)
        if guideline.rules_for_time
        else None,
        rules_for_location=_localize_data(guideline.rules_for_location, language)
        if guideline.rules_for_location
        else None,
    )


def localize_template(config: TemplateCfg, language: str) -> TemplateCfg:
    """Convert multilingual template config to single-language config.

    Args:
        config: Original multilingual config
        language: Target language code (e.g., 'zh', 'en')

    Returns:
        TemplateCfg: Single-language config with all multilingual fields converted to strings

    Examples:
        >>> config = ConfigLoader.load_config("template.yaml")
        >>> config_zh = localize_template(config, "zh")
        >>> print(config_zh.description)  # string
    """

    return TemplateCfg(
        language=language,
        name=config.name,
        type=config.type,
        tags=config.tags,
        description=_localize_data(config.description, language),
        output=_localize_output(config.output, language),
        guideline=_localize_guideline(config.guideline, language, config.type),
        identifiers=config.identifiers,
        options=config.options,
        display=config.display,
    )


def load_template(file_path: Union[str, Path]) -> TemplateCfg:
    """Load and validate template configuration."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        template = TemplateCfg(**yaml.safe_load(f))

    # Validate multi-language support
    existing_languages = (
        template.language
        if isinstance(template.language, list)
        else [template.language]
    )
    for lang in existing_languages:
        try:
            localize_template(template, lang)
        except Exception as e:
            raise ValueError(
                f"The template configuration is not valid for language {lang}: {e}"
            )

    return template


__all__ = [
    "TemplateCfg",
    "load_template",
    "localize_template",
]
