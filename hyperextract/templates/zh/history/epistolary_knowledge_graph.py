"""信札内容图谱 - 提取信件正文中提到的人物、事件及其相互关系。

适用于档案馆藏信札、历史人物书信集。
"""

from datetime import datetime
from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph


class CorrespondentNode(BaseModel):
    """书信人物节点"""
    name: str = Field(description="人物姓名")
    identity: str = Field(description="身份描述，如北宋文学家、东吴大都督", default="")
    description: str = Field(description="人物描述", default="")


class LetterContentEdge(BaseModel):
    """书信内容边"""
    source: str = Field(description="发信人")
    target: str = Field(description="收信人")
    time: str = Field(description="时间", default="")
    subject: str = Field(description="信件主题或主要议题")
    mentionedPersons: List[str] = Field(description="信中提及的人物", default_factory=list)
    mentionedEvents: List[str] = Field(description="信中提及的事件", default_factory=list)
    summary: str = Field(description="信件内容摘要")


_NODE_PROMPT = """## 角色与任务
请从文本中提取书信中的人物作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的书信相关人物
- **边 (Edge)**：书信内容及其中提及的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 人物要包含身份描述

## 源文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知人物列表中提取书信内容关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的书信相关人物
- **边 (Edge)**：书信内容及其中提及的关系
- **时间**：信件书写或发送的时间

## 提取规则
### 核心约束
1. 仅从已知人物列表中提取边，不要创建未列出的人物
2. 关系描述应与原文保持一致

### 领域特定规则
- 信件主题：信件讨论的主要议题
- 提及人物：必须仔细阅读信件正文，提取正文中明确提到的人物姓名，整理为列表
- 提及事件：必须仔细阅读信件正文，提取正文中明确提到的事件，整理为列表
- 内容摘要：信件的主要内容概括
- 重要：如果正文未提及，则留空列表，不要编造

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月
   - "本季度" → {observation_time} 所在季度
   - "近期" → {observation_time} 最近 3 个月

2. 精确时间 → 保持原样
3. 时间缺失 → 留空，不要猜测

## 已知人物列表：
{known_nodes}

## 源文本:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位专业的历史学专家，请从文本中提取书信中的人物以及书信内容关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的书信相关人物
- **边 (Edge)**：书信内容及其中提及的关系
- **时间**：信件书写或发送的时间

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知人物列表中提取边，不要创建未列出的人物
4. 关系描述应与原文保持一致

### 领域特定规则
- 人物要包含身份描述
- 信件主题：信件讨论的主要议题
- 提及人物：必须仔细阅读信件正文，提取正文中明确提到的人物姓名，整理为列表
- 提及事件：必须仔细阅读信件正文，提取正文中明确提到的事件，整理为列表
- 内容摘要：信件的主要内容概括
- 重要：如果正文未提及，则留空列表，不要编造

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月
   - "本季度" → {observation_time} 所在季度
   - "近期" → {observation_time} 最近 3 个月

2. 精确时间 → 保持原样
3. 时间缺失 → 留空，不要猜测

## 源文本:
{source_text}
"""


class EpistolaryKnowledgeGraph(AutoTemporalGraph[CorrespondentNode, LetterContentEdge]):
    """
    适用文档: 档案馆藏信札、历史人物书信集

    功能介绍:
    提取信件正文中提到的人物、事件及其相互关系，而非仅仅是发信和收信关系，适用于史料挖掘、事件考证。

    设计说明:
    - 节点（CorrespondentNode）：存储书信相关人物信息
    - 边（LetterContentEdge）：存储信件内容及提及的人物事件

    Example:
        >>> template = EpistolaryKnowledgeGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("苏轼致司马光书：论科举之法...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        observation_time: str | None = None,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化信札内容图谱模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            observation_time: 观察时间，用于解析相对时间表达，
                如未指定则使用当前日期
            chunk_size: 每个分块的最大字符数，默认为 512（历史文本信息量大，需较小分块）
            chunk_overlap: 分块之间的重叠字符数，默认为 64
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        if observation_time is None:
            observation_time = datetime.now().strftime("%Y-%m-%d")

        super().__init__(
            node_schema=CorrespondentNode,
            edge_schema=LetterContentEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.subject}|{x.target}",
            time_in_edge_extractor=lambda x: x.time or "",
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
        展示信札内容图谱。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: CorrespondentNode) -> str:
            return node.name

        def edge_label_extractor(edge: LetterContentEdge) -> str:
            if edge.time:
                return f"{edge.subject} （{edge.time}）"
            return f"{edge.subject}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
