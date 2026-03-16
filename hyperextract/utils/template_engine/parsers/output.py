"""Output schema parser."""

from typing import List
from .schemas import (
    FieldSchema,
    NaiveOutputSchema,
    GraphOutputSchema,
    NaiveOutputSchema,
)
from pydantic import Field, create_model, BaseModel


TYPE_MAPPING = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list[str]": List[str],
}


def build_naive_schema(
    name: str,
    fields: List[FieldSchema],
    description: str,
) -> BaseModel:
    """Build Pydantic schema for naive types (model, list, set)."""
    schema_fields = {}
    for field in fields:
        kwargs = {
            "description": field.description,
        }
        if field.required is not None:
            kwargs["required"] = field.required
        if field.default is not None:
            kwargs["default"] = field.default
        schema_fields[field.name] = (TYPE_MAPPING[field.type], Field(**kwargs))
    return create_model(name, __doc__=description, **schema_fields)


def build_graph_schema(
    name: str,
    entity: NaiveOutputSchema,
    relation: NaiveOutputSchema,
    description: str,
) -> BaseModel:
    """Build Pydantic schema for graph types (graph, hypergraph, temporal_graph, spatial_graph, spatio_temporal_graph)."""
    schema_fields = {
        "entities": build_naive_schema(
            entity.name,
            entity.fields,
            entity.description,
        ),
        "relations": build_naive_schema(
            relation.name,
            relation.fields,
            relation.description,
        ),
    }
    return create_model(name, __doc__=description, **schema_fields)


def parse_output(
    output: NaiveOutputSchema | GraphOutputSchema, autotype: str
) -> BaseModel:
    """Parse template and return schemas based on autotype.

    Args:
        config: TemplateCfg instance

    """

    if autotype in ("model", "list", "set"):
        return build_naive_schema(
            output.name,
            output.fields,
            output.description,
        )
    else:
        return build_graph_schema(
            output.name,
            output.entities,
            output.relations,
            output.description,
        )


__all__ = [
    "parse_output",
]
