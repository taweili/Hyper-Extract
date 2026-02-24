from typing import Any, Optional
from datetime import datetime
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import AutoTemporalGraph


class LifeEntity(BaseModel):
    """生活实体节点"""

    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型：人物、地点、组织、物品、概念、其他")
    description: str = Field(description="简要描述", default="")


class LifeEvent(BaseModel):
    """生活事件边（带可选时间戳）"""

    source: str = Field(description="事件主体/相关实体")
    target: str = Field(description="事件对象/相关实体")
    eventType: str = Field(
        description="事件类型：出生、逝世、教育、工作、成就、交往、旅行、其他"
    )
    eventDate: Optional[str] = Field(
        description="事件日期，格式为年-月-日或年份，可选", default=None
    )
    details: str = Field(description="事件详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的传记年表专家，请从文本中提取人物、地点、组织等实体以及生活事件。

## 核心概念定义
- **节点 (Node)**：人物、地点、组织等实体
- **边 (Edge)**：生活事件
- **时间**：事件发生的时间

## 提取规则
### 节点提取规则
1. 提取所有相关实体
2. 为每个实体指定类型

### 事件提取规则
1. 仅从提取的实体中创建事件边
2. 每条边必须连接已提取的节点
3. 时间信息为可选，仅在文本中明确提及时才提取

### 时间解析规则
当前观察日期：{observation_time}

1. 相对时间解析（基于观察日期）：
   - "去年" → {observation_time} 前一年
   - "今年" → {observation_time} 所属年份
   - "明年" → {observation_time} 后一年
   - "昨天/今天/明天" → {observation_time} 前/当/后一天
   - "十年前/五年后" → {observation_time} 前/后相应年数
   - "年初/年末" → 当年 1月1日/12月31日
   - "朝代" → 保留朝代名称

2. 明确日期：保持原格式
   - 年份（如 429年、2023年）→ 429、2023
   - 年-月-日 → 保持原格式

3. 缺失时间：留空

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取人物、地点、组织等实体作为节点。

## 核心概念定义
- **节点 (Node)**：人物、地点、组织等实体

## 提取规则
1. 提取所有相关实体
2. 为每个实体指定类型

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取生活事件。

## 核心概念定义
- **边 (Edge)**：生活事件
- **时间**：事件发生的时间

### 时间解析规则
当前观察日期：{observation_time}

1. 相对时间解析（基于观察日期）：
   - "去年" → {observation_time} 前一年
   - "今年" → {observation_time} 所属年份
   - "明年" → {observation_time} 后一年
   - "昨天/今天/明天" → {observation_time} 前/当/后一天
   - "十年前/五年后" → {observation_time} 前/后相应年数
   - "年初/年末" → 当年 1月1日/12月31日
   - "朝代" → 保留朝代名称

2. 明确日期：保持原格式
3. 缺失时间：留空

### 约束条件
1. 仅从已知实体列表中提取事件
2. 不要创建未列出的实体
3. 时间信息为可选，仅在文本中明确提及时才提取
"""


class LifeEventTimeline(AutoTemporalGraph[LifeEntity, LifeEvent]):
    """
    适用文档: 人物传记、年表、回忆录、自传

    功能介绍:
    提取带时间戳的事件，并按时间顺序排列。适用于人物传记、年表、回忆录等。

    Example:
        >>> template = LifeEventTimeline(llm_client=llm, embedder=embedder)
        >>> template.feed_text("祖冲之（429年－500年），字文远，范阳遒县人...")
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
            node_schema=LifeEntity,
            edge_schema=LifeEvent,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.eventType}|{x.details}",
            time_in_edge_extractor=lambda x: x.eventDate or "",
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
        展示生平时序图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: LifeEntity) -> str:
            return f"{node.name} ({node.type})"

        def edge_label_extractor(edge: LifeEvent) -> str:
            if edge.eventDate:
                return f"{edge.eventType} ({edge.eventDate})"
            return f"{edge.eventType}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
