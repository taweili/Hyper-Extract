"""General purpose knowledge graph templates.

This module provides foundational templates for general information extraction:
- KnowledgeGraph: Factual entity-relationship mapping for news and biographies.
- ConceptMap: Semantic definitions and taxonomies for technical/educational content.
- LogicGraph: Analysis of reasoning, arguments, and causal chains in analytical text.
"""

from .knowledge_graph import KnowledgeGraph, Entity, Relation
from .concept_map import ConceptMap, Concept, ConceptRelation
from .logic_graph import LogicGraph, LogicNode, LogicRelation

__all__ = [
    "KnowledgeGraph",
    "Entity",
    "Relation",
    "ConceptMap",
    "Concept",
    "ConceptRelation",
    "LogicGraph",
    "LogicNode",
    "LogicRelation",
]
