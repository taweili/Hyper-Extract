"""复杂关系网络 - 建模涉及多方（三人及以上）的社会关联。

适用于人物特稿、政商关系分析。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class ParticipantNode(BaseModel):
    """参与者节点"""

    name: str = Field(description="参与者名称")
    role: str = Field(description="角色：企业、个人、机构")
    description: str = Field(description="参与者描述", default="")


class ComplexRelationHyperedge(BaseModel):
    """复杂关系超边"""

    relationType: str = Field(
        description="关系类型：商业伙伴、政治盟友、家族成员、投资关系、担保关系"
    )
    participants: List[str] = Field(description="参与者列表（3个及以上）")
    description: str = Field(description="关系描述")


_NODE_PROMPT = """## 角色与任务
请从调查报道文本中提取所有参与者作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的参与者实体
- **边 (Edge)**：连接多个参与者的超边，表示复杂的社会关联

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 参与者类型：企业、个人、机构
- 参与者描述要包含基本背景信息

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知参与者列表中提取涉及多方（3人及以上）的复杂关系超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的参与者实体
- **边 (Edge)**：连接多个参与者的超边，表示复杂的社会关联

## 提取规则
### 核心约束
1. 超边必须包含至少3个参与者
2. 仅从已知参与者列表中提取边，不要创建未列出的参与者
3. 描述应与原文保持一致

### 领域特定规则
- 关系类型：商业伙伴、政治盟友、家族成员、投资关系、担保关系
- 描述多方之间的具体关联

"""

_PROMPT = """## 角色与任务
你是一位专业的新闻调查记者，请从调查报道文本中提取参与者以及它们之间的复杂关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的参与者实体
- **边 (Edge)**：连接多个参与者的超边，表示复杂的社会关联

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 超边必须包含至少3个参与者
4. 仅从已知参与者列表中提取边，不要创建未列出的参与者
5. 描述应与原文保持一致

### 领域特定规则
- 参与者类型：企业、个人、机构
- 关系类型：商业伙伴、政治盟友、家族成员、投资关系、担保关系

### 源文本:
"""


class ComplexRelationNet(AutoHypergraph[ParticipantNode, ComplexRelationHyperedge]):
    """
    适用文档: 人物特稿、政商关系分析

    功能介绍:
    建模涉及多方（三人及以上）的社会关联（如家族、政治盟友、商业伙伴），而非简单的点对点关系。

    设计说明:
    - 节点（ParticipantNode）：存储参与者信息，包括名称、角色、描述
    - 边（ComplexRelationHyperedge）：存储复杂关系信息，包括参与者列表及关系描述

    Example:
        >>> template = ComplexRelationNet(llm_client=llm, embedder=embedder)
        >>> template.feed_text("某地产项目调查报道...")
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
        初始化复杂关系网络模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"

            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """

        def nodes_in_edge_extractor(edge: ComplexRelationHyperedge) -> set:
            return set(edge.participants)

        super().__init__(
            node_schema=ParticipantNode,
            edge_schema=ComplexRelationHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.relationType}|{len(x.participants)}",
            nodes_in_edge_extractor=nodes_in_edge_extractor,
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
        展示复杂关系网络。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: ParticipantNode) -> str:
            return f"{node.name}[{node.role}]"

        def edge_label_extractor(edge: ComplexRelationHyperedge) -> str:
            return f"{edge.relationType}: {len(edge.participants)}人"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
