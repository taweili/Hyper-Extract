"""Output schema parser."""

from typing import Any, List, Type, Union, Tuple
from pydantic import Field, create_model


TYPE_MAPPING = {
    "string": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
}


def build_field_type(field) -> Type:
    """Build field type from field."""
    if isinstance(field, dict):
        field_type_str = field.get("type", "string")
    else:
        field_type_str = field.type

    if field_type_str == "list":
        if isinstance(field, dict):
            item_type_str = field.get("item_type")
        else:
            item_type_str = field.item_type
        if item_type_str:
            item_type = TYPE_MAPPING.get(item_type_str, str)
            return List[item_type]
        return List
    return TYPE_MAPPING.get(field_type_str, str)


def build_field_default(field) -> Any:
    """Build field default value."""
    if isinstance(field, dict):
        is_required = field.get("required", False)
        default_val = field.get("default")
    else:
        is_required = field.required
        default_val = field.default

    if is_required:
        return ...
    if default_val is not None:
        return default_val
    field_type = field.get("type", "string") if isinstance(field, dict) else field.type
    if field_type == "list":
        return []
    return None


def build_field_description(field) -> str:
    """Get field description (config is already localized, just return string)."""
    if isinstance(field, dict):
        return field.get("description", "") or ""
    return field.description or ""


def _build_schema_from_fields(
    fields: List,
    schema_name: str,
) -> Type:
    """Build Pydantic schema from field list."""
    schema_fields = {}
    for field in fields:
        if isinstance(field, dict):
            field_name = field.get("name")
        else:
            field_name = field.name

        if not field_name:
            continue

        field_type = build_field_type(field)
        default = build_field_default(field)
        description = build_field_description(field)
        schema_fields[field_name] = (field_type, Field(default=default, description=description))
    return create_model(schema_name, **schema_fields)


def _get_schema_fields(schema):
    """Get fields from schema."""
    if schema is None:
        return None
    if isinstance(schema, dict):
        return schema.get("fields")
    if hasattr(schema, "fields"):
        return schema.fields
    return None


def _get_output_value(output, attr: str):
    """Get value from output."""
    if output is None:
        return None
    if isinstance(output, dict):
        return output.get(attr)
    return getattr(output, attr, None)


def _build_non_graph_schema(config) -> Type:
    """Build schema for non-graph types (model, list, set)."""
    autotype = config.type

    output = config.output
    output_fields = _get_output_value(output, "fields") if output else None
    if output_fields:
        schema_name = f"{config.name}Schema"
        return _build_schema_from_fields(output_fields, schema_name)

    if autotype == "model":
        model_schema = getattr(config, "model_schema", None)
        if model_schema:
            fields = _get_schema_fields(model_schema)
            if fields:
                schema_name = f"{getattr(model_schema, '__name__', config.name)}Schema"
                return _build_schema_from_fields(fields, schema_name)

    if autotype in ("list", "set"):
        item_schema = getattr(config, "item_schema", None)
        if item_schema:
            fields = _get_schema_fields(item_schema)
            if fields:
                schema_name = f"{getattr(item_schema, '__name__', config.name)}Schema"
                return _build_schema_from_fields(fields, schema_name)

    raise ValueError(f"No schema definition found for {autotype} type: {config.name}")


def _build_graph_schemas(config) -> Tuple[Type, Type]:
    """Build schemas for graph types."""
    output = config.output
    entities = _get_output_value(output, "entities")
    relations = _get_output_value(output, "relations")

    if entities and relations:
        entity_fields = _get_output_value(entities, "fields")
        relation_fields = _get_output_value(relations, "fields")
        if entity_fields and relation_fields:
            entity_schema = _build_schema_from_fields(
                entity_fields,
                f"{config.name}Entity",
            )
            relation_schema = _build_schema_from_fields(
                relation_fields,
                f"{config.name}Relation",
            )
            return entity_schema, relation_schema

    node_schema = getattr(config, "node_schema", None)
    edge_schema = getattr(config, "edge_schema", None)
    if node_schema and edge_schema:
        entity_schema = _build_schema_from_fields(
            node_schema.fields if hasattr(node_schema, 'fields') else node_schema.get('fields'),
            f"{getattr(node_schema, '__name__', node_schema.get('__name__', 'Node'))}Entity",
        )
        relation_schema = _build_schema_from_fields(
            edge_schema.fields if hasattr(edge_schema, 'fields') else edge_schema.get('fields'),
            f"{getattr(edge_schema, '__name__', edge_schema.get('__name__', 'Edge'))}Relation",
        )
        return entity_schema, relation_schema

    raise ValueError(f"No schema definition found for graph type: {config.name}")


def OutputParser(config) -> Union[Type, Tuple[Type, Type]]:
    """Parse template and return schemas based on autotype (config is already localized).

    Args:
        config: Template Configuration instance (single-language)

    Returns:
        - For non-graph types (model, list, set): returns data_schema
        - For graph types: returns (entity_schema, relation_schema)
    """
    autotype = config.type

    if autotype in ("model", "list", "set"):
        return _build_non_graph_schema(config)
    else:
        return _build_graph_schemas(config)


__all__ = [
    "OutputParser",
]
