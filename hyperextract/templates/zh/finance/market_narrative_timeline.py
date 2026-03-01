"""市场叙事时间线 - 追踪市场叙事随时间的演变。

追踪市场主导叙事和主题随时间的演变（例如从"通胀恐惧"转向"软着陆希望"），
用于主题投资和市场情绪分析。
"""

from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph


class NarrativeNode(BaseModel):
    """市场叙事节点"""

    name: str = Field(description="叙事名称（如'通胀恐惧'、'软着陆希望'）。")
    narrative_type: str = Field(
        description="叙事类型：'市场情绪'、'投资主题'、'政策预期'、'经济判断'。"
    )
    description: str = Field(description="叙事描述。")


class NarrativeTransitionEdge(BaseModel):
    """叙事演变边"""

    source: str = Field(description="先前叙事名称。")
    target: str = Field(description="新兴叙事名称。")
    transition_type: str = Field(
        description="演变类型：被替代、演变为、触发了、主导了。"
    )
    timestamp: str = Field(
        description="演变时间（如'2024-03'、'2024年Q2'）。"
    )
    catalyst: Optional[str] = Field(
        None,
        description="触发演变的事件或数据点。",
    )


_PROMPT = """## 角色与任务
你是一位专业的策略师，请从财经评论中提取市场叙事以及它们随时间的演变。

## 核心概念定义
- **节点 (Node)**：市场叙事，如市场情绪、投资主题、政策预期、经济判断
- **边 (Edge)**：叙事之间的演变关系
- **时间**：叙事演变发生的日期或时间段

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的叙事，禁止将多个叙事合并为一个节点
2. 叙事名称与原文保持一致
3. 仅从已知叙事列表中提取边，不要创建新的叙事
4. 关系描述应与原文保持一致

### 叙事定义
- 叙事是市场中的"故事"、主题、情绪
- 叙事不是具体的公司、指数、政策本身
- 例如："通胀恐惧"、"软着陆希望"、"AI热潮"、"避险情绪"是叙事
- 例如："降准"、"上证指数"、"GDP"不是叙事，是催化剂或指标

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月
   - "本季度" → {observation_time} 所在季度
   - "近期" → {observation_time} 最近 3 个月

2. 精确时间 → 保持原样
3. 时间缺失 → 留空

## 源文本:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的策略师，请从文本中提取市场叙事作为节点。

## 核心概念定义
- **节点 (Node)**：市场叙事

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的叙事，禁止将多个叙事合并为一个节点
2. 叙事名称与原文保持一致

### 叙事定义
- 叙事是市场中的"故事"、主题、情绪
- 叙事不是具体的公司、指数、政策本身
- 例如："通胀恐惧"、"软着陆希望"、"AI热潮"、"避险情绪"是叙事

### 叙事类型
- 市场情绪：投资者情绪变化
- 投资主题：主导投资方向
- 政策预期：对政策走向的判断
- 经济判断：对经济形势的看法

## 源文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的策略师，请从给定叙事列表中提取叙事演变关系。

## 核心概念定义
- **节点 (Node)**：市场叙事
- **边 (Edge)**：叙事之间的演变关系

## 提取规则
### 核心约束
1. **关键**：边的 source 和 target 必须完全使用下方叙事列表中的名称，禁止创造新叙事
2. 仅从已知叙事列表中提取边，不要创建新的叙事
3. 关系描述应与原文保持一致

### 演变类型
- 被替代：先前叙事被新叙事取代
- 演变为：先前叙事逐渐变成新叙事
- 触发了：新叙事因某事件而产生
- 主导了：新叙事成为市场主导

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月

2. 精确时间 → 保持原样
3. 时间缺失 → 留空

## 已知叙事列表：
{known_nodes}

## 源文本:
{source_text}
"""


class MarketNarrativeTimeline(
    AutoTemporalGraph[NarrativeNode, NarrativeTransitionEdge]
):
    """
    适用文档: 市场评论、宏观策略报告、财经新闻档案、投资展望报告、季度市场回顾。

    模板用于追踪市场主导叙事和主题随时间的演变。支持主题投资、
    市场情绪分析和叙事动量研究。

    使用示例:
        >>> narrative = MarketNarrativeTimeline(llm_client=llm, embedder=embedder)
        >>> commentary = "市场在 2024 年第二季度从通胀恐惧转向软着陆希望..."
        >>> narrative.feed_text(commentary)
        >>> narrative.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: str | None = None,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化市场叙事时间线模板。

        Args:
            llm_client (BaseChatModel): 用于叙事提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            observation_time (str): 用于解析相对日期的参考时间，未指定时默认为当前日期。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoTemporalGraph 的其他参数。
        """
        if observation_time is None:
            observation_time = datetime.now().strftime("%Y-%m-%d")

        super().__init__(
            node_schema=NarrativeNode,
            edge_schema=NarrativeTransitionEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: (
                f"{x.source}|{x.transition_type}|{x.target}"
            ),
            time_in_edge_extractor=lambda x: x.timestamp or "",
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
        使用 OntoSight 可视化市场叙事时间线。

        Args:
            top_k_nodes_for_search (int): 检索的叙事数。默认 3。
            top_k_edges_for_search (int): 检索的演变数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的叙事数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的演变数。默认 3。
        """

        def node_label_extractor(node: NarrativeNode) -> str:
            return f"{node.name} ({node.narrative_type})"

        def edge_label_extractor(edge: NarrativeTransitionEdge) -> str:
            date = f" [{edge.timestamp}]" if edge.timestamp else ""
            return f"{edge.transition_type}{date}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
