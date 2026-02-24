"""多方事件超图 - 将历史事件建模为连接多个参与者的超边结构。

适用于历史专著、战役记录、重大事件档案。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class EventParticipantNode(BaseModel):
    """事件参与者节点"""
    name: str = Field(description="参与者姓名或名称")
    role: str = Field(description="角色定位，如主将、谋士、使者、参战方")
    faction: str = Field(description="所属阵营", default="")
    description: str = Field(description="参与者描述，包括身份背景和在事件中的角色说明", default="")


class EventHyperedge(BaseModel):
    """事件超边"""
    eventName: str = Field(description="事件名称，如赤壁之战、鸿门宴")
    time: str = Field(description="发生时间，如建安十三年冬")
    location: str = Field(description="发生地点")
    description: str = Field(description="事件概述，描述事件背景、经过和结果")
    participants: List[str] = Field(description="参与者列表，与节点对应")


_NODE_PROMPT = """## 角色与任务
请从文本中提取历史事件中的参与者作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的事件参与者实体
- **边 (Edge)**：连接多个参与者的超边，表示一个完整的事件

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 参与者要标注角色定位（主将、谋士、使者等）
- 参与者要标注所属阵营

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知参与者列表中提取多方参与的事件超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的事件参与者实体
- **边 (Edge)**：连接多个参与者的超边，表示一个完整的事件

## 提取规则
### 核心约束
1. 超边必须连接2个或以上的参与者
2. 仅从已知参与者列表中提取边，不要创建未列出的参与者
3. 关系描述应与原文保持一致

### 领域特定规则
- 一个超边代表一个完整的历史事件
- 需要包含事件的时间、地点、背景和结果

"""

_PROMPT = """## 角色与任务
你是一位专业的历史学专家，请从文本中提取历史事件中的参与者以及他们组成的事件超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的事件参与者实体
- **边 (Edge)**：连接多个参与者的超边，表示一个完整的事件

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 超边必须连接2个或以上的参与者
4. 仅从已知参与者列表中提取边，不要创建未列出的参与者
5. 关系描述应与原文保持一致

### 领域特定规则
- 参与者要标注角色定位（主将、谋士、使者等）
- 参与者要标注所属阵营
- 一个超边代表一个完整的历史事件
- 需要包含事件的时间、地点、背景和结果

### 源文本:
"""


class MultiParticipantEventMap(AutoHypergraph[EventParticipantNode, EventHyperedge]):
    """
    适用文档: 历史专著、战役记录、重大事件档案

    功能介绍:
    将历史事件建模为连接多个参与者的超边，如赤壁之战连接曹操、孙权、刘备、周瑜等多方。

    设计说明:
    - 节点（EventParticipantNode）：存储参与者信息，包括姓名、角色、阵营、描述
    - 边（EventHyperedge）：存储完整的事件信息及所有参与者

    Example:
        >>> template = MultiParticipantEventMap(llm_client=llm, embedder=embedder)
        >>> template.feed_text("赤壁之战中，周瑜率吴军与曹操大战于长江...")
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
        初始化多方事件超图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            chunk_size: 每个分块的最大字符数，默认为 512（历史文本信息量大，需较小分块）
            chunk_overlap: 分块之间的重叠字符数，默认为 64
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        def nodes_in_edge_extractor(edge: EventHyperedge) -> set:
            return set(edge.participants)

        super().__init__(
            node_schema=EventParticipantNode,
            edge_schema=EventHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.eventName,
            nodes_in_edge_extractor=nodes_in_edge_extractor,
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
        展示多方事件超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: EventParticipantNode) -> str:
            return f"{node.name}({node.role})"

        def edge_label_extractor(edge: EventHyperedge) -> str:
            return f"{edge.eventName}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
