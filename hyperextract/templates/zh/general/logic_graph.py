from typing import List, Optional
from pydantic import BaseModel, Field
from hyperextract.graphs import AutoGraph

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================

class LogicNode(BaseModel):
    """代表论点中的主张、证据或前提的节点。"""
    statement: str = Field(description="核心主张、事实或观察结果。")
    node_type: str = Field(
        description="节点类型：主张 (Claim), 证据 (Evidence), 前提 (Premise)。"
    )
    source_attribution: Optional[str] = Field(description="该逻辑点的来源或出处。")

class LogicRelation(BaseModel):
    """两个陈述之间的逻辑连接。"""
    source: str = Field(description="源陈述。")
    target: str = Field(description="目标陈述。")
    inference: str = Field(
        description="逻辑链路：支持 (Supports), 反驳 (Contradicts), 证明, 导致, 解释。"
    )

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

LOGIC_GRAPH_PROMPT = (
    "你是一位逻辑分析师。请将文本中的论证结构提取并转化为一个有向图。\n\n"
    "提取指南：\n"
    "- 识别主要主张（结论）以及引向这些结论的证据或前提。\n"
    "- 明确映射一个陈述是如何支持或反驳另一个陈述的。\n"
    "- 不仅要提取事实，更要提取“论证”和“推理”的流向。"
)

LOGIC_GRAPH_NODE_PROMPT = (
    "请提取论证中的各个基本构成要素。识别核心主张、支持性证据和底层前提。对于每一项，确定其类型并记录提及的任何来源出处。"
)

LOGIC_GRAPH_EDGE_PROMPT = (
    "映射提取出的主张与证据之间的逻辑流向。重点关注各个陈述之间是如何相互 支持、反驳 或 导致 彼此的。确保每条边都代表推理链中的一个步骤。"
)

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================

class LogicGraph(AutoGraph[LogicNode, LogicRelation]):
    """
    用于分析论文推理、论证和因果链的模板。
    适用于分析报告、辩论内容、科研推理及逻辑分析。
    """
    def __init__(self, **kwargs):
        super().__init__(
            node_schema=LogicNode,
            edge_schema=LogicRelation,
            node_key_extractor=lambda x: x.statement.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.inference.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            prompt=LOGIC_GRAPH_PROMPT,
            prompt_for_node_extraction=LOGIC_GRAPH_NODE_PROMPT,
            prompt_for_edge_extraction=LOGIC_GRAPH_EDGE_PROMPT,
            **kwargs
        )
