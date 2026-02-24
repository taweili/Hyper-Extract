"""违规处罚因果链 - 描述从“违规行为”到“处理程序”再到“最终结果”的演变路径。

适用于风险溯源、处罚逻辑分析等。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class PenaltyNode(BaseModel):
    """处罚因果节点"""

    name: str = Field(description="节点名称")
    type: str = Field(description="节点类型：违规行为、处理程序、处罚结果、其他")
    description: str = Field(description="详细描述")


class PenaltyPath(BaseModel):
    """处罚因果路径边"""

    source: str = Field(description="源节点名称")
    target: str = Field(description="目标节点名称")
    relation: str = Field(description="关系类型：导致、触发、执行、产生、其他")
    details: str = Field(description="详细说明", default="")


_PROMPT = """## 角色与任务
你是一位专业的处罚逻辑分析专家，请从文本中提取违规处罚的因果链。

## 核心概念定义
- **节点 (Node)**：处罚因果链中的关键单元，包括类型如违规行为、处理程序、处罚结果等，用于表示处罚过程中的关键环节
- **边 (Edge)**：节点之间的因果关系，包括导致、触发、执行、产生等二元关系，用于表示从违规到处罚的演变路径

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 节点提取规则
1. 提取所有关键节点
2. 为每个节点指定类型

### 边提取规则
1. 仅从提取的节点中创建因果路径边
2. 记录节点之间的因果关系
3. 关系描述应与原文保持一致

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取处罚因果链的关键节点。

## 核心概念定义
- **节点 (Node)**：处罚因果链中的关键单元，包括类型如违规行为、处理程序、处罚结果等

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 节点提取规则
1. 提取所有关键节点
2. 为每个节点指定类型

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知节点列表中提取节点之间的因果关系。

## 核心概念定义
- **节点 (Node)**：处罚因果链中的关键单元，作为因果关系的参与者
- **边 (Edge)**：节点之间的因果关系，包括导致、触发、执行、产生等二元关系

## 提取规则
### 核心约束
1. 仅从已知节点列表中提取边，不要创建未列出的节点
2. 关系描述应与原文保持一致

### 关系类型说明
- Causes：导致
- Triggers：触发
- Executes：执行
- Produces：产生
- Other：其他

"""



class PenaltyMapping(AutoGraph[PenaltyNode, PenaltyPath]):
    """
    适用文档: 公司内部管理制度、行政法规、合规指南、处罚案例

    功能介绍:
    描述从“违规行为”到“处理程序”再到“最终结果”的演变路径。适用于风险溯源、处罚逻辑分析等。

    Example:
        >>> template = PenaltyMapping(llm_client=llm, embedder=embedder)
        >>> template.feed_text("宇宙第一摸鱼公司员工处罚条例...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化违规处罚因果链模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=PenaltyNode,
            edge_schema=PenaltyPath,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relation}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ):
        """
        展示违规处罚因果链。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: PenaltyNode) -> str:
            return f"{node.name} ({node.type})"

        def edge_label_extractor(edge: PenaltyPath) -> str:
            return edge.relation

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
