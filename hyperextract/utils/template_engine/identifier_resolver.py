"""Identifier Resolver - Generates extraction functions for nodes and edges.

Converts identifier definitions in configuration to callable functions.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel


class IdentifierResolver:
    """Identifier Resolver."""

    @staticmethod
    def resolve_item_id(field_name: str) -> Callable[[BaseModel], str]:
        """Generate item ID extractor for Set type."""
        def extractor(item: BaseModel) -> str:
            value = getattr(item, field_name, None)
            return str(value) if value is not None else ""
        return extractor

    @staticmethod
    def resolve_node_id(field_name: str) -> Callable[[BaseModel], str]:
        """Generate node ID extractor."""
        def extractor(node: BaseModel) -> str:
            value = getattr(node, field_name, None)
            return str(value) if value is not None else ""
        return extractor

    @staticmethod
    def resolve_edge_id(template: str) -> Callable[[BaseModel], str]:
        """Generate edge ID extractor (supports template string)."""
        def extractor(edge: BaseModel) -> str:
            try:
                return template.format(**edge.model_dump())
            except (KeyError, ValueError):
                parts = []
                for key in template.split("|"):
                    key = key.strip().strip("{}")
                    value = getattr(edge, key, None)
                    parts.append(str(value) if value is not None else "")
                return "|".join(parts)
        return extractor

    @staticmethod
    def resolve_edge_members(
        edge_members: Union[str, Dict[str, str]]
    ) -> Callable[[BaseModel], Tuple[str, ...]]:
        """Generate edge member extractor (unified for binary edge/hyperedge)."""
        if isinstance(edge_members, str):
            def extractor(edge: BaseModel) -> Tuple[str, ...]:
                value = getattr(edge, edge_members, None)
                if value is None:
                    return ()
                if isinstance(value, (list, tuple)):
                    return tuple(str(v) for v in value)
                return (str(value),)
            return extractor
        elif isinstance(edge_members, dict):
            source_key = edge_members.get("source", "source")
            target_key = edge_members.get("target", "target")

            def extractor(edge: BaseModel) -> Tuple[str, str]:
                source = getattr(edge, source_key, None)
                target = getattr(edge, target_key, None)
                return (
                    str(source) if source is not None else "",
                    str(target) if target is not None else "",
                )
            return extractor
        else:
            raise ValueError(f"Invalid edge_members configuration: {edge_members}")

    @staticmethod
    def resolve_time(field_name: str) -> Callable[[BaseModel], str]:
        """Generate time extractor."""
        def extractor(item: BaseModel) -> str:
            value = getattr(item, field_name, None)
            return str(value) if value is not None else ""
        return extractor

    @staticmethod
    def resolve_location(field_name: str) -> Callable[[BaseModel], str]:
        """Generate location extractor."""
        def extractor(item: BaseModel) -> str:
            value = getattr(item, field_name, None)
            return str(value) if value is not None else ""
        return extractor

    @classmethod
    def resolve_all(cls, config) -> Dict[str, Callable]:
        """Resolve all identifier extractors based on configuration."""
        result = {}
        identifiers = config.identifiers or {}
        autotype = config.autotype

        # Handle Identifiers object or dict
        if hasattr(identifiers, 'model_dump'):
            identifiers_dict = identifiers.model_dump()
        elif isinstance(identifiers, dict):
            identifiers_dict = identifiers
        else:
            identifiers_dict = {}

        if autotype == "set" and identifiers_dict.get("item_id"):
            result["item_id_extractor"] = cls.resolve_item_id(identifiers_dict["item_id"])

        if autotype in ("graph", "hypergraph", "temporal_graph", "spatial_graph", "spatio_temporal_graph"):
            if identifiers_dict.get("node_id"):
                result["node_key_extractor"] = cls.resolve_node_id(identifiers_dict["node_id"])

            if identifiers_dict.get("edge_id"):
                result["edge_key_extractor"] = cls.resolve_edge_id(identifiers_dict["edge_id"])

            if identifiers_dict.get("edge_members"):
                result["nodes_in_edge_extractor"] = cls.resolve_edge_members(identifiers_dict["edge_members"])

        if autotype in ("temporal_graph", "spatio_temporal_graph"):
            if identifiers_dict.get("time_field"):
                result["time_in_edge_extractor"] = cls.resolve_time(identifiers_dict["time_field"])

        if autotype in ("spatial_graph", "spatio_temporal_graph"):
            if identifiers_dict.get("location_field"):
                result["location_in_edge_extractor"] = cls.resolve_location(identifiers_dict["location_field"])

        return result
