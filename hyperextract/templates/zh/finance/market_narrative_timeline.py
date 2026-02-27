"""市场叙事时间线 - 追踪市场叙事随时间的演变。

追踪市场叙事和主导主题随时间的演变（例如从"通胀恐惧"转向"软着陆希望"），
用于主题投资和市场体制识别。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class NarrativeEntity(BaseModel):
    """
    参与叙事演变的市场叙事、主题或市场实体。
    """

    name: str = Field(
        description='叙事或实体的名称（例如"通胀恐惧"、"软着陆希望"、"标普 500"、"美联储政策"）。'
    )
    entity_type: str = Field(
        description='类型："叙事"、"主题"、"市场指数"、"资产类别"、"政策体制"、"经济阶段"。'
    )
    description: Optional[str] = Field(
        None,
        description='对该叙事或主题的解释。',
    )


class NarrativeShiftEdge(BaseModel):
    """
    具有时间背景的叙事转变或演变事件。
    """

    source: str = Field(description='先前的叙事或触发实体名称。')
    target: str = Field(description='新兴叙事或受影响实体名称。')
    shift_type: str = Field(
        description='类型："被替代"、"演变为"、"触发了"、"主导了"、'
        '"共存于"、"被削弱"。'
    )
    start_timestamp: Optional[str] = Field(
        None,
        description='转变开始时间（例如"2024-03"、"2024年3月"、"2024年第一季度"）。',
    )
    end_timestamp: Optional[str] = Field(
        None,
        description='转变完成或新叙事成为主导的时间。',
    )
    catalyst: Optional[str] = Field(
        None,
        description='触发转变的事件或数据点（例如"CPI 数据为 2.4%"）。',
    )
    market_impact: Optional[str] = Field(
        None,
        description='叙事转变如何影响市场（例如"从价值股轮动到成长股"）。',
    )
    description: Optional[str] = Field(
        None,
        description='叙事转变的详细解释。',
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = """## 角色与任务
你是一位专业的策略师，请从财经评论中提取市场叙事、主导主题以及它们随时间的演变。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系
- **时间**：叙事转变发生的日期或时间段

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别主导市场叙事和主题（例如'通胀恐惧'、'AI 热潮'）
- 追踪叙事如何转变、替代或演变为新的叙事
- 提取转变发生的具体日期或时间段
- 捕捉触发叙事变化的催化剂
- 记录叙事转变的市场影响

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
你是一位专业的策略师，请从文本中提取所有叙事、主题和市场实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别主导叙事和投资主题
- 识别市场指数、资产类别和政策体制

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的策略师，请从给定实体列表中提取叙事转变和演变事件。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系
- **时间**：叙事转变发生的日期或时间段

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 通过叙事的演变连接它们（被替代、演变为等）
- 提取具体日期或时间段
- 捕捉催化剂和市场影响

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月

2. 精确时间 → 保持原样
3. 时间缺失 → 留空，不要猜测

"""

# ==============================================================================
# 3. 模板类
# ==============================================================================


class MarketNarrativeTimeline(
    AutoTemporalGraph[NarrativeEntity, NarrativeShiftEdge]
):
    """
    适用文档: 市场评论、宏观策略报告、财经新闻档案、投资展望报告、季度市场回顾。

    模板用于追踪市场叙事和主导主题随时间的演变。支持主题投资、
    市场体制识别和叙事动量分析。

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
        observation_time: str = "2024-01-01",
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
            observation_time (str): 用于解析相对日期的参考时间。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoTemporalGraph 的其他参数。
        """
        super().__init__(
            node_schema=NarrativeEntity,
            edge_schema=NarrativeShiftEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: (
                f"{x.source}|{x.shift_type}|{x.target}"
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
        使用 OntoSight 可视化市场叙事时间线。

        Args:
            top_k_nodes_for_search (int): 检索的叙事数。默认 3。
            top_k_edges_for_search (int): 检索的转变数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的叙事数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的转变数。默认 3。
        """

        def node_label_extractor(node: NarrativeEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: NarrativeShiftEdge) -> str:
            date = f" [{edge.start_timestamp}]" if edge.start_timestamp else ""
            return f"{edge.shift_type}{date}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
