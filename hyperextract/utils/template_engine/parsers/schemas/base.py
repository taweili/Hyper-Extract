from typing import Any, Dict, Literal
from pydantic import BaseModel


VALID_MERGE_STRATEGIES = Literal[
    "merge_field",
    "keep_incoming",
    "keep_existing",
    "llm_balanced",
    "llm_prefer_incoming",
    "llm_prefer_existing",
]
VALID_AUTOTYPES = Literal[
    "model",
    "list",
    "set",
    "graph",
    "hypergraph",
    "temporal_graph",
    "spatial_graph",
    "spatio_temporal_graph",
]


class FieldSchema(BaseModel):
    name: str
    type: Literal["str", "int", "float", "bool", "list", "dict"]
    description: str | Dict[str, str]
    required: bool = False
    default: Any | None = None
