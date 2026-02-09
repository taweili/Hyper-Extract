"""领域通用知识图谱模板。

本模块提供基础的信息提取模板，适用于多种场景：
- KnowledgeGraph: 事实实体-关系映射，适用于新闻、传记和百科。
- ConceptMap: 语义定义与分类体系，适用于技术文档和教育材料。
- LogicGraph: 推理分析、论证过程及因果链，适用于分析性文本。
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
