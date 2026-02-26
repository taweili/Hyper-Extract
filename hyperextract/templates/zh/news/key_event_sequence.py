"""调查事件脉络 - 按时间顺序还原调查中揭露的关键事件节点，梳理前因后果。

适用于深度调查报道、历史遗留问题揭秘。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class EventNode(BaseModel):
    """事件节点"""
    name: str = Field(description="事件名称")
    category: str = Field(description="事件类型：开工、销售、停工、诉讼、侦查、处罚、协调、公示")
    time: str = Field(description="时间，格式为年-月-日（如 2023-09-15）")
    description: str = Field(description="事件描述")


class EventSequenceEdge(BaseModel):
    """事件序列边"""
    source: str = Field(description="前置事件名称")
    target: str = Field(description="后续事件名称")
    relationType: str = Field(description="关系类型：紧接、导致、触发、升级、回应、协调、裁决、调查")
    description: str = Field(description="因果描述，说明两事件之间的逻辑关系")


_NODE_PROMPT = """## 角色与任务
请从调查报道文本中提取所有关键事件作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的关键事件
- **边 (Edge)**：事件之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的事件，禁止将多个事件合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 事件类型：开工、销售、停工、诉讼、侦查、处罚、协调、公示
- 时间格式：年-月-日（如 2023-09-15），精确到日
- 事件描述要包含简要信息

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知事件列表中提取事件之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的关键事件
- **边 (Edge)**：事件之间的关系

## 提取规则
### 核心约束
1. 仅从已知事件列表中提取边，不要创建未列出的事件
2. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型：紧接（紧接着发生）、导致（直接原因）、触发（导火索/间接原因）、升级（事态扩大）、回应（对某事件的回应）、协调（多方协商处理）、裁决（法律/官方判定）、调查（正在调查阶段）
- 描述两事件之间的具体逻辑关系

"""

_PROMPT = """## 角色与任务
你是一位专业的新闻调查记者，请从调查报道文本中提取关键事件以及它们之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的关键事件
- **边 (Edge)**：事件之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的事件，禁止将多个事件合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知事件列表中提取边，不要创建未列出的事件
4. 关系描述应与原文保持一致

### 领域特定规则
- 事件类型：开工、销售、停工、诉讼、侦查、处罚、协调、公示
- 时间格式：年-月-日（如 2023-09-15），精确到日
- 关系类型：紧接、导致、触发、升级、回应、协调、裁决、调查

### 源文本:
"""


class KeyEventSequence(AutoGraph[EventNode, EventSequenceEdge]):
    """
    适用文档: 深度调查报道、历史遗留问题揭秘

    功能介绍:
    按时间顺序还原调查中揭露的关键事件节点，梳理前因后果。

    设计说明:
    - 节点（EventNode）：存储事件信息，包括名称、类型、时间、描述
    - 边（EventSequenceEdge）：存储事件之间的关系及描述

    Example:
        >>> template = KeyEventSequence(llm_client=llm, embedder=embedder)
        >>> template.feed_text("某地产项目调查报道...")
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
        初始化调查事件脉络模板。

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
            node_schema=EventNode,
            edge_schema=EventSequenceEdge,
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
        展示调查事件脉络。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: EventNode) -> str:
            return f"{node.name} ({node.time})"

        def edge_label_extractor(edge: EventSequenceEdge) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
