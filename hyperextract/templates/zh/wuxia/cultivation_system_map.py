from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class CultivationRealm(BaseModel):
    """武侠/修真体系中的修炼境界节点。"""

    name: str = Field(description="境界名称（如：练气期、元婴期、宗师境）。")
    system: str = Field(description="所属体系（如：仙道、武道、魔门、魂修）。")
    key_feature: Optional[str] = Field(
        description="该境界的核心特征（如：内力外放、御剑飞行、元神出窍）。"
    )


class AdvancementCondition(BaseModel):
    """从一个境界突破到下一个境界的条件与风险。"""

    source: str = Field(description="当前境界。")
    target: str = Field(description="下一境界。")
    requirements: List[str] = Field(
        description="突破的前置条件（如：筑基丹、感悟剑意、渡雷劫）。"
    )
    risk: Optional[str] = Field(
        description="突破失败的后果或风险（如：走火入魔、修为尽废）。"
    )
    method: str = Field(
        description="修炼或突破的具体方法描述（如：闭关、双修、顿悟）。"
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位通晓诸天万界修炼体系的‘百晓生’。你的任务是分析并提取小说中的等级境界体系及晋升路径。\n\n"
    "### 核心提取规则：\n"
    "1. **层级严谨性**：确定境界的线性或分支关系（如从‘练气’到‘筑基’）。\n"
    "2. **突破细节**：识别每个大境界或小境界突破时的核心指标、所需外物（丹药、机缘）及外部环境（如雷劫、感悟）。\n"
    "3. **风险评估**：特别标注突破失败可能导致的走火入魔、修为跌落甚至陨落等描述。\n"
    "4. **体系独立性**：如果文本中存在多套体系（如武道与神修并存），确保互不混淆。"
)

_NODE_PROMPT = (
    "你是一位异世界设定分析师。请识别文本中出现的修炼境界节点及境界体系名称。\n\n"
    "### 提取要求：\n"
    "1. **粒度控制**：除了提取大境界名，也应提取具有显著特征的小层级（如‘大圆满’）。\n"
    "2. **属性补全**：捕捉该境界独有的神通或身体异化（如‘紫府初开’）。"
)

_EDGE_PROMPT = (
    "你是一位功法大演化专家。请在已识别的修炼境界间建立晋升脉络。\n\n"
    "### 逻辑连接规则：\n"
    "1. **进阶关系**：建立有向边，表示修行进阶的方向。\n"
    "2. **因果与条件**：详细提取‘如何突破’的动作（闭关、战斗突破等）及所需资源映射到 `requirements`。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class CultivationSystemMap(AutoGraph[CultivationRealm, AdvancementCondition]):
    """
    适用于：[仙侠/武侠小说, 游戏世界观设定, RPG 升级指南]

    一个专门设计用于映射玄幻小说中复杂修炼等级及进阶逻辑的图谱模板。

    Key Features:
    - 厘清修炼境界的层级结构（如从“练气”到“筑基”）。
    - 捕获进阶所需的特定条件，如丹药、顿悟或雷劫。
    - 记录潜在的风险，包括修为倒退或走火入魔。

    Example:
        >>> from hyperextract.templates.zh.wuxia import CultivationSystemMap
        >>> cult_map = CultivationSystemMap(llm_client=llm, embedder=embedder)
        >>> text = "由筑基入金丹，需服九转金丹，历经三九雷劫，方可碎丹成婴。"
        >>> cult_map.feed_text(text).show()
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
        初始化 CultivationSystemMap。

        Args:
            llm_client (BaseChatModel): 用于提取的语言模型客户端。
            embedder (Embeddings): 用于索引的嵌入模型。
            extraction_mode (str): 提取模式，'one_stage' 或 'two_stage'。默认为 'two_stage'。
            **kwargs: 传递给 AutoGraph 的额外参数。
        """
        super().__init__(
            node_schema=CultivationRealm,
            edge_schema=AdvancementCondition,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source}->{x.target}",
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
        可视化修炼进阶图谱。

        Args:
            **kwargs: 传递给基础 show() 方法的参数。
        """

        def n_label(node: CultivationRealm) -> str:
            return f"{node.system}: {node.name}"

        def e_label(edge: AdvancementCondition) -> str:
            reqs = ",".join(edge.requirements)
            return f"突破条件: {reqs} | 风险: {edge.risk or '无'}"

        super().show(
            node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs
        )
