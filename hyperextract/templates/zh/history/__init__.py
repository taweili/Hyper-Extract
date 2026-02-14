"""History domain templates for knowledge extraction."""

from .cultural_artifact_registry import CulturalArtifactRegistry
from .war_timeline_graph import WarTimelineGraph
from .diplomatic_event_hypergraph import DiplomaticEventHypergraph

__all__ = [
    "CulturalArtifactRegistry",
    "WarTimelineGraph",
    "DiplomaticEventHypergraph",
]
