from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class SectEntity(BaseModel):
    """武侠或修真世界中的势力实体：宗门、帮派、家族。"""

    name: str = Field(description="宗门名称（如：少林寺、天魔教、慕容世家）。")
    alignment: str = Field(
        description="阵营或正邪倾向（如：正道魁首、魔门六道、隐世家族）。"
    )
    location_base: Optional[str] = Field(description="山门驻地（如：嵩山、海外仙岛）。")


class DiplomaticStance(BaseModel):
    """描述势力之间的复杂关系：盟友、世仇、联姻、主从。"""

    source: str = Field(description="发起方势力。")
    target: str = Field(description="对象势力。")
    relation_type: str = Field(
        description="关系性质（如：血海深仇、战略同盟、依附、表面交好）。"
    )
    origin_story: str = Field(
        description="该关系的成因或历史渊源（如：百年前正邪大战、争夺矿脉、老祖间的约定）。"
    )
    current_status: str = Field(description="当前状态（如：开战中、冷战、频繁往来）。")


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位研究武林史的学者。你的任务是分析江湖中各大门派、世家、帮派之间的外交关系与势力消长。\n\n"
    "### 核心提取规则：\n"
    "1. **身份锚定**：准确区分‘名门正派’、‘魔教反派’、‘中立势力’及‘隐世家族’。\n"
    "2. **关系动态**：不仅识别当前的盟友或敌对状态，更要挖掘导致这种关系的‘历史恩怨’（origin_story）或‘共同利益’。\n"
    "3. **状态敏感性**：区分当前是‘交战中’、‘貌合神离’还是‘盟约稳固’。\n"
    "4. **势力冲突**：特别提取多方势力之间爆发的武林战争、围攻或利益纷争。"
)

_NODE_PROMPT = (
    "你是一位江湖密探。请识别文本中出现的门派、势力名称及其江湖地位。\n\n"
    "### 提取要求：\n"
    "1. **分类识别**：根据其行事风格将其分类为‘正、邪、中立’等。\n"
    "2. **驻位捕捉**：提取该门派的山门驻地或总坛位置。"
)

_EDGE_PROMPT = (
    "你是一位分析江湖纠葛的谋士。请识别各大势力间的互动与关联。\n\n"
    "### 逻辑连接规则：\n"
    "1. **关系定性**：在 `relation_type` 中明确标注‘同盟’、‘死敌’、‘附庸’或‘世代结亲’。\n"
    "2. **背景追溯**：在 `origin_story` 中记录导致该关系的标志性事件（如某次围攻黑木崖）。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class SectRelationGraph(AutoGraph[SectEntity, DiplomaticStance]):
    """
    适用于：[武侠/仙侠小说, 历史演义, 外交分析]

    一个专注于建模虚构门派与势力间复杂社会政治关系的图谱模板。

    Key Features:
    - 将势力按道德立场分类（名门正派、魔门、中立）。
    - 映射主要门派的地理驻地。
    - 追踪历史恩怨的起源及当前的外交紧张局势。

    Example:
        >>> from hyperextract.templates.zh.wuxia import SectRelationGraph
        >>> sect_graph = SectRelationGraph(llm_client=llm, embedder=embedder)
        >>> text = "少林与武当交厚，共御魔教百年；然因屠龙刀现世，各大门派貌合神离。"
        >>> sect_graph.feed_text(text).show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        **kwargs: Any,
    ):
        """
        初始化 SectRelationGraph。

        Args:
            llm_client (BaseChatModel): 用于提取的语言模型客户端。
            embedder (Embeddings): 用于索引的嵌入模型。
            extraction_mode (str): 提取模式，'one_stage' 或 'two_stage'。默认为 'two_stage'。
            **kwargs: 传递给 AutoGraph 的额外参数。
        """
        super().__init__(
            node_schema=SectEntity,
            edge_schema=DiplomaticStance,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source}->{x.relation_type}->{x.target}",
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
        """
        可视化势力社交网络。

        Args:
            **kwargs: 传递给基础 show() 方法的参数。
        """

        def n_label(node: SectEntity) -> str:
            return f"[{node.alignment}] {node.name}"

        def e_label(edge: DiplomaticStance) -> str:
            return f"{edge.relation_type}: {edge.origin_story[:20]}..."

        super().show(
            node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs
        )
