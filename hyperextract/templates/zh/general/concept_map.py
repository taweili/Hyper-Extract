from typing import List, Optional
from pydantic import BaseModel, Field
from hyperextract.graphs import AutoGraph

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================

class Concept(BaseModel):
    """一个代表术语、想法或理论的概念节点。"""
    term: str = Field(description="技术术语或概念的名称。")
    definition: str = Field(description="该概念的正式定义或解释。")
    examples: Optional[List[str]] = Field(default_factory=list, description="说明该概念的示例。")
    attributes: Optional[List[str]] = Field(default_factory=list, description="该概念的关键特征或属性。")

class ConceptRelation(BaseModel):
    """两个概念之间的语义关系。"""
    source: str = Field(description="源概念。")
    target: str = Field(description="目标概念。")
    relation_type: str = Field(
        description="关系类型（例如：是一种 (is-a), 属于 (part-of), 相关于, 用于, 为...的实例）。"
    )

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

CONCEPT_MAP_PROMPT = (
    "你是一位语义建模专家。请从文本中提取概念图（Concept Map），重点关注术语定义及其层级或关联关系。\n\n"
    "提取指南：\n"
    "- 识别核心术语，并基于文本提供精确定义。\n"
    "- 使用标准的语义关系词，如“是一种”（继承关系）或“属于”（组成关系）。\n"
    "- 如果文本提到了说明性的示例，请一并捕获。"
)

CONCEPT_MAP_NODE_PROMPT = (
    "请从文本中提取所有基础概念和技术术语。对于每个概念，提供其术语名称、精确定义、关键属性列表，"
    "以及文本中提到的任何具体示例。"
)

CONCEPT_MAP_EDGE_PROMPT = (
    "在提供的概念之间建立语义关系。重点关注层级分类（是一种、属于）以及功能性关联（用于、为...的实例）。"
    "确保边逻辑上连接了已定义的各个概念。"
)

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================

class ConceptMap(AutoGraph[Concept, ConceptRelation]):
    """
    用于构建概念图谱和分类体系的模板。
    适用于技术文档、教育材料、术语表解析等场景。
    """
    def __init__(self, **kwargs):
        super().__init__(
            node_schema=Concept,
            edge_schema=ConceptRelation,
            node_key_extractor=lambda x: x.term.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.relation_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            prompt=CONCEPT_MAP_PROMPT,
            prompt_for_node_extraction=CONCEPT_MAP_NODE_PROMPT,
            prompt_for_edge_extraction=CONCEPT_MAP_EDGE_PROMPT,
            **kwargs
        )
