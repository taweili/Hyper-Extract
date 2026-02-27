"""公司历史时间线 - 从招股说明书或公司历史文档中提取里程碑事件。

适用文档: S-1 招股说明书、公司简介页面、尽职调查报告、公司历史摘要

功能介绍:
    按时间顺序提取公司创立、融资轮次、收购、IPO 等里程碑事件，
    支持尽职调查和公司发展历史分析。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class CorporateEntity(BaseModel):
    """
    参与公司历史里程碑的实体。
    """

    name: str = Field(
        description="实体名称（例如公司名称、创始人、投资者、被收购方）。"
    )
    entity_type: str = Field(
        description='类型："公司"、"创始人"、"投资者"、"被收购方"、"合作伙伴"、"监管机构"。'
    )
    description: Optional[str] = Field(
        None, description="角色或背景信息（例如'A 轮领投方'、'被收购子公司'）。"
    )


class CorporateMilestoneEdge(BaseModel):
    """
    带有时间上下文的公司里程碑事件。
    """

    source: str = Field(description="发起方实体名称。")
    target: str = Field(description="受影响的实体或里程碑目标。")
    event_type: str = Field(
        description='类型："创立"、"融资轮次"、"收购"、"产品发布"、'
        '"IPO"、"战略转型"、"合作"、"扩张"、"重组"、"关键人才引进"。'
    )
    start_timestamp: Optional[str] = Field(
        None,
        description="里程碑日期（例如'2015-06'、'2018 年 3 月'、'2020'）。",
    )
    end_timestamp: Optional[str] = Field(
        None,
        description="结束日期（如适用，例如收购完成日期）。",
    )
    description: Optional[str] = Field(
        None,
        description="里程碑详情（例如'红杉资本领投 5000 万美元 B 轮融资'）。",
    )
    financial_details: Optional[str] = Field(
        None,
        description="财务条款（如有，例如估值、交易规模）。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = """## 角色与任务
你是一位专业的尽职调查分析师，请从招股说明书或公司历史文档中提取公司历史里程碑及相关实体。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系
- **时间**：里程碑事件发生的日期或时间段

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别创立事件、融资轮次、收购、战略转型和关键人才引进
- 提取每个里程碑的具体日期或时间段
- 捕捉财务细节（估值、交易规模）（如有提及）
- 保持时间顺序的准确性

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月
   - "本季度" → {observation_time} 所在季度
   - "近期" → {observation_time} 最近 3 个月

2. 精确时间 → 保持原样
3. 时间缺失 → 留空，不要猜测

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的尽职调查分析师，请从文本中提取公司历史中涉及的所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别公司、创始人、投资者、被收购公司和合作伙伴
- 按类型对每个实体进行分类

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的尽职调查分析师，请从给定实体列表中提取带有日期的公司里程碑。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系
- **时间**：里程碑事件发生的日期或时间段

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 通过里程碑事件连接实体
- 提取具体日期或时间段
- 捕捉财务细节（交易规模、估值）
- 按类型对每个里程碑进行分类

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月

2. 精确时间 → 保持原样
3. 时间缺失 → 留空，不要猜测

### 源文本:
"""

# ==============================================================================
# 3. 模板类
# ==============================================================================


class CompanyHistoryTimeline(
    AutoTemporalGraph[CorporateEntity, CorporateMilestoneEdge]
):
    """
    适用文档: S-1 招股说明书（业务部分）、公司简介页面、
    尽职调查报告、公司历史摘要、投资者演示材料。

    模板用于从招股说明书和公司历史中按时间顺序提取公司里程碑。支持尽职调查
    时间线构建和企业演进跟踪。

    使用示例:
        >>> history = CompanyHistoryTimeline(llm_client=llm, embedder=embedder)
        >>> text = "公司于 2015 年由张三创立。2017 年完成 1000 万美元 A 轮融资..."
        >>> history.feed_text(text)
        >>> history.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: str = "2024-01-01",
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化公司历史时间线模板。

        Args:
            llm_client (BaseChatModel): 用于里程碑提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            observation_time (str): 用于解析相对日期的参考时间。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoTemporalGraph 的其他参数。
        """
        super().__init__(
            node_schema=CorporateEntity,
            edge_schema=CorporateMilestoneEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: (
                f"{x.source}|{x.event_type}|{x.target}"
            ),
            time_in_edge_extractor=lambda x: x.start_timestamp or "",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ) -> None:
        """
        使用 OntoSight 可视化公司历史时间线。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的里程碑数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的里程碑数。默认 3。
        """

        def node_label_extractor(node: CorporateEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: CorporateMilestoneEdge) -> str:
            date = f" [{edge.start_timestamp}]" if edge.start_timestamp else ""
            return f"{edge.event_type}{date}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
