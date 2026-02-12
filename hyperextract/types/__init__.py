"""Types - Core data structures for automatic knowledge extraction.

This module contains the fundamental, reusable data structure primitives that can
automatically extract knowledge from text. These are the "building blocks" of the
Hyper-Extract framework.
"""

from .base import BaseAutoType
from .model import AutoModel
from .list import AutoList
from .set import AutoSet
from .graph import AutoGraph
from .hypergraph import AutoHypergraph
from .temporal_graph import AutoTemporalGraph
from .spatial_graph import AutoSpatialGraph
from .spatio_temporal_graph import AutoSpatioTemporalGraph

__all__ = [
    # Base class
    "BaseAutoType",
    # Scalar types
    "AutoModel",
    # Collection types
    "AutoList",
    "AutoSet",
    # Graph types
    "AutoGraph",
    "AutoTemporalGraph",
    "AutoSpatialGraph",
    "AutoSpatioTemporalGraph",
    # Hypergraph type
    "AutoHypergraph",
]
