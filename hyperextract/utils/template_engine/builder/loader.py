"""Config loader, parameters and display models."""

from typing import Any, Dict, List, Literal, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, ConfigDict
import yaml

from .schema import ModelSchema, ItemSchema, NodeSchema, EdgeSchema
from .extraction import Guide
from .identifiers import Identifiers


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
    guide: Optional[Guide] = None
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


__all__ = [
    "Parameters",
    "Display",
    "TemplateConfig",
    "ConfigLoader",
]
