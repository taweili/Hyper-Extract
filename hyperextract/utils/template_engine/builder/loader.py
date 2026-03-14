"""Config loader and template configuration models."""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict

from .prompt import Guideline
from .identifiers import Identifiers
from .schema import ModelSchema, ItemSchema, NodeSchema, EdgeSchema, OutputDefinition
from .options import Options


class Display(BaseModel):
    """Display configuration."""

    label: Optional[str] = None
    entity_label: Optional[str] = None
    relation_label: Optional[str] = None


class TemplateConfig(BaseModel):
    """Template configuration top-level model."""

    language: Optional[Union[str, List[str]]] = "zh"
    name: str
    type: Literal[
        "model", "list", "set", "graph", "hypergraph",
        "temporal_graph", "spatial_graph", "spatio_temporal_graph"
    ]
    tags: Optional[List[str]] = None
    description: Optional[Union[str, Dict[str, str]]] = None
    output: Optional[OutputDefinition] = None
    model_schema: Optional[ModelSchema] = Field(None, alias="schema")
    item_schema: Optional[ItemSchema] = None
    node_schema: Optional[NodeSchema] = None
    edge_schema: Optional[EdgeSchema] = None
    guideline: Optional[Guideline] = None
    identifiers: Optional[Identifiers] = None
    options: Optional[Options] = None
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
    def validate_type(type_value: str) -> bool:
        """Validate if type is valid."""
        valid_types = {
            "model", "list", "set", "graph", "hypergraph",
            "temporal_graph", "spatial_graph", "spatio_temporal_graph"
        }
        return type_value in valid_types


__all__ = [
    "Display",
    "TemplateConfig",
    "ConfigLoader",
]
