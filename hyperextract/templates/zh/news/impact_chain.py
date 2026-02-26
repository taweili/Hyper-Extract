"""影响推演链 - 提取"政策/事件 -> 影响群体 -> 预期后果"的因果预测链条。

适用于宏观政策解读、行业影响评估。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class ImpactNode(BaseModel):
    """影响节点"""

    name: str = Field(description="节点名称")
    category: str = Field(description="节点类型：政策/事件、影响群体、预期后果")
    description: str = Field(description="描述")


class ImpactEdge(BaseModel):
    """影响边"""

    source: str = Field(description="原因")
    target: str = Field(description="结果")
    relationType: str = Field(description="关系类型：影响、导致、预期")
    description: str = Field(description="影响描述")


_NODE_PROMPT = """## 角色与任务
请从政策分析文本中提取所有影响链相关实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的影响链实体
- **边 (Edge)**：实体之间的因果关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 节点类型：政策/事件（政策文件、重大事件）、影响群体（企业、消费者、经销商等）、预期后果（销量变化、价格调整、市场调整等）
- 描述要包含简要信息

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取因果影响关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的影响链实体
- **边 (Edge)**：实体之间的因果关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型：影响（政策对群体的影响）、导致（原因导致结果）、预期（对未来趋势的预测）
- 描述原因到结果的逻辑链条

"""

_PROMPT = """## 角色与任务
你是一位专业的政策分析师，请从政策分析文本中提取影响链实体和它们之间的因果关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的影响链实体
- **边 (Edge)**：实体之间的因果关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 节点类型：政策/事件、影响群体、预期后果
- 关系类型：影响、导致、预期

### 源文本:
"""


class ImpactChain(AutoGraph[ImpactNode, ImpactEdge]):
    """
    适用文档: 政策解读、行业分析报告

    功能介绍:
    提取"政策/事件 -> 影响群体 -> 预期后果"的因果预测链条。

    设计说明:
    - 节点（ImpactNode）：存储影响链实体信息，包括名称、类型、描述
    - 边（ImpactEdge）：存储因果关系信息，包括原因、结果、关系类型、描述

    Example:
        >>> template = ImpactChain(llm_client=llm, embedder=embedder)
        >>> template.feed_text("某政策解读文章...")
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
        初始化影响推演链模板。

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
            node_schema=ImpactNode,
            edge_schema=ImpactEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
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
        展示影响推演链。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: ImpactNode) -> str:
            return f"{node.name}[{node.category}]"

        def edge_label_extractor(edge: ImpactEdge) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
