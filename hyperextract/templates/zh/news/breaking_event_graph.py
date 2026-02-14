from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================

class NewsEntity(BaseModel):
    """新闻事件中的关键实体（人物、组织、国家、核心物件）。"""
    name: str = Field(description="实体的全称或最常用名。")
    category: str = Field(description="实体类别（如：政治人物、国际组织、政府机构、抗议团体）。")
    role: str = Field(description="该实体在当前新闻事件中扮演的角色或立场（如：发起者、受害者、调停方）。")

class NewsAction(BaseModel):
    """实体间的具体动作、行为或声明。"""
    source: str = Field(description="动作的发起方。")
    target: str = Field(description="动作的对象或接收方。")
    action_type: str = Field(description="动作类型（如：谴责、签署协议、发起进攻、发布声明）。")
    impact: str = Field(description="该动作产生的直接影响、结果或背景动机。")
    evidence: str = Field(description="对应的原文核心表述片段。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位资深的新闻编辑和地缘政治分析师。你的任务是从新闻报道中快速提取突发事件的全景图。\n\n"
    "提取要求：\n"
    "1. **实体定位**：提取所有关键参与方，并明确其在事件中的角色。\n"
    "2. **互动追踪**：分析各方之间的实体动作（Action），区分言语声明与实际行为。\n"
    "3. **影响评估**：捕捉动作背后的影响和核心动机。\n"
)

_NODE_PROMPT = "提取新闻中提及的所有关键人物、组织和国家。请注明其所属类别及在事件中的主要角色。"
_EDGE_PROMPT = "识别各方之间的具体行为与互动逻辑。请描述动作的性质、影响，并附带原文证据。"

# ==============================================================================
# 3. 模板类
# ==============================================================================

class BreakingEventGraph(AutoGraph[NewsEntity, NewsAction]):
    """
    适用于：[突发新闻报道, 地缘政治简报, 新闻稿, 情报摘要]

    用于快速解析突发新闻中“谁对谁做了什么”的全景图谱模板。

    该模板适合快速梳理复杂国际事件、经济纠纷或突发社会事件中各方的互动网。

    示例:
        >>> news = BreakingEventGraph(llm_client=llm, embedder=embedder)
        >>> text = "联合国秘书长今日公开谴责某国的军事行动，并呼吁立即停火。"
        >>> news.feed_text(text).show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",
        **kwargs: Any
    ):
        super().__init__(
            node_schema=NewsEntity,
            edge_schema=NewsAction,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source}-{x.action_type}-{x.target}",
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
        def n_label(node: NewsEntity) -> str: return f"{node.name} ({node.role})"
        def e_label(edge: NewsAction) -> str: return edge.action_type
        super().show(node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs)
