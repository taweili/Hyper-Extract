"""Types - Core data structures for automatic knowledge extraction.

This module contains the fundamental, reusable data structure primitives that can 
automatically extract knowledge from text. These are the "building blocks" of the 
Hyper-Extract framework.
"""

from .base import BaseAutoType
from .model import AutoModel
from .list import AutoList, AutoListSchema
from .set import AutoSet, AutoSetSchema
from .graph import AutoGraph, AutoGraphSchema
from .hypergraph import AutoHypergraph, AutoHypergraphSchema
from .temporal_graph import AutoTemporalGraph
from .spatial_graph import AutoSpatialGraph
from .spatio_temporal_graph import AutoSpatioTemporalGraph

__all__ = [
    # Base class
    "BaseAutoType",
    # Scalar types
    "AutoModel",
    "AutoList",
    "AutoListSchema",
    "AutoSet",
    "AutoSetSchema",
    # Graph types
    "AutoGraph",
    "AutoGraphSchema",
    "AutoHypergraph",
    "AutoHypergraphSchema",
    "AutoTemporalGraph",
    "AutoSpatialGraph",
    "AutoSpatioTemporalGraph",
]
