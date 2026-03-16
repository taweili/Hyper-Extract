from typing import Dict, List
from pydantic import BaseModel
from .base import VALID_MERGE_STRATEGIES
from .naive import NaiveOutputSchema


class GraphGuidelineSchema(BaseModel):
    target: str | List[str] | Dict[str, str]
    rules_for_entities: str | List[str] | Dict[str, str | List[str]]
    rules_for_relations: str | List[str] | Dict[str, str | List[str]]
    # Only for AutoTemporalGraph, AutoSpatioTemporalGraph
    rules_for_time: str | List[str] | Dict[str, str | List[str]] | None = None
    # Only for AutoSpatialGraph, AutoSpatioTemporalGraph
    rules_for_location: str | List[str] | Dict[str, str | List[str]] | None = None


class GraphOutputSchema(BaseModel):
    description: str | Dict[str, str]
    entities: NaiveOutputSchema
    relations: NaiveOutputSchema


class GraphOptionsSchema(BaseModel):
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    max_workers: int | None = None
    verbose: bool | None = None
    entity_merge_strategy: VALID_MERGE_STRATEGIES | None = None
    relation_merge_strategy: VALID_MERGE_STRATEGIES | None = None
    extraction_mode: str | None = None
    entity_fields_for_search: List[str] | None = None
    relation_fields_for_search: List[str] | None = None
    # Only for AutoTemporalGraph, AutoSpatioTemporalGraph
    observation_time: str | None = None
    # Only for AutoSpatialGraph, AutoSpatioTemporalGraph
    observation_location: str | None = None


class GraphDisplaySchema(BaseModel):
    entity_label: str
    relation_label: str


class GraphIdentifiersSchema(BaseModel):
    entity_id: str = None
    relation_id: str = None
    relation_members: str | Dict[str, str] | List[str] = None
    # Only for AutoTemporalGraph, AutoSpatioTemporalGraph
    time_field: str | None = None
    # Only for AutoSpatialGraph, AutoSpatioTemporalGraph
    location_field: str | None = None
