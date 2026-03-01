"""公司历史时间线 - 从招股说明书或公司历史文档中提取里程碑事件。

适用文档: S-1 招股说明书、公司简介页面、尽职调查报告、公司历史摘要

功能介绍:
    按时间顺序提取公司创立、融资轮次、收购、IPO 等里程碑事件，
    支持尽职调查和公司发展历史分析。
"""

from typing import Any, Optional
from datetime import datetime
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import AutoTemporalGraph


class CompanyEntity(BaseModel):
    """公司实体节点"""

    name: str = Field(description="实体名称")
    type: str = Field(
        description="实体类型：公司、创始人、投资机构等"
    )
    description: str = Field(description="简要描述", default="")


class CompanyEvent(BaseModel):
    """公司事件边（带时间戳）"""

    source: str = Field(description="事件主体/相关实体")
    target: str = Field(description="事件对象/相关实体")
    eventType: str = Field(
        description="事件类型：成立、融资、并购、IPO、裁员、发布产品、管理层变更、股权变更、获得专利、获奖"
    )
    eventDate: Optional[str] = Field(
        description="事件日期，格式为年-月-日或年份", default=None
    )
    details: str = Field(description="事件详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的公司历史分析师，请从文本中提取公司相关的实体以及里程碑事件。

## 核心概念定义
- **节点 (Node)**：与公司历史直接相关的实体（本公司、子公司、创始人、投资机构）
- **边 (Edge)**：公司里程碑事件
- **时间**：事件发生的时间

## 提取规则
### 节点提取规则
1. 仅提取与公司历史直接相关的核心实体
2. 重点关注：本公司、子公司、创始人、投资机构

### 事件提取规则
1. 仅从提取的实体中创建事件边
2. 每条边必须连接已提取的节点
3. 时间信息为可选，仅在文本中明确提及时才提取
4. **source 和 target 只能是单个实体，不能是多个实体的拼接**
5. 如果多个主体参与同一事件，应为每个主体创建独立的边
   - 例如："A和B共同创立了C" → 创建两条边：(A, 创立, C) 和 (B, 创立, C)

### 事件类型
- 成立：公司成立
- 融资：种子轮、A轮、B轮、C轮、D轮、战略投资
- 并购：收购或被收购
- IPO：上市
- 裁员：人员优化、人员缩减
- 发布产品：新品发布、产品上线
- 管理层变更：CEO、CTO、COO等高管变动
- 股权变更：股权结构调整、增持、减持
- 获得专利：专利获批
- 获奖：行业奖项

### 时间解析规则
当前观察日期：{observation_time}

1. 相对时间解析（基于观察日期）：
   - "去年" → {observation_time} 前一年
   - "今年" → {observation_time} 所属年份
   - "明年" → {observation_time} 后一年
   - "五年前" → {observation_time} 前五年
   - "最近" → {observation_time} 前1年

2. 明确日期：保持原格式
   - 年份（如 2015年）→ 2015
   - 年-月-日 → 保持原格式

3. 缺失时间：留空

## 源文本:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取公司历史相关的实体作为节点。

## 核心概念定义
- **节点 (Node)**：与公司历史直接相关的实体

## 提取规则
1. 仅提取与公司历史直接相关的核心实体
2. 重点关注：本公司、子公司、创始人、投资机构
3. 谨慎提取：其他实体除非与重大里程碑事件相关

### 实体类型（优先提取）
- 公司：本公司的主体名称
- 创始人：公司的创始团队成员
- 投资机构：VC、PE等投资方

## 源文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取公司里程碑事件。

## 核心概念定义
- **节点 (Node)**：与公司历史相关的实体
- **边 (Edge)**：公司里程碑事件
- **时间**：事件发生的时间

### 事件类型
- 成立、融资、并购、IPO、裁员、发布产品、管理层变更等

### 时间解析规则
当前观察日期：{observation_time}

1. 相对时间解析：
   - "去年" → {observation_time} 前一年
   - "今年" → {observation_time} 所属年份
   - "五年前" → {observation_time} 前五年

2. 明确日期：保持原格式
3. 缺失时间：留空

### 约束条件
1. 仅从已知实体列表中提取事件
2. 不要创建未列出的实体
3. 时间信息为可选，仅在文本中明确提及时才提取
4. **source 和 target 只能是单个实体，不能是多个实体的拼接**
5. 如果多个主体参与同一事件，应为每个主体创建独立的边
   - 例如："A和B共同创立了C" → 创建两条边：(A, 创立, C) 和 (B, 创立, C)
   - 例如："红杉资本、IDG投资了该公司" → 创建两条边：(红杉资本, 投资, 该公司) 和 (IDG, 投资, 该公司)

## 已知实体列表：
{known_nodes}

## 源文本:
{source_text}
"""


class CompanyHistoryTimeline(AutoTemporalGraph[CompanyEntity, CompanyEvent]):
    """
    适用文档: S-1 招股说明书、公司简介页面、尽职调查报告、公司历史摘要

    功能介绍:
    按时间顺序提取公司创立、融资轮次、收购、IPO 等里程碑事件，
    支持尽职调查和公司发展历史分析。

    Example:
        >>> template = CompanyHistoryTimeline(llm_client=llm, embedder=embedder)
        >>> template.feed_text("公司于2015年成立，2018年完成A轮融资，2020年IPO上市...")
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
        初始化公司历史时间线模板。

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
            node_schema=CompanyEntity,
            edge_schema=CompanyEvent,
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
        展示公司历史时间线。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: CompanyEntity) -> str:
            return f"{node.name} ({node.type})"

        def edge_label_extractor(edge: CompanyEvent) -> str:
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
