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


class FieldsDefinition(BaseModel):
    """Fields definition container with description."""

    description: Optional[Union[str, Dict[str, str]]] = None
    fields: List[SchemaField] = Field(default_factory=list)


class OutputDefinition(BaseModel):
    """Output definition - unified data structure definition."""

    description: Optional[Union[str, Dict[str, str]]] = None
    fields: Optional[List[SchemaField]] = None
    entities: Optional[FieldsDefinition] = None
    relations: Optional[FieldsDefinition] = None


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

    @staticmethod
    def build_schema_description(description: Optional[Union[str, Dict[str, str]]]) -> str:
        """Build schema-level description."""
        if description is None:
            return ""
        if isinstance(description, str):
            return description
        if isinstance(description, dict):
            return description.get("zh") or description.get("en") or ""
        return str(description)

    @classmethod
    def _build_schema_from_fields(cls, fields: List[SchemaField]) -> Type[BaseModel]:
        """Build Pydantic schema from field list."""
        schema_fields = {}
        for field in fields:
            field_type = cls.build_field_type(field)
            default = cls.build_field_default(field)
            description = cls.build_field_description(field)
            schema_fields[field.name] = (field_type, Field(default=default, description=description))
        return create_model("GeneratedSchema", **schema_fields)

    @classmethod
    def build_model_schema(cls, schema: ModelSchema) -> Type[BaseModel]:
        """Build Model type Schema."""
        return cls._build_schema_from_fields(schema.fields)

    @classmethod
    def build_item_schema(cls, schema: ItemSchema) -> Type[BaseModel]:
        """Build List/Set type Item Schema."""
        return cls._build_schema_from_fields(schema.fields)

    @classmethod
    def build_node_schema(cls, schema: NodeSchema) -> Type[BaseModel]:
        """Build Graph type Node Schema."""
        return cls._build_schema_from_fields(schema.fields)

    @classmethod
    def build_edge_schema(cls, schema: EdgeSchema) -> Type[BaseModel]:
        """Build Graph type Edge Schema."""
        return cls._build_schema_from_fields(schema.fields)

    @classmethod
    def build_output_schema(cls, output: OutputDefinition) -> Type[BaseModel]:
        """Build schema from OutputDefinition (for non-graph types)."""
        if output.fields is None:
            raise ValueError("OutputDefinition must have fields for non-graph types")
        model = cls._build_schema_from_fields(output.fields)
        if output.description:
            model.__doc__ = cls.build_schema_description(output.description)
        return model

    @classmethod
    def build_entity_schema(cls, entities: FieldsDefinition) -> Type[BaseModel]:
        """Build entity schema from FieldsDefinition."""
        model = cls._build_schema_from_fields(entities.fields)
        if entities.description:
            model.__doc__ = cls.build_schema_description(entities.description)
        return model

    @classmethod
    def build_relation_schema(cls, relations: FieldsDefinition) -> Type[BaseModel]:
        """Build relation schema from FieldsDefinition."""
        model = cls._build_schema_from_fields(relations.fields)
        if relations.description:
            model.__doc__ = cls.build_schema_description(relations.description)
        return model

    @classmethod
    def build_schema(cls, config) -> Dict[str, Type[BaseModel]]:
        """Build corresponding Schema based on configuration."""
        result = {}

        if config.output is not None:
            autotype = config.type

            if autotype in ("model", "list", "set"):
                if config.output.fields:
                    result["schema"] = cls.build_output_schema(config.output)

            elif autotype in ("graph", "hypergraph", "temporal_graph", "spatial_graph", "spatio_temporal_graph"):
                if config.output.entities:
                    result["entity_schema"] = cls.build_entity_schema(config.output.entities)
                if config.output.relations:
                    result["relation_schema"] = cls.build_relation_schema(config.output.relations)

        if config.model_schema is not None:
            result["schema"] = cls.build_model_schema(config.model_schema)

        if config.item_schema is not None:
            result["item_schema"] = cls.build_item_schema(config.item_schema)

        if config.node_schema is not None:
            result["entity_schema"] = cls.build_node_schema(config.node_schema)

        if config.edge_schema is not None:
            result["relation_schema"] = cls.build_edge_schema(config.edge_schema)

        return result


__all__ = [
    "FieldDescription",
    "SchemaField",
    "FieldsDefinition",
    "OutputDefinition",
    "BaseSchema",
    "ModelSchema",
    "ItemSchema",
    "NodeSchema",
    "EdgeSchema",
    "SchemaBuilder",
]
