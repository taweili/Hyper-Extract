from typing import Dict, List
from pydantic import BaseModel
from .base import VALID_MERGE_STRATEGIES, FieldSchema


class NaiveGuidelineSchema(BaseModel):
    target: str | List[str] | Dict[str, str]
    rules: str | List[str] | Dict[str, str | List[str]]


class NaiveOutputSchema(BaseModel):
    description: str | Dict[str, str]
    fields: List[FieldSchema]


class NaiveOptionsSchema(BaseModel):
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    max_workers: int | None = None
    verbose: bool | None = None
    merge_strategy: VALID_MERGE_STRATEGIES | None = None
    fields_for_search: List[str] | None = None


class NaiveDisplaySchema(BaseModel):
    label: str


class NaiveIdentifierSchema(BaseModel):
    item_id: str
