from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================


class NarrativePoint(BaseModel):
    """叙事流中的核心情节节点。"""

    name: str = Field(description="情节或事件的短标题（如‘鸿门宴’、‘初遇’）。")
    location: Optional[str] = Field(description="事件发生的地点。")
    characters_involved: List[str] = Field(
        default_factory=list, description="参与该事件的人物名单。"
    )
    description: str = Field(description="对情节内容的具体描述，包括核心动作和转折。")


class TimeTransition(BaseModel):
    """情节节点之间的时间演变与逻辑关联。"""

    source: str = Field(description="起始情节名称。")
    target: str = Field(description="后续情节名称。")
    time: str = Field(
        description="事实发生的时间。你必须结合上下文和观察日期，将相对时间（如‘三天后’、‘次日’）解析并转换为绝对日期（如‘2024-01-15’）或具体年份。"
    )
    logic: str = Field(description="事件间的逻辑关系（如：因果、递进、意外转折）。")


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位资深的叙事学家。你的任务是从文本中还原情节发展的时空蓝图。\n\n"
    "提取要求：\n"
    "1. **情节识别**：提取具有独立叙事意义的节点，记录其发生的地点及参与者。\n"
    "2. **时间轴构建**：在情节间建立带时间属性的连线。特别注意文本中的时间指示词（如‘过了半晌’、‘数月无话’）。\n"
    "3. **逻辑链条**：除了时间先后，还要识别事件间的因果驱动力。\n"
    "注意：时间必须提取在边（Transition）上，不要作为独立的节点。"
)

_NODE_PROMPT = "请识别并提取文本中所有的关键情节节点（Plot Points）。为每个节点命名，并提供地点描述及涉及的人物。"

_EDGE_PROMPT = "在给定的情节节点之间建立联系。请精确提取文本中提及的时间线索，并描述这些事件是如何在叙事逻辑上相互连接的。"

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================


class NarrativeTimeline(AutoTemporalGraph[NarrativePoint, TimeTransition]):
    """
    适用于：[编年史, 史诗文学, 侦探小说, 史书]

    用于还原文学或历史叙述中情节演变的时间线图谱模板。

    该模板利用 AutoTemporalGraph 的时序特性，将时间信息嵌入关系中，专注于呈现“起因-经过-结果”的动态过程。

    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> # 初始化模板
        >>> timeline = NarrativeTimeline(llm_client=llm, embedder=embedder)
        >>> # 输入包含时间跨度的文本
        >>> text = "隆中对之后，刘备三顾茅庐请出诸葛亮。数年后，曹操南下，引发了赤壁之战。"
        >>> timeline.feed_text(text)
        >>> timeline.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: Optional[str] = None,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化 NarrativeTimeline 模板。

        Args:
            llm_client: 用于提取的语言模型客户端。
            embedder: 用于实体去重和索引的嵌入模型。
            observation_time: 设定的基准参考日期，用于解析相对时间（如‘今天’）。
            extraction_mode: 默认使用 two_stage 以保证时间解析的精准度。
            chunk_size: 文本块大小。
            chunk_overlap: 文本块重叠大小。
            max_workers: 最大并行工作线程数。
            verbose: 是否开启详细日志。
            **kwargs: 其他传给 AutoTemporalGraph 的参数。
        """
        super().__init__(
            node_schema=NarrativePoint,
            edge_schema=TimeTransition,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source}->{x.target}",
            time_in_edge_extractor=lambda x: x.time,
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            extraction_mode=extraction_mode,
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
        可视化叙事时间线。

        Args:
            top_k_nodes_for_search: 搜索时找回的相关节点数量。
            top_k_edges_for_search: 搜索时找回的相关边数量。
            top_k_nodes_for_chat: 聊天时找回的相关节点数量。
            top_k_edges_for_chat: 聊天时找回的相关边数量。
        """

        def node_label_extractor(node: NarrativePoint) -> str:
            return node.name

        def edge_label_extractor(edge: TimeTransition) -> str:
            return f"[{edge.time}] {edge.logic}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
