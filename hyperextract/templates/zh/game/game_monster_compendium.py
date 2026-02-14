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
    monster_type: str = Field(..., description="怪物种族分类：'哥布林'、'龙'、'亡灵'、'野兽'等")
    rarity_tier: Optional[str] = Field(None, description="怪物的稀有程度：'普通'、'精英'、'首领'、'传奇'等")
    habitat: Optional[str] = Field(None, description="该怪物通常出现的地图区域")
    combat_stats: Optional[str] = Field(None, description="战斗属性和数值：生命值、攻击力、防御力、魔抗等")
    special_abilities: Optional[str] = Field(None, description="该怪物拥有的独特技能或特殊攻击方式")
    elemental_weakness: Optional[str] = Field(None, description="该怪物克制的元素类型：火、冰、风、圣、暗等")
    drop_table: Optional[str] = Field(None, description="打败该怪物掉落的物品及掉落概率")
    respawn_timer: Optional[str] = Field(None, description="该怪物被击败后的复活周期")
    encounter_difficulty: Optional[str] = Field(None, description="遭遇该怪物的推荐玩家等级或难度评估")


# ==============================================================================
# 提取 Prompt
# ==============================================================================

_PROMPT = """你是一位游戏怪物图鉴和刷怪攻略作者。
你的任务是从文本中提取游戏怪物的结构化信息。

对于文本中提到的每个怪物，提取：
1. **monster_name**：怪物的官方名称
2. **monster_type**：怪物的种族或生物类型
3. **rarity_tier**：该怪物的稀有程度或强度等级
4. **habitat**：可以发现该怪物的位置或地图区域
5. **combat_stats**：战斗属性的数值（生命值、攻击力、防御力等）
6. **special_abilities**：该怪物拥有的独特或危险的能力
7. **elemental_weakness**：克制该怪物的元素类型
8. **drop_table**：打败该怪物可能掉落的物品和概率
9. **respawn_timer**：怪物被击败后复活所需的时间
10. **encounter_difficulty**：推荐的玩家等级或挑战难度评估

仅提取文本中明确提及的信息。如果某个字段未描述，空置即可。
全面捕捉所有怪物详情，即使分散在文本中。

### 源文本：
"""


# ==============================================================================
# 模板类
# ==============================================================================

class GameMonsterCompendium(AutoSet[GameMonsterSchema]):
    """适用于：怪物指南、图鉴条目、刷怪指南、补丁说明

    通过自动去重和合并来自多个来源的怪物信息来提取全面的游戏怪物数据库。

    该模板特别适用于：
    - 从分散的 Wiki 信息构建统一的怪物数据库
    - 合并来自多个刷怪指南的怪物数据
    - 整合属性信息和掉落表
    - 通过合并来自多个来源的数据创建详细的怪物档案

    示例：
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.zh.game import GameMonsterCompendium
        >>>
        >>> llm = ChatOpenAI(model="gpt-4", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>>
        >>> monsters = GameMonsterCompendium(
        ...     llm_client=llm,
        ...     embedder=embedder
        ... )
        >>>
        >>> # 输入多个来源
        >>> monsters.feed_text(
        ...     "哥布林战士是一个近战格斗者，拥有150生命值和45攻击力。"
        ...     "在黑暗森林区域发现，每5分钟复活一次。"
        ... )
        >>> monsters.feed_text(
        ...     "哥布林战士对火消伤害克制。它可以使用盾牌冲击和横扫攻击。"
        ... )
        >>>
        >>> # 所有信息自动合并为单个哥布林战士档案
        >>> monsters.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        """初始化游戏怪物百科模板。

        参数：
            llm_client：语言模型客户端，用于怪物提取（如 ChatOpenAI）
            embedder：嵌入模型，用于语义索引（如 OpenAIEmbeddings）
            chunk_size：单个文本块的最大字符数（默认2048）
            chunk_overlap：相邻块之间的重叠字符数（默认256）
            **kwargs：传递给 AutoSet 父类的其他参数
        """
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
        """展示游戏怪物百科为交互式知识库。

        参数：
            top_k_for_search：语义搜索返回的前 K 个结果数
            top_k_for_chat：对话上下文中显示的前 K 个结果数
        """

        def monster_label_extractor(item: GameMonsterSchema) -> str:
            """提取展示标签：怪物名称带种族"""
            type_label = f" ({item.monster_type})" if item.monster_type else ""
            return f"{item.monster_name}{type_label}"

        super().show(
            item_label_extractor=monster_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
