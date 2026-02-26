"""观点逻辑结构 - 建模文章的论证逻辑：{核心观点, 支撑论据, 背景引用}。

适用于社论分析、舆情观点聚类。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class ArgumentElementNode(BaseModel):
    """论证元素节点"""

    name: str = Field(description="元素名称")
    category: str = Field(description="元素类型：观点、论据、背景引用")
    content: str = Field(description="内容")
    source: str = Field(description="来源", default="")


class ViewpointHyperedge(BaseModel):
    """观点结构超边"""

    coreViewpoint: str = Field(description="核心观点")
    supportingEvidences: List[str] = Field(description="支撑论据列表")
    backgroundCitations: List[str] = Field(description="背景引用列表")
    source: str = Field(description="观点来源（专家/机构名称）", default="")
    description: str = Field(description="论证描述")


_NODE_PROMPT = """## 角色与任务
请从政策分析或社论文本中提取所有论证元素作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的论证元素
- **边 (Edge)**：连接多个元素的超边，表示完整的论证结构

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的元素，禁止将多个元素合并为一个节点
2. 元素名称与原文保持一致

### 领域特定规则
- 元素类型：观点（核心论点）、论据（支撑观点的证据或分析）、背景引用（政策、数据、专家说法）
- 内容要完整概括原文意思
- 来源如无则为空白

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知论证元素列表中提取观点结构的超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的论证元素
- **边 (Edge)**：连接多个元素的超边，表示完整的论证结构

## 提取规则
### 核心约束
1. 超边必须包含至少一个论据或背景引用
2. 超边必须包含核心观点
3. 仅从已知元素列表中提取边，不要创建未列出的元素
4. 描述应与原文保持一致

### 领域特定规则
- 论据：支撑观点的证据或分析
- 背景引用：政策文件、统计数据、专家说法
- 观点：作者的核心论点

"""

_PROMPT = """## 角色与任务
你是一位专业的政策分析师，请从文本中提取论证元素以及它们组成的观点结构超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的论证元素
- **边 (Edge)**：连接多个元素的超边，表示完整的论证结构

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的元素，禁止将多个元素合并为一个节点
2. 元素名称与原文保持一致
3. 超边必须包含至少一个论据或背景引用
4. 超边必须包含核心观点
5. 仅从已知元素列表中提取边，不要创建未列出的元素
6. 描述应与原文保持一致

### 领域特定规则
- 元素类型：观点、论据、背景引用
- 论据：支撑观点的证据或分析
- 背景引用：政策文件、统计数据、专家说法
- 观点：作者的核心论点

### 源文本:
"""


class ViewpointStructure(AutoHypergraph[ArgumentElementNode, ViewpointHyperedge]):
    """
    适用文档: 政策分析、社论、舆情文章

    功能介绍:
    建模文章的论证逻辑：{核心观点, 支撑论据, 背景引用}。

    设计说明:
    - 节点（ArgumentElementNode）：存储论证元素信息，包括名称、类型、内容、来源
    - 边（ViewpointHyperedge）：存储观点结构信息，包括核心观点、论据、引用、描述

    Example:
        >>> template = ViewpointStructure(llm_client=llm, embedder=embedder)
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
        初始化观点逻辑结构模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """

        def nodes_in_edge_extractor(edge: ViewpointHyperedge) -> set:
            nodes = set()
            nodes.add(edge.coreViewpoint)
            nodes.update(edge.supportingEvidences)
            nodes.update(edge.backgroundCitations)
            return nodes

        super().__init__(
            node_schema=ArgumentElementNode,
            edge_schema=ViewpointHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.coreViewpoint[:30],
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
        展示观点逻辑结构。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: ArgumentElementNode) -> str:
            return f"{node.name}[{node.category}]"

        def edge_label_extractor(edge: ViewpointHyperedge) -> str:
            return f"观点: {edge.coreViewpoint[:20]}..."

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
