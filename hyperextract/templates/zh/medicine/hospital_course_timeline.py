"""住院病程时间轴 - 严格按时间顺序提取入院、检查、治疗、转归等节点。

适用于出院小结中关于住院病程的内容。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph


class HospitalEntity(BaseModel):
    """住院实体节点"""

    name: str = Field(description="节点名称，如入院、检查、治疗、转归等")
    category: str = Field(description="节点类型：入院、检查、治疗、手术、转归、其他等")
    description: str = Field(description="简要描述", default="")


class HospitalEvent(BaseModel):
    """住院事件边"""

    source: str = Field(description="源节点")
    target: str = Field(description="目标节点")
    eventType: str = Field(description="事件类型：入院、检查、治疗、手术、转归等")
    eventDate: str = Field(description="事件日期，格式为年-月-日")
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的医院管理人员，请从文本中严格按时间顺序提取入院、检查、治疗、转归等节点，构建住院病程时间轴。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指住院实体，包括入院、检查、治疗、手术、转归等类型，用于表示住院病程中的基本要素。
- **边 (Edge)**：本模板中的"边"指住院事件边，连接节点并包含时间信息，表达住院病程中的事件。
- **时间**：本模板中的"时间"指事件发生的时间信息，用于按时间顺序排列住院事件，支持相对时间解析。

## 提取规则
### 节点提取规则
1. 提取所有住院相关节点：入院、检查项目、治疗方法、手术、转归等
2. 为每个节点指定类型：入院、检查、治疗、手术、转归、其他等
3. 为每个节点添加简要描述

### 事件提取规则
1. 仅从提取的节点中创建事件边
2. 为每个事件指定类型：入院、检查、治疗、手术、转归等
3. 为每个事件指定日期，格式为年-月-日
4. 为每个事件添加详细描述（如果文本中提供）

### 时间解析规则
当前观察日期：{observation_time}

1. **相对时间解析**：必须根据观察日期解析相对时间表达
   - "入院当天" → 使用入院日期
   - "术后第一天" → 手术日期的后一天
   - "昨天" → {observation_time} 前一天
   - "今天" → {observation_time}

2. **明确日期**：保持原文中的明确日期格式不变
   - 年-月-日（如 2026-02-01）→ 2026-02-01

3. **缺失时间**：如果文本中没有时间信息，将 eventDate 留空，不要编造日期

### 约束条件
- 每条边必须连接已提取的节点
- 不要创建未在文本中提及的节点或事件
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的医院管理人员，请从文本中提取所有住院相关节点。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指住院实体，包括入院、检查、治疗、手术、转归等类型，用于表示住院病程中的基本要素。

## 提取规则
1. 提取所有住院相关节点：入院、检查项目、治疗方法、手术、转归等
2. 为每个节点指定类型：入院、检查、治疗、手术、转归、其他等
3. 为每个节点添加简要描述

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的医院管理人员，请从给定节点列表中提取住院事件，构建住院病程时间轴。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指住院实体，作为住院事件的参与者。
- **边 (Edge)**：本模板中的"边"指住院事件边，连接节点并包含时间信息，表达住院病程中的事件。
- **时间**：本模板中的"时间"指事件发生的时间信息，用于按时间顺序排列住院事件，支持相对时间解析。

## 提取规则
### 时间解析规则
当前观察日期：{observation_time}

1. **相对时间解析**：必须根据观察日期解析相对时间表达
   - "入院当天" → 使用入院日期
   - "术后第一天" → 手术日期的后一天
   - "昨天" → {observation_time} 前一天
   - "今天" → {observation_time}

2. **明确日期**：保持原文中的明确日期格式不变
   - 年-月-日（如 2026-02-01）→ 2026-02-01

3. **缺失时间**：如果文本中没有时间信息，将 eventDate 留空，不要编造日期

### 日期格式要求
- 所有日期信息统一转换为「年-月-日」格式（如 2026-02-01）

### 约束条件
1. 仅从下方已知节点列表中提取事件
2. 不要创建未列出的节点
3. 时间信息为必填项，必须为每个事件指定日期

"""


class HospitalCourseTimeline(AutoTemporalGraph[HospitalEntity, HospitalEvent]):
    """
    适用文档: 出院小结、住院病历

    功能介绍:
    严格按时间顺序提取入院、检查、治疗、转归等节点，适用于病历质控、医疗纠纷溯源。

    Example:
        >>> template = HospitalCourseTimeline(llm_client=llm, embedder=embedder)
        >>> template.feed_text("患者于2026年2月1日入院，2月2日进行心电图检查...")
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
        初始化住院病程时间轴模板。

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
            node_schema=HospitalEntity,
            edge_schema=HospitalEvent,
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
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ):
        """
        展示住院病程时间轴。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: HospitalEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: HospitalEvent) -> str:
            return f"{edge.eventType} ({edge.eventDate})"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
