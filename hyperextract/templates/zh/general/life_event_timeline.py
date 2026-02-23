from typing import Any
from datetime import datetime
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import AutoTemporalGraph


class PersonEntity(BaseModel):
    """人物实体"""
    name: str = Field(description="人物姓名")
    description: str = Field(description="简要描述", default="")


class LifeEvent(BaseModel):
    """生活事件"""
    source: str = Field(description="相关人物")
    eventType: str = Field(description="事件类型：出生、教育、工作、婚姻、死亡等")
    eventName: str = Field(description="事件名称")
    timeInfo: str = Field(description="时间信息，统一格式为年-月-日（如 2023-06-15）")
    location: str = Field(description="事件地点", default="")
    description: str = Field(description="事件描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的生活事件提取专家，请从文本中提取人物及其生活事件。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指人物，包括人物姓名和简要描述。
- **边 (Edge)**：本模板中的"边"指生活事件，包括事件类型、名称、时间、地点和描述。

## 提取规则
### 节点提取规则
1. 提取所有人物，包括其姓名和简要描述
2. 保持人物姓名与原文一致

### 事件提取规则
1. 提取所有生活事件，包括事件类型、名称、时间、地点和描述
2. 每条事件必须连接相关的人物
3. 时间信息必须统一转换为「年-月-日」格式（如 2023-06-15）

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年，格式化为 YYYY-01-01
   - "上月" → {observation_time} 的前一个月，格式化为 YYYY-MM-01

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的人物识别专家，请从文本中提取所有人物作为节点。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指人物，包括人物姓名和简要描述。

## 提取规则
1. 提取所有人物，包括其姓名和简要描述
2. 保持人物姓名与原文一致

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的生活事件提取专家，请从给定人物列表中提取生活事件。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指人物，作为生活事件的参与者。
- **边 (Edge)**：本模板中的"边"指生活事件，包括事件类型、名称、时间、地点和描述。

## 提取规则
1. 仅从下方已知人物列表中提取事件
2. 每条事件必须连接相关的人物
3. 时间信息必须统一转换为「年-月-日」格式（如 2023-06-15）

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年，格式化为 YYYY-01-01
   - "上月" → {observation_time} 的前一个月，格式化为 YYYY-MM-01

"""


class LifeEventTimeline(AutoTemporalGraph[PersonEntity, LifeEvent]):
    """
    适用文档: 人物传记、历史人物资料、个人履历
    
    功能介绍:
    提取人物的生活事件时间线，如出生、教育、工作、婚姻、死亡等重要事件。
    
    Example:
        >>> template = LifeEventTimeline(llm_client=llm, embedder=embedder)
        >>> template.feed_text("...")
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
        初始化生活事件时间线模板。
        
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
        if observation_time is None:
            observation_time = datetime.now().strftime("%Y-%m-%d")
        
        super().__init__(
            node_schema=PersonEntity,
            edge_schema=LifeEvent,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.eventType}|{x.eventName}",
            time_in_edge_extractor=lambda x: x.timeInfo or "",
            nodes_in_edge_extractor=lambda x: (x.source, x.source),
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
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        展示生活事件时间线。
        
        Args:
            top_k_for_search: 语义检索返回的节点/边数量，默认为 3
            top_k_for_chat: 问答使用的节点/边数量，默认为 3
        """
        def node_label_extractor(node: PersonEntity) -> str:
            return node.name
        
        def edge_label_extractor(edge: LifeEvent) -> str:
            return f"{edge.eventType}: {edge.eventName}"
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )