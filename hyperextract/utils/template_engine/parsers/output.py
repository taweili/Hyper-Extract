"""Output schema parser."""

from typing import Any, List, Type, Union, Tuple
from pydantic import Field, create_model


TYPE_MAPPING = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
}


def build_field_type(field) -> Type:
    """Build field type from field definition."""
    if isinstance(field, dict):
        field_type_str = field.get("type", "str")
    else:
        field_type_str = field.type

    if field_type_str == "list":
        if isinstance(field, dict):
            item_type_str = field.get("item_type")
        else:
            item_type_str = getattr(field, "item_type", None)
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
        is_required = getattr(field, "required", False)
        default_val = getattr(field, "default", None)

    if is_required:
        return ...
    if default_val is not None:
        return default_val
    field_type = field.get("type", "str") if isinstance(field, dict) else getattr(field, "type", "str")
    if field_type == "list":
        return []
    return None


def build_field_description(field) -> str:
    """Get field description (config is already localized)."""
    if isinstance(field, dict):
        return field.get("description", "") or ""
    return getattr(field, "description", "") or ""


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
            field_name = getattr(field, "name", None)

        if not field_name:
            continue

        field_type = build_field_type(field)
        default = build_field_default(field)
        description = build_field_description(field)
        schema_fields[field_name] = (field_type, Field(default=default, description=description))
    return create_model(schema_name, **schema_fields)


def _get_output_value(output, attr: str):
    """Get value from output object."""
    if output is None:
        return None
    if isinstance(output, dict):
        return output.get(attr)
    return getattr(output, attr, None)


def _build_naive_schema(config) -> Type:
    """Build schema for non-graph types (model, list, set)."""
    output = config.output
    output_fields = _get_output_value(output, "fields") if output else None
    
    if output_fields:
        schema_name = f"{config.name}Schema"
        return _build_schema_from_fields(output_fields, schema_name)

    raise ValueError(f"No fields definition found for {config.type} type: {config.name}")


def _build_graph_schemas(config) -> Tuple[Type, Type]:
    """Build schemas for graph types (graph, hypergraph, temporal_graph, spatial_graph, spatio_temporal_graph)."""
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

    raise ValueError(f"No schema definition found for graph type: {config.name}")


def OutputParser(config) -> Union[Type, Tuple[Type, Type]]:
    """Parse template and return schemas based on autotype.

    Args:
        config: TemplateCfg instance (single-language, all fields are strings)

    Returns:
        - For non-graph types (model, list, set): returns data_schema
        - For graph types: returns (entity_schema, relation_schema)
    """
    autotype = config.type

    if autotype in ("model", "list", "set"):
        return _build_naive_schema(config)
    else:
        return _build_graph_schemas(config)


__all__ = [
    "OutputParser",
]
