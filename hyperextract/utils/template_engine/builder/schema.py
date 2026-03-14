"""Schema models and builder."""

from typing import Any, Dict, List, Literal, Optional, Union, Type
from pydantic import BaseModel, Field, field_validator, create_model


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


TYPE_MAPPING = {
    "string": str,
    "int": int,
    "float": float,
    "bool": bool,
    "array": List,
}


class SchemaBuilder:
    """Schema Builder - Dynamically generates Pydantic Schema."""

    @staticmethod
    def build_field_type(field: SchemaField) -> Type:
        """Build field type."""
        if field.type == "array":
            if field.item_type:
                item_type = TYPE_MAPPING.get(field.item_type, str)
                return List[item_type]
            return List
        return TYPE_MAPPING.get(field.type, str)

    @staticmethod
    def build_field_default(field: SchemaField) -> Any:
        """Build field default value."""
        if field.required:
            return ...
        if field.default is not None:
            return field.default
        if field.type == "array":
            return []
        return None

    @staticmethod
    def build_field_description(field: SchemaField) -> str:
        """Build field description."""
        if field.description is None:
            return ""
        if isinstance(field.description, str):
            return field.description
        if isinstance(field.description, dict):
            return field.description.get("zh") or field.description.get("en") or ""
        return str(field.description)

    @classmethod
    def build_model_schema(cls, schema: ModelSchema) -> Type[BaseModel]:
        """Build Model type Schema."""
        fields = {}
        for field in schema.fields:
            field_type = cls.build_field_type(field)
            default = cls.build_field_default(field)
            description = cls.build_field_description(field)
            fields[field.name] = (field_type, Field(default=default, description=description))

        return create_model("GeneratedModelSchema", **fields)

    @classmethod
    def build_item_schema(cls, schema: ItemSchema) -> Type[BaseModel]:
        """Build List/Set type Item Schema."""
        fields = {}
        for field in schema.fields:
            field_type = cls.build_field_type(field)
            default = cls.build_field_default(field)
            description = cls.build_field_description(field)
            fields[field.name] = (field_type, Field(default=default, description=description))

        return create_model("GeneratedItemSchema", **fields)

    @classmethod
    def build_node_schema(cls, schema: NodeSchema) -> Type[BaseModel]:
        """Build Graph type Node Schema."""
        fields = {}
        for field in schema.fields:
            field_type = cls.build_field_type(field)
            default = cls.build_field_default(field)
            description = cls.build_field_description(field)
            fields[field.name] = (field_type, Field(default=default, description=description))

        return create_model("GeneratedNodeSchema", **fields)

    @classmethod
    def build_edge_schema(cls, schema: EdgeSchema) -> Type[BaseModel]:
        """Build Graph type Edge Schema."""
        fields = {}
        for field in schema.fields:
            field_type = cls.build_field_type(field)
            default = cls.build_field_default(field)
            description = cls.build_field_description(field)
            fields[field.name] = (field_type, Field(default=default, description=description))

        return create_model("GeneratedEdgeSchema", **fields)

    @classmethod
    def build_schema(cls, config) -> Dict[str, Type[BaseModel]]:
        """Build corresponding Schema based on configuration."""
        result = {}

        if config.model_schema is not None:
            result["schema"] = cls.build_model_schema(config.model_schema)

        if config.item_schema is not None:
            result["item_schema"] = cls.build_item_schema(config.item_schema)

        if config.node_schema is not None:
            result["node_schema"] = cls.build_node_schema(config.node_schema)

        if config.edge_schema is not None:
            result["edge_schema"] = cls.build_edge_schema(config.edge_schema)

        return result


__all__ = [
    "FieldDescription",
    "SchemaField",
    "BaseSchema",
    "ModelSchema",
    "ItemSchema",
    "NodeSchema",
    "EdgeSchema",
    "SchemaBuilder",
]
