"""叙事事件链 - 按故事内部时间线提取关键情节转折点 (Plot Points)。

适用于长篇小说。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph


class PlotPointNode(BaseModel):
    """情节转折点节点"""
    name: str = Field(description="事件名称")
    description: str = Field(description="事件描述")


class PlotEdge(BaseModel):
    """情节链边"""
    source: str = Field(description="前置事件")
    target: str = Field(description="后续事件")
    time: str = Field(description="故事内部时间点，如'第X章'、'第X日'、'第X年'")
    causeEffect: str = Field(description="因果关系描述")


_NODE_PROMPT = """## 角色与任务
请从长篇小说文本中提取所有情节转折点作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的情节转折点
- **边 (Edge)**：情节之间的因果关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 情节转折点：改变故事走向的关键事件

## 小说文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知情节列表中提取情节之间的因果关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的情节转折点
- **边 (Edge)**：情节之间的因果关系

## 提取规则
### 核心约束
1. 仅从已知情节列表中提取边，不要创建未列出的情节
2. 关系描述应与原文保持一致

### 时间解析规则
当前观测时间: {observation_time}
1. 章节格式：如"第一章"、"第3章" → 保持原样
2. 日期格式：如"第一日"、"第X日" → 保持原样
3. 年份格式：如"第一年"、"XX年" → 保持原样
4. 相对时间：如"随后"、"之后" → 留空，不要猜测

## 已知情节列表:
{known_nodes}

## 小说文本:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位专业的小说分析师，请从文本中提取情节转折点以及它们之间的因果关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的情节转折点
- **边 (Edge)**：情节之间的因果关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知情节列表中提取边，不要创建未列出的情节
4. 关系描述应与原文保持一致

### 领域特定规则
- 情节转折点：改变故事走向的关键事件

### 时间解析规则
当前观测时间: {observation_time}
1. 章节格式：如"第一章"、"第3章" → 保持原样
2. 日期格式：如"第一日"、"第X日" → 保持原样
3. 年份格式：如"第一年"、"XX年" → 保持原样
4. 相对时间：如"随后"、"之后" → 留空，不要猜测

## 小说文本:
{source_text}
"""


class NarrativeEventChain(AutoTemporalGraph[PlotPointNode, PlotEdge]):
    """
    适用文档: 长篇小说

    功能介绍:
    按故事内部时间线提取关键情节转折点 (Plot Points)。

    设计说明:
    - 节点（PlotPointNode）：存储情节转折点信息，包括名称、描述
    - 边（PlotEdge）：存储情节之间的因果关系及时间点

    Example:
        >>> template = NarrativeEventChain(llm_client=llm, embedder=embedder)
        >>> template.feed_text("梅长苏入京...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        observation_time: str | None = None,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化叙事事件链模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            observation_time: 观察时间，用于解析相对时间表达，
                如未指定则使用当前日期
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=PlotPointNode,
            edge_schema=PlotEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.time}|{x.target}",
            time_in_edge_extractor=lambda x: x.time,
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
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
        展示叙事事件链。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: PlotPointNode) -> str:
            return node.name

        def edge_label_extractor(edge: PlotEdge) -> str:
            return f"{edge.time}: {edge.causeEffect[:20]}..."

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
