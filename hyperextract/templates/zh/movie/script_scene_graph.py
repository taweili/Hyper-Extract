from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================

class Scene(BaseModel):
    """电影剧本中的场景节点。"""
    title: str = Field(description="场景标题（如 'INT. COFFEE SHOP - DAY'）。")
    location: str = Field(description="场景发生的具体地点。")
    time_of_day: str = Field(description="场景发生的时间段（如 DAY, NIGHT, DUSK）。")
    description: str = Field(description="场景的简要动作描述或核心事件。")

class SceneTransition(BaseModel):
    """场景间的转场与逻辑演变。"""
    source: str = Field(description="起始场景标题。")
    target: str = Field(description="目标场景标题。")
    time: str = Field(description="场景间逝去的时间描述。你必须将其解析为绝对的持续时间或精确的时间偏移。")
    transition_type: str = Field(description="转场方式（如 CUT TO, FADE IN, CROSSFADE）。")
    logic: str = Field(description="场景间的叙事关联（如 动作延续、时间跳跃、平行剪辑）。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位资深的电影编剧和导演。你的任务是从剧本或分镜脚本中提取场景流及其叙事逻辑。\n\n"
    "提取要求：\n"
    "1. **场景识别**：提取所有独立的场景节点，完整记录其标题、地点和光影时间。\n"
    "2. **节奏分析**：识别场景间的转场方式，并准确解析场景间的时间流逝。\n"
    "3. **叙事逻辑**：描述场景之间是如何在故事层面上相互驱动的。\n"
)

_NODE_PROMPT = "请从剧本中提取所有场景（Scene）。记录每个场景的标准标题、地点、时间段及核心情节摘要。"
_EDGE_PROMPT = "在已识别的场景间建立联系（Transition）。请指出转场手段，并精确推断场景间的时间跨度与叙事逻辑关系。"

# ==============================================================================
# 3. 模板类
# ==============================================================================

class ScriptSceneGraph(AutoTemporalGraph[Scene, SceneTransition]):
    """
    适用于：[电影剧本, 电视剧本, 故事板, 叙事大纲]

    用于提取电影剧本中场景流与剪辑节奏的时序图谱模板。

    该模板专注于呈现电影的叙事节奏和场景变换，适合导演视角下的剧本拆解与可视化。

    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> script = ScriptSceneGraph(llm_client=llm, embedder=embedder)
        >>> text = "场景1：INT. LAB - DAY。科学家正在实验。CUT TO: 场景2：EXT. STREET - NIGHT。三小时后，他出现在街头。"
        >>> script.feed_text(text)
        >>> script.show()
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
            node_schema=Scene,
            edge_schema=SceneTransition,
            node_key_extractor=lambda x: x.title.strip(),
            edge_key_extractor=lambda x: f"{x.source}->{x.target}",
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
        def n_label(node: Scene) -> str: return node.title
        def e_label(edge: SceneTransition) -> str: return f"{edge.transition_type} ({edge.time})"
        super().show(node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs)
