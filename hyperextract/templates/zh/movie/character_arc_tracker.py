from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================

class CharacterState(BaseModel):
    """电影人物在特定时刻的状态节点。"""
    character_name: str = Field(description="人物名称。")
    psychological_state: str = Field(description="人物此时的心理状态或核心情绪。")
    current_goal: str = Field(description="人物此时的核心目标。")
    situation: str = Field(description="人物所处的外部处境或冲突。")

class CharacterDevelopment(BaseModel):
    """人物状态的演变与弧光转变。"""
    source: str = Field(description="起始状态。")
    target: str = Field(description="转变后的状态。")
    time: str = Field(description="发生转变的时间点或剧情阶段（如‘第二幕’、‘决战前夕’）。")
    trigger_event: str = Field(description="导致这一状态转变的关键剧情事件。")
    arc_direction: str = Field(description="弧光方向（如：成长、堕落、觉醒、发现）。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位资深的剧本分析师和角色研究专家。你的任务是从剧本或长篇影评中追踪角色的‘人物弧光’。\n\n"
    "提取要求：\n"
    "1. **状态切片**：提取人物在故事不同阶段的心理、目标和处境节点。\n"
    "2. **转变触发**：识别导致人物在两个状态之间发生转变的关键驱动事件。\n"
    "3. **时间线解析**：明确转变发生的时间节点（如剧本页码、幕数或相对时间）。\n"
)

_NODE_PROMPT = "请识别并提取角色在剧本关键节点的内部与外部状态。记录其情绪、当下的目标以及面临的主要处境。"
_EDGE_PROMPT = "分析角色状态之间的演变。请指出是什么剧情事件触发了角色的心路历程转变，并归纳其弧光的发展方向。"

# ==============================================================================
# 3. 模板类
# ==============================================================================

class CharacterArcTracker(AutoTemporalGraph[CharacterState, CharacterDevelopment]):
    """
    适用于：[角色传记, 戏剧脚本, 文学改编, 影评]

    用于分析电影角色成长路径与心理弧光的时序图谱模板。

    该模板专注于呈现“为什么变”和“怎么变”，适合深度角色研究与戏剧冲突分析。

    示例:
        >>> arc = CharacterArcTracker(llm_client=llm, embedder=embedder)
        >>> text = "故事开始时，杰克是个胆怯的职员。在经历那场爆炸后，他意识到生命的可贵，在决战中展现了惊人的勇气。"
        >>> arc.feed_text(text).show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        **kwargs: Any
    ):
        super().__init__(
            node_schema=CharacterState,
            edge_schema=CharacterDevelopment,
            node_key_extractor=lambda x: f"{x.character_name}-{x.psychological_state[:10]}",
            edge_key_extractor=lambda x: f"{x.source}>>{x.target}",
            time_in_edge_extractor=lambda x: x.time,
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            extraction_mode=extraction_mode,
            **kwargs
        )

    def show(self, **kwargs):
        def n_label(node: CharacterState) -> str: return f"{node.character_name}: {node.psychological_state}"
        def e_label(edge: CharacterDevelopment) -> str: return f"[{edge.time}] {edge.arc_direction}"
        super().show(node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs)
