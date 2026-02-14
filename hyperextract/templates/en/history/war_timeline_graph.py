"""War Timeline Graph - Extracts temporal relationships in historical conflicts.

Captures territorial changes, leadership transitions, and military events with
time boundaries for precise historical analysis.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

class HistoricalEntitySchema(BaseModel):
    entity_id: str = Field(..., description="Unique identifier")
    entity_type: str = Field(..., description="'Polity' (state), 'City' (location), or 'General' (person)")
    entity_name: str = Field(..., description="Name of the entity")

class TemporalEventSchema(BaseModel):
    source_entity: str = Field(..., description="Acting entity")
    target_entity: str = Field(..., description="Affected entity")
    edge_type: str = Field(..., description="'Occupied', 'Ruled_By', 'Besieged', etc.")
    start_timestamp: Optional[int] = Field(None, description="Start year or timestamp")
    end_timestamp: Optional[int] = Field(None, description="End year (if applicable)")
    description: Optional[str] = Field(None, description="Event details")

_PROMPT = """Extract historical entities (Nodes) and temporal events (Edges) showing
territorial control and leadership changes during the specified period.

For Nodes, extract: polities, cities, and key military leaders.
For Edges, extract relationships with time boundaries:
- start_timestamp: Begin year of the event
- end_timestamp: End year (leave empty if ongoing)
Ensure all edges connect nodes that exist in the extracted nodes list.

### Source Text:
"""

_NODE_PROMPT = """Extract all historical entities mentioned: polities (states), cities,
and military leaders. Include their names and basic descriptions."""

_EDGE_PROMPT = """Extract temporal relationships between the known entities.
For each relationship, provide exact year ranges when available.
Only connect entities from the known entity list provided."""

class WarTimelineGraph(AutoTemporalGraph[HistoricalEntitySchema, TemporalEventSchema]):
    """Applicable to: Historical chronicles, War records, Textbook chapters

    Extracts temporal knowledge graph capturing territorial control and military
    events with precise time boundaries for historical analysis.
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        observation_time: str = "2024-01-01",
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        super().__init__(
            node_schema=HistoricalEntitySchema,
            edge_schema=TemporalEventSchema,
            node_key_extractor=lambda x: x.entity_name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source_entity.lower()}|{x.edge_type.lower()}|{x.target_entity.lower()}"
            ),
            time_in_edge_extractor=lambda x: f"{x.start_timestamp or ''}",
            nodes_in_edge_extractor=lambda x: (x.source_entity.lower(), x.target_entity.lower()),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(self, *, top_k_for_search: int = 5, top_k_for_chat: int = 5) -> None:
        def node_label(node: HistoricalEntitySchema) -> str:
            return f"{node.entity_name} ({node.entity_type})"
        def edge_label(edge: TemporalEventSchema) -> str:
            return f"{edge.edge_type} ({edge.start_timestamp or '?'})"
        super().show(
            node_label_extractor=node_label,
            edge_label_extractor=edge_label,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
