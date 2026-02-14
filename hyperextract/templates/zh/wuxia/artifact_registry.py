from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class DivineArtifact(BaseModel):
    """修真界或武侠世界中的神兵、法宝、丹药或天材地宝。"""

    name: str = Field(description="宝物名称（如：屠龙刀、九转金丹）。")
    grade: str = Field(description="品阶（如：天阶上品、神器、后天至宝）。")
    origin: Optional[str] = Field(
        description="来历或创造者（如：太上老君炼制、上古遗迹出土）。"
    )
    special_effects: List[str] = Field(
        description="独特神通或功效（如：吞噬神魂、破防、延寿千载）。"
    )
    spirit_consciousness: Optional[str] = Field(
        description="器灵或灵性描述（如：有一丝懵懂意识、器灵沉睡中）。"
    )
    current_owner: Optional[str] = Field(description="最近已知的持有者。")


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位痴迷于搜集天下奇珍异宝的‘鉴宝宗师’。你的任务是从小说描述中建立一份神兵法宝、天材地宝及稀世丹药的名录。\n\n"
    "### 核心提取规则：\n"
    "1. **属性详尽性**：准确提取法宝的品阶（grade）、来历（origin）及核心用途。\n"
    "2. **神通动态更新**：解析法宝携带的独特神通（special_effects）。由于同一法宝在不同阶段显示的威力不同，请确保持续补充新发现的能力。\n"
    "3. **灵性洞察**：特别标注法宝是否具备‘器灵’（spirit_consciousness）及其性格特征或苏醒状态。\n"
    "4. **传承链条**：识别并更新该法宝的历史持有者及当前主人（current_owner）。\n"
    "5. **命名规范**：确保同一件法宝使用统一的名称作为主键，合并琐碎的描述。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class ArtifactRegistry(AutoSet[DivineArtifact]):
    """
    适用于：[武侠/仙侠小说, 奇幻游戏道具, 重宝名录]

    一个旨在积累并完善神兵利器、法宝及稀世丹药属性的图鉴模板。

    Key Features:
    - 使用 AutoSet 逻辑合并同一法宝的多源信息。
    - 记录每件物品的品阶、创造者及必杀技。
    - 追踪贯穿叙事始终的器灵意识及归属权变更。

    Example:
        >>> from hyperextract.templates.zh.wuxia import ArtifactRegistry
        >>> registry = ArtifactRegistry(llm_client=llm, embedder=embedder)
        >>> text = "此剑名曰青索，乃紫青双剑之一，曾属长眉真人，剑中藏有一尊沉睡的青龙器灵。"
        >>> registry.feed_text(text).show()
    """

    def __init__(self, llm_client: BaseChatModel, embedder: Embeddings, **kwargs: Any):
        """
        初始化 ArtifactRegistry。

        Args:
            llm_client (BaseChatModel): 用于提取的语言模型客户端。
            embedder (Embeddings): 用于索引的嵌入模型。
            **kwargs: 传递给 AutoSet 的额外参数。
        """
        super().__init__(
            schema=DivineArtifact,
            # 以名称作为唯一键
            key_extractor=lambda x: x.name.strip(),
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            **kwargs,
        )

    def show(self, **kwargs):
        """
        展示法宝图鉴列表。

        Args:
            **kwargs: 传递给基础 show() 方法的参数。
        """

        def label_func(item: DivineArtifact) -> str:
            effects = ", ".join(item.special_effects[:2])
            return f"【{item.grade}】{item.name}: {effects}..."

        super().show(label_extractor=label_func, **kwargs)
