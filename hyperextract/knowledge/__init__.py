"""Knowledge extraction framework.

This package provides a hierarchical knowledge extraction framework:
    - generic: Base knowledge patterns (UnitKnowledge, ListKnowledge, SetKnowledge)
    - typical: Common knowledge types (EntityKnowledge, RelationKnowledge)
    - domain: Domain-specific knowledge patterns (reserved for future use)
    - graph: Graph-based knowledge structures
    - hypergraph: Hypergraph-based knowledge structures

Usage:
    All main classes can be imported directly from hyperextract.knowledge:
    
    >>> from hyperextract.knowledge import UnitKnowledge, ListKnowledge, EntityKnowledge
    >>> from hyperextract.knowledge import SimpleGraph
"""

from .base import BaseKnowledge

# Generic patterns
from .generic import UnitKnowledge, ListKnowledge, ItemListSchema

# Typical patterns
from .typical import EntityKnowledge

# Graph patterns
from .graph.base import SimpleGraph, Entity, Relationship, GraphSchema

__all__ = [
    # Base
    "BaseKnowledge",
    
    # Generic patterns
    "UnitKnowledge",
    "ListKnowledge",
    "ItemListSchema",
    
    # Typical patterns
    "EntityKnowledge",
    
    # Graph patterns
    "SimpleGraph",
    "Entity",
    "Relationship",
    "GraphSchema",
]
