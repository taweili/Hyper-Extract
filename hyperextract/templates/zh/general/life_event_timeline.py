"""生平时序图 - 提取带时间戳的事件，并按时间顺序排列。

适用于人物传记、年表、回忆录等。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
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
    eventType: str = Field(description="事件类型：出生、逝世、教育、工作、成就、交往、旅行、其他")
    eventDate: Optional[str] = Field(description="事件日期，格式为年-月-日或年份，可选", default=None)
    details: str = Field(description="事件详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的传记年表专家，请从文本中提取人物、地点、组织等实体以及生活事件，构建生平时序图。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指生活实体，包括人物、地点、组织、物品、概念等类型，用于表示生平时序中的实体。
- **边 (Edge)**：本模板中的"边"指生活事件，连接多个实体，记录出生、教育、工作、成就等人生经历的二元关系。
- **时间**：本模板中的"时间"指事件发生的时间信息，用于按时间顺序排列生活事件，支持相对时间解析。

## 提取规则
### 节点提取规则
1. 提取所有相关实体：人物、地点、组织、物品、概念等
2. 为每个实体指定类型：人物、地点、组织、物品、概念、其他
3. 为每个实体添加简要描述

### 事件提取规则
1. 仅从提取的实体中创建事件边
2. 事件类型包括：
   - 出生：出生事件
   - 逝世：逝世事件
   - 教育：学习、受教育事件
   - 工作：工作、职业事件
   - 成就：取得成就、获得荣誉事件
   - 交往：人际交往、社会活动事件
   - 旅行：旅行、迁居事件
   - 其他：其他事件
3. 事件日期为可选提取项，仅在文本中明确提及时才提取
4. 日期格式：年-月-日（如 429-01-01）或年份（如 429）
5. 每条边必须连接已提取的节点

### 中文时间计算规则
当前观察日期：{observation_time}

1. **相对时间解析**：必须根据观察日期解析相对时间表达
   - "去年" → 计算为 {observation_time} 前一年
   - "今年" → {observation_time} 所属年份
   - "明年" → {observation_time} 后一年
   - "昨天" → {observation_time} 前一天
   - "今天" → {observation_time}
   - "明天" → {observation_time} 后一天
   - "上个月" → {observation_time} 前一个月的第一天
   - "这个月" → {observation_time} 所属月份的第一天
   - "下个月" → {observation_time} 后一个月的第一天
   - "十年前" → {observation_time} 前十年
   - "五年后" → {observation_time} 后五年
   - "年初" → 当年的 1月1日
   - "年末" → 当年的 12月31日
   - "世纪初" → 该世纪的第 1 年（如 2000 年）
   - "世纪末" → 该世纪的最后 1 年（如 2099 年）
   - "朝代" → 保留朝代名称（如"唐朝"、"宋代"），无需转换

2. **明确日期**：保持原文中的明确日期格式不变
   - 年份（如 429 年、2023 年）→ 429、2023
   - 年-月（如 429年3月）→ 429-03
   - 年-月-日（如 429年3月14日）→ 429-03-14
   - 中文数字日期（如"民国三十八年"）→ 转换为公元纪年

3. **缺失时间**：如果文本中没有时间信息，将 eventDate 留空（None），不要编造日期

### 约束条件
- 不要创建未在文本中提及的实体或事件
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的实体识别专家，请从文本中提取所有相关实体作为节点。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指生活实体，包括人物、地点、组织、物品、概念等类型，用于表示生平时序中的实体。

## 提取规则
1. 提取所有相关实体：人物、地点、组织、物品、概念等
2. 为每个实体指定类型：人物、地点、组织、物品、概念、其他
3. 为每个实体添加简要描述

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的生活事件提取专家，请从给定实体列表中提取生活事件。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指生活实体，作为生活事件的参与者。
- **边 (Edge)**：本模板中的"边"指生活事件，连接多个实体，记录出生、教育、工作、成就等人生经历的二元关系。
- **时间**：本模板中的"时间"指事件发生的时间信息，用于按时间顺序排列生活事件，支持相对时间解析。

## 提取规则
### 事件类型说明
- 出生：出生事件
- 逝世：逝世事件
- 教育：学习、受教育事件
- 工作：工作、职业事件
- 成就：取得成就、获得荣誉事件
- 交往：人际交往、社会活动事件
- 旅行：旅行、迁居事件
- 其他：其他事件

### 中文时间计算规则
当前观察日期：{observation_time}

1. **相对时间解析**：必须根据观察日期解析相对时间表达
   - "去年" → 计算为 {observation_time} 前一年
   - "今年" → {observation_time} 所属年份
   - "明年" → {observation_time} 后一年
   - "昨天" → {observation_time} 前一天
   - "今天" → {observation_time}
   - "明天" → {observation_time} 后一天
   - "上个月" → {observation_time} 前一个月的第一天
   - "这个月" → {observation_time} 所属月份的第一天
   - "下个月" → {observation_time} 后一个月的第一天
   - "十年前" → {observation_time} 前十年
   - "五年后" → {observation_time} 后五年
   - "年初" → 当年的 1月1日
   - "年末" → 当年的 12月31日
   - "世纪初" → 该世纪的第 1 年（如 2000 年）
   - "世纪末" → 该世纪的最后 1 年（如 2099 年）
   - "朝代" → 保留朝代名称（如"唐朝"、"宋代"），无需转换

2. **明确日期**：保持原文中的明确日期格式不变
   - 年份（如 429 年、2023 年）→ 429、2023
   - 年-月（如 429年3月）→ 429-03
   - 年-月-日（如 429年3月14日）→ 429-03-14
   - 中文数字日期（如"民国三十八年"）→ 转换为公元纪年

3. **缺失时间**：如果文本中没有时间信息，将 eventDate 留空（None），不要编造日期

### 日期格式要求
- 所有日期信息统一转换为「年-月-日」格式（如 429-01-01）或年份（如 429）
- 时间信息为可选提取项，仅在文本中明确提及时才提取

### 约束条件
1. 仅从下方已知实体列表中提取事件
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
        observation_time: str | None = None,
        extraction_mode: str = "two_stage",
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化生平时序图模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            observation_time: 观察日期，用于解析相对时间表达，默认为今天
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=LifeEntity,
            edge_schema=LifeEvent,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.eventType}|{x.target}",
            time_in_edge_extractor=lambda x: x.eventDate,
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
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        展示生平时序图。
        
        Args:
            top_k_for_search: 语义检索返回的节点/边数量，默认为 3
            top_k_for_chat: 问答使用的节点/边数量，默认为 3
        """
        def node_label_extractor(node: LifeEntity) -> str:
            return f"{node.name} ({node.type})"
        
        def edge_label_extractor(edge: LifeEvent) -> str:
            if edge.eventDate:
                return f"{edge.eventType} ({edge.eventDate})"
            return edge.eventType
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
