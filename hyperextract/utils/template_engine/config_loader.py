"""Config Loader - Loads and validates YAML configuration files.

Provides configuration schema definition, multilingual field parsing, and configuration validation.
"""

from typing import Any, Dict, List, Literal, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, ConfigDict
import yaml


class FieldDescription(BaseModel):
    """Field description with multilingual support."""

    zh: Optional[str] = None
    en: Optional[str] = None

    def get(self, language: str = "zh") -> str:
        """Get description for specified language."""
        if isinstance(self, str):
            return self
        return getattr(self, language) or self.zh or ""


class SchemaField(BaseModel):
    """Schema field definition."""

    name: str
    type: Literal["string", "int", "float", "bool", "array"]
    description: Optional[Union[str, Dict[str, str]]] = None
    required: bool = False
    default: Optional[Any] = None
    item_type: Optional[str] = None

    @field_validator("description", mode="before")
    @classmethod
    def parse_description(cls, v):
        """Parse description field, supports plain string or multilingual dict."""
        return v


class BaseSchema(BaseModel):
    """Base schema configuration."""

    fields: List[SchemaField] = Field(default_factory=list)


class ModelSchema(BaseSchema):
    """Model type schema."""
    pass


class ItemSchema(BaseSchema):
    """List/Set type item schema."""
    pass


class NodeSchema(BaseSchema):
    """Graph type node schema."""
    pass


class EdgeSchema(BaseSchema):
    """Graph type edge schema."""
    pass


class ExtractionGuideTarget(BaseModel):
    """Extraction target with role definition and content description."""

    zh: Optional[str] = None
    en: Optional[str] = None

    @classmethod
    def from_value(cls, value: Union[str, Dict[str, str], None]) -> Optional["ExtractionGuideTarget"]:
        """Create instance from string or dict."""
        if value is None:
            return None
        if isinstance(value, str):
            return cls(zh=value)
        if isinstance(value, dict):
            return cls(**value)
        return None

    def get(self, language: str = "zh") -> str:
        """Get content for specified language."""
        return getattr(self, language) or self.zh or ""


class ExtractionGuide(BaseModel):
    """Extraction guide configuration."""

    target: Optional[Union[str, Dict[str, str]]] = None
    rules: Optional[Union[str, Dict[str, str]]] = None
    rules_for_nodes: Optional[Union[str, Dict[str, str]]] = None
    rules_for_edges: Optional[Union[str, Dict[str, str]]] = None
    rules_for_time: Optional[Union[str, Dict[str, str]]] = None
    rules_for_location: Optional[Union[str, Dict[str, str]]] = None

    def get_field(self, field_name: str, language: str = "zh") -> Optional[str]:
        """Get specified field content for specified language."""
        value = getattr(self, field_name, None)
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return value.get(language) or value.get("zh") or ""
        return None


class Identifiers(BaseModel):
    """Identifier configuration."""

    item_id: Optional[str] = None
    node_id: Optional[str] = None
    edge_id: Optional[str] = None
    edge_members: Optional[Union[str, Dict[str, str], List[str]]] = None
    time_field: Optional[str] = None
    location_field: Optional[str] = None


class Parameters(BaseModel):
    """Runtime parameters configuration."""

    merge_strategy: Optional[str] = None
    custom_merge_rule: Optional[Union[str, Dict[str, str]]] = None
    node_merge_strategy: Optional[str] = None
    node_custom_merge_rule: Optional[Union[str, Dict[str, str]]] = None
    edge_merge_strategy: Optional[str] = None
    edge_custom_merge_rule: Optional[Union[str, Dict[str, str]]] = None
    extraction_mode: Optional[str] = None
    observation_time: Optional[str] = None
    observation_location: Optional[str] = None
    chunk_size: int = 2048
    chunk_overlap: int = 256
    max_workers: int = 10
    verbose: bool = False
    search_fields: Optional[List[str]] = None
    node_search_fields: Optional[List[str]] = None
    edge_search_fields: Optional[List[str]] = None

    def get_merge_strategy(self) -> Optional[str]:
        """Get merge strategy."""
        return self.merge_strategy or self.node_merge_strategy

    def get_custom_merge_rule(self, language: str = "zh") -> Optional[str]:
        """Get custom merge rule."""
        rule = self.custom_merge_rule or self.node_custom_merge_rule
        if rule is None:
            return None
        if isinstance(rule, str):
            return rule
        if isinstance(rule, dict):
            return rule.get(language) or rule.get("zh") or ""
        return None


class Display(BaseModel):
    """Display configuration."""

    label: Optional[str] = None
    node_label: Optional[str] = None
    edge_label: Optional[str] = None


class TemplateConfig(BaseModel):
    """Template configuration top-level model."""

    name: str
    autotype: Literal[
        "model", "list", "set", "graph", "hypergraph",
        "temporal_graph", "spatial_graph", "spatio_temporal_graph"
    ]
    tag: Optional[List[str]] = None
    language: Optional[Union[str, List[str]]] = "zh"
    description: Optional[Union[str, Dict[str, str]]] = None
    model_schema: Optional[ModelSchema] = Field(None, alias="schema")
    item_schema: Optional[ItemSchema] = None
    node_schema: Optional[NodeSchema] = None
    edge_schema: Optional[EdgeSchema] = None
    extraction_guide: Optional[ExtractionGuide] = None
    identifiers: Optional[Identifiers] = None
    parameters: Optional[Parameters] = None
    display: Optional[Display] = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("description", mode="before")
    @classmethod
    def parse_description(cls, v):
        """Parse description field."""
        return v

    def model_dump(self, **kwargs):
        """Override model_dump to handle alias."""
        data = super().model_dump(**kwargs)
        if "schema" in data and data["schema"] is None:
            data["schema"] = data.pop("model_schema", None)
        return data


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
    def load_config(file_path: Union[str, Path]) -> TemplateConfig:
        """Load and validate configuration."""
        data = ConfigLoader.load_yaml(file_path)
        return TemplateConfig(**data)

    @staticmethod
    def load_config_from_dict(data: Dict[str, Any]) -> TemplateConfig:
        """Load configuration from dict."""
        return TemplateConfig(**data)

    @staticmethod
    def get_text_value(value: Union[str, Dict[str, str], None], language: str = "zh") -> Optional[str]:
        """Get multilingual text value."""
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return value.get(language) or value.get("zh") or ""
        return None

    @staticmethod
    def validate_autotype(autotype: str) -> bool:
        """Validate if autotype is valid."""
        valid_types = {
            "model", "list", "set", "graph", "hypergraph",
            "temporal_graph", "spatial_graph", "spatio_temporal_graph"
        }
        return autotype in valid_types
