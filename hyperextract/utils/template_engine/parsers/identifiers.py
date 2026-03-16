"""Identifier models and resolver."""

from typing import Callable, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel


class Identifiers(BaseModel):
    """Identifier configuration."""

    item_id: Optional[str] = None
    entity_id: Optional[str] = None
    relation_id: Optional[str] = None
    relation_members: Optional[Union[str, Dict[str, str], List[str]]] = None
    time_field: Optional[str] = None
    location_field: Optional[str] = None


class IdentifierResolver:
    """Identifier Resolver - Generates extraction functions for entities and relations."""

    @staticmethod
    def resolve_item_id(field_name: str) -> Callable[[BaseModel], str]:
        """Generate item ID extractor for Set type."""
        def extractor(item: BaseModel) -> str:
            value = getattr(item, field_name, None)
            return str(value) if value is not None else ""
        return extractor

    @staticmethod
    def resolve_entity_id(field_name: str) -> Callable[[BaseModel], str]:
        """Generate entity ID extractor."""
        def extractor(entity: BaseModel) -> str:
            value = getattr(entity, field_name, None)
            return str(value) if value is not None else ""
        return extractor

    @staticmethod
    def resolve_relation_id(template: str) -> Callable[[BaseModel], str]:
        """Generate relation ID extractor (supports template str)."""
        def extractor(relation: BaseModel) -> str:
            try:
                return template.format(**relation.model_dump())
            except (KeyError, ValueError):
                parts = []
                for key in template.split("|"):
                    key = key.strip().strip("{}")
                    value = getattr(relation, key, None)
                    parts.append(str(value) if value is not None else "")
                return "|".join(parts)
        return extractor

    @staticmethod
    def resolve_relation_members(
        relation_members: Union[str, Dict[str, str], List[str]]
    ) -> Callable[[BaseModel], Tuple[str, ...]]:
        """Generate relation member extractor (unified for binary relation/hyperrelation)."""
        if isinstance(relation_members, str):
            def extractor(relation: BaseModel) -> Tuple[str, ...]:
                value = getattr(relation, relation_members, None)
                if value is None:
                    return ()
                if isinstance(value, (list, tuple)):
                    return tuple(str(v) for v in value)
                return (str(value),)
            return extractor
        elif isinstance(relation_members, dict):
            source_key = relation_members.get("source", "source")
            target_key = relation_members.get("target", "target")

            def extractor(relation: BaseModel) -> Tuple[str, str]:
                source = getattr(relation, source_key, None)
                target = getattr(relation, target_key, None)
                return (
                    str(source) if source is not None else "",
                    str(target) if target is not None else "",
                )
            return extractor
        elif isinstance(relation_members, list):
            def extractor(relation: BaseModel) -> Tuple[str, ...]:
                result = []
                for field_name in relation_members:
                    value = getattr(relation, field_name, None)
                    if value is None:
                        continue
                    if isinstance(value, (list, tuple)):
                        result.extend(str(v) for v in value)
                    else:
                        result.append(str(value))
                return tuple(result)
            return extractor
        else:
            raise ValueError(f"Invalid relation_members configuration: {relation_members}")

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
        autotype = config.type

        if hasattr(identifiers, 'model_dump'):
            identifiers_dict = identifiers.model_dump()
        elif isinstance(identifiers, dict):
            identifiers_dict = identifiers
        else:
            identifiers_dict = {}

        if autotype == "set" and identifiers_dict.get("item_id"):
            result["item_id_extractor"] = cls.resolve_item_id(identifiers_dict["item_id"])

        if autotype in ("graph", "hypergraph", "temporal_graph", "spatial_graph", "spatio_temporal_graph"):
            if identifiers_dict.get("entity_id"):
                result["entity_key_extractor"] = cls.resolve_entity_id(identifiers_dict["entity_id"])

            if identifiers_dict.get("relation_id"):
                result["relation_key_extractor"] = cls.resolve_relation_id(identifiers_dict["relation_id"])

            if identifiers_dict.get("relation_members"):
                result["entities_in_relation_extractor"] = cls.resolve_relation_members(identifiers_dict["relation_members"])

        if autotype in ("temporal_graph", "spatio_temporal_graph"):
            if identifiers_dict.get("time_field"):
                result["time_in_relation_extractor"] = cls.resolve_time(identifiers_dict["time_field"])

        if autotype in ("spatial_graph", "spatio_temporal_graph"):
            if identifiers_dict.get("location_field"):
                result["location_in_relation_extractor"] = cls.resolve_location(identifiers_dict["location_field"])

        return result


__all__ = [
    "Identifiers",
    "IdentifierResolver",
]
