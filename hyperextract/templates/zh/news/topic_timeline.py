from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class NewsEventNode(BaseModel):
    """专题新闻中的核心事件节点。"""

    event_summary: str = Field(description="事件的简短标题或摘要。")
    location: Optional[str] = Field(description="事件发生的具体地理位置。")
    key_participants: List[str] = Field(description="涉及的核心人物或组织列表。")


class NewsTimelineProgression(BaseModel):
    """事件随时间的演进逻辑。"""

    source: str = Field(description="前导事件摘要。")
    target: str = Field(description="后续事件摘要。")
    time: str = Field(
        description="事件发生的具体时间节点。你必须解析文本中的模糊表达（如‘两周后’）为绝对日期。"
    )
    evolution_type: str = Field(
        description="事态演变性质（如：升级、转折、平息、连锁反应）。"
    )
    description: str = Field(description="这一阶段演进的具体内容描述。")


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位资深的时政调查记者。你的任务是从深度报道或系列新闻中梳理事件发展的脉络。\n\n"
    "提取要求：\n"
    "1. **节点提取**：识别具有里程碑意义的单一事件节点。\n"
    "2. **时间对齐**：根据基准日期解析出的所有时间信息，并将其体现在边（Progression）上。\n"
    "3. **动态关联**：侧重描述事件之间是如何由时间驱动并产生因果联系的。\n"
)

_NODE_PROMPT = (
    "识别新闻报道中的关键里程碑事件。为每个事件提供简明标题、地点及核心参与者。"
)
_EDGE_PROMPT = "在里程碑事件间建立时序链。请基于提供的观察日期解析相对时间词，并说明事态是如何演变或连锁触发的。"

# ==============================================================================
# 3. 模板类
# ==============================================================================


class TopicTimeline(AutoTemporalGraph[NewsEventNode, NewsTimelineProgression]):
    """
    适用于：[系列报道, 长篇调查新闻, 专题档案, 历史回顾]

    用于将零散新闻报道串联成连贯主题演化时间轴的模板。

    该模板专注于呈现事态的纵向发展轨迹，适合追踪长期社会热点或政策演变。

    示例:
        >>> timeline = TopicTimeline(llm_client=llm, embedder=embedder)
        >>> text = "2023年法案提出。半年后，经过激烈辩论获得通过。次月正式生效。"
        >>> timeline.feed_text(text).show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        **kwargs: Any,
    ):
        super().__init__(
            node_schema=NewsEventNode,
            edge_schema=NewsTimelineProgression,
            node_key_extractor=lambda x: x.event_summary.strip(),
            edge_key_extractor=lambda x: f"{x.source}>>{x.target}",
            time_in_edge_extractor=lambda x: x.time,
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            extraction_mode=extraction_mode,
            **kwargs,
        )

    def show(self, **kwargs):
        def n_label(node: NewsEventNode) -> str:
            return node.event_summary

        def e_label(edge: NewsTimelineProgression) -> str:
            return f"[{edge.time}] {edge.evolution_type}"

        super().show(
            node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs
        )
