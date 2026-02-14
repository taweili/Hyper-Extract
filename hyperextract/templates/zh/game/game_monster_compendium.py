"""游戏怪物百科 - 从多个来源自动合并游戏怪物信息。

该模板通过合并来自攻略、Wiki、怪物掉落手册的多个来源的信息来构建
全面的游戏怪物数据库。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# Schema 定义
# ==============================================================================

class GameMonsterSchema(BaseModel):
    """游戏怪物百科中单个怪物的数据结构。"""

    monster_name: str = Field(..., description="怪物的标准名称，如'哥布林战士'")
    type: str = Field(..., description="怪物种族分类及强度：'哥布林/普通'、'龙/首领'")
    habitat: Optional[str] = Field(None, description="通常出现的地图区域")
    abilities: Optional[str] = Field(None, description="战斗数值、特殊技能、弱点及难度评估等综合战斗信息")
    loot_and_lore: Optional[str] = Field(None, description="掉落物品、复活机制及背景故事")


# ==============================================================================
# 提取 Prompt
# ==============================================================================

_PROMPT = """你是一位游戏怪物图鉴作者。从文本中提取怪物的核心信息。

提取目标：
1. **monster_name**：怪物官方名称
2. **type**：种族及稀有度（如：亡灵/精英）
3. **habitat**：出没地点
4. **abilities**：合并战斗属性（HP/攻击）、技能、弱点和打法建议
5. **loot_and_lore**：合并掉落列表、刷新时间和背景描述

仅提取明确提及的信息。

### 源文本：
"""


# ==============================================================================
# 模板类
# ==============================================================================

class GameMonsterCompendium(AutoSet[GameMonsterSchema]):
    """适用于：怪物指南、图鉴条目、刷怪指南

    通过自动去重和合并来自多个来源的怪物信息来提取全面的游戏怪物数据库。
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        super().__init__(
            item_schema=GameMonsterSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.monster_name.strip().lower(),
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        def monster_label_extractor(item: GameMonsterSchema) -> str:
            type_label = f" ({item.type})" if item.type else ""
            return f"{item.monster_name}{type_label}"

        super().show(
            item_label_extractor=monster_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
