"""实时动态时间轴 - 针对正在发生的事件，提取分钟级更新。

适用于直播贴整理、实时监控。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class UpdatePointNode(BaseModel):
    """更新节点"""
    time: str = Field(description="时间点，格式为HH:MM")
    event: str = Field(description="事件内容")
    name: str = Field(description="简短名称/摘要")
    speaker: str = Field(description="发言人", default="")


class TimelineEdge(BaseModel):
    """时间轴边"""
    source: str = Field(description="源时间点（格式为HH:MM）")
    target: str = Field(description="目标时间点（格式为HH:MM）")
    relationType: str = Field(description="关系类型：开场、介绍、发布、发言、提问、回答、总结、结束")
    description: str = Field(description="详细描述")


_NODE_PROMPT = """## 角色与任务
请从实时直播文本中提取所有时间更新点作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的时间更新点
- **边 (Edge)**：时间点之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的时间点，禁止将多个时间点合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 时间格式：HH:MM（24小时制）
- 事件内容要包含详细信息
- 简短名称要简洁明了
- 发言人如无则为空白

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知时间点列表中提取时间轴边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的时间更新点
- **边 (Edge)**：时间点之间的关系

## 提取规则
### 核心约束
1. 仅从已知时间点列表中提取边，不要创建未列出的时间点
2. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型：开场（会议开始）、介绍（介绍环节）、发布（正式发布）、发言（领导/发言人讲话）、提问（记者提问）、回答（回应问题）、总结（总结陈词）、结束（会议结束）
- 描述两时间点之间的具体关系

"""

_PROMPT = """## 角色与任务
你是一位专业的新闻直播编辑，请从实时直播文本中提取时间更新点以及它们之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的时间更新点
- **边 (Edge)**：时间点之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的时间点，禁止将多个时间点合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知时间点列表中提取边，不要创建未列出的时间点
4. 关系描述应与原文保持一致

### 领域特定规则
- 时间格式：HH:MM（24小时制）
- 事件内容要包含详细信息
- 简短名称要简洁明了
- 关系类型：开场、介绍、发布、发言、提问、回答、总结、结束
- 发言人如无则为空白

### 源文本:
"""


class LiveUpdateTimeline(AutoGraph[UpdatePointNode, TimelineEdge]):
    """
    适用文档: 直播贴、实时新闻更新

    功能介绍:
    针对正在发生的事件（如直播、发布会），提取分钟级时间更新。

    设计说明:
    - 节点（UpdatePointNode）：存储时间点信息，包括时间、事件、名称、发言人
    - 边（TimelineEdge）：存储时间点之间的关系及描述

    Example:
        >>> template = LiveUpdateTimeline(llm_client=llm, embedder=embedder)
        >>> template.feed_text("某发布会直播...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化实时动态时间轴模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            chunk_size: 每个分块的最大字符数，默认为 512
            chunk_overlap: 分块之间的重叠字符数，默认为 64
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=UpdatePointNode,
            edge_schema=TimelineEdge,
            node_key_extractor=lambda x: x.time,
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
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
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
        展示实时动态时间轴。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: UpdatePointNode) -> str:
            return f"{node.time} {node.name}"

        def edge_label_extractor(edge: TimelineEdge) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
