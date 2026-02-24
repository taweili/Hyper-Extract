"""编年事件链 - 提取带精确时间戳的原子事件，严格还原历史时间线。

适用于编年史、年表、大事记。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph


class EventNode(BaseModel):
    """历史事件节点"""
    name: str = Field(description="事件名称")
    category: str = Field(description="事件类型：战争、政治、外交、军事")
    description: str = Field(description="事件简要描述")


class TemporalEventEdge(BaseModel):
    """时序事件边"""
    source: str = Field(description="前置事件名称")
    target: str = Field(description="后续事件名称")
    time: str = Field(description="时间，格式为年份或朝代年份，如208年、建安十三年")
    location: str = Field(description="地点")
    description: str = Field(description="事件因果描述，说明两事件之间的逻辑关系")


_NODE_PROMPT = """## 角色与任务
请从文本中提取所有历史事件作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的历史事件
- **边 (Edge)**：事件之间的时间因果关系
- **时间**：年号年份（如208年、建安十三年）

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 事件类型：战争、政治、外交、军事等
- 事件要包含简要描述

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知事件列表中提取事件之间的时间因果关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的历史事件
- **边 (Edge)**：事件之间的时间因果关系
- **时间**：年号年份（如208年、建安十三年）

## 提取规则
### 核心约束
1. 仅从已知事件列表中提取边，不要创建未列出的人物
2. 关系描述应与原文保持一致

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月

2. 精确时间 → 保持原样
3. 时间缺失 → 留空，不要猜测

"""

_PROMPT = """## 角色与任务
你是一位专业的历史学专家，请从文本中提取历史事件以及它们之间的时间因果关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的历史事件
- **边 (Edge)**：事件之间的时间因果关系
- **时间**：年号年份（如208年、建安十三年）

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知事件列表中提取边，不要创建未列出的事件
4. 关系描述应与原文保持一致

### 领域特定规则
- 事件类型：战争、政治、外交、军事等
- 事件要包含简要描述

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月

2. 精确时间 → 保持原样
3. 时间缺失 → 留空，不要猜测

### 源文本:
"""


class ChronologicalEventChain(AutoTemporalGraph[EventNode, TemporalEventEdge]):
    """
    适用文档: 编年史、年表、大事记

    功能介绍:
    提取带精确时间戳的原子事件，严格还原历史时间线。

    设计说明:
    - 节点（EventNode）：存储事件信息，包括名称、类型、描述
    - 边（TemporalEventEdge）：存储事件之间的时间因果关系及时间点

    Example:
        >>> template = ChronologicalEventChain(llm_client=llm, embedder=embedder)
        >>> template.feed_text("建安十三年冬，曹操率军南下...")
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
        初始化编年事件链模板。

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
            node_schema=EventNode,
            edge_schema=TemporalEventEdge,
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
        展示编年事件链。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: EventNode) -> str:
            return node.name

        def edge_label_extractor(edge: TemporalEventEdge) -> str:
            return f"{edge.time}: {edge.description[:20]}..."

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
