"""游戏物品图鉴 - 从多个来源自动合并游戏物品信息。

该模板通过自动合并来自攻略、Wiki、补丁说明等多个来源的物品信息来构建完整的物品库。
使用 AutoSet 按物品名称精确匹配去重并融合属性信息。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# Schema 定义
# ==============================================================================

class GameItemSchema(BaseModel):
    """游戏物品图鉴中单个物品的数据结构。"""

    item_name: str = Field(..., description="物品的标准名称")
    category: str = Field(..., description="物品分类：'武器'、'防具'、'消耗品'、'配饰'、'材料'等")
    stat_bonuses: Optional[str] = Field(
        None, description="物品提供的属性加成，如'攻击力+50，生命值+100'"
    )
    crafting_recipe: Optional[str] = Field(None, description="如何通过合成其他物品获得该物品")
    drop_sources: Optional[str] = Field(
        None, description="物品的获取方式：掉落怪物、NPC商店、任务奖励等"
    )
    suitable_heroes: Optional[str] = Field(None, description="最适合装备该物品的职业或角色")
    lore_background: Optional[str] = Field(None, description="物品的游戏进度设定或背景故事")


# ==============================================================================
# 提取 Prompt
# ==============================================================================

_PROMPT = """你是一位游戏设计师和游戏攻略作者，对游戏物品系统非常熟悉。
你的任务是从文本中提取游戏物品的结构化信息。

对于文本中提到的每个物品，提取：
1. **item_name**：物品的标准名称
2. **category**：物品的类型（武器、防具、消耗品等）
3. **stat_bonuses**：该物品提供的属性、伤害、防御或状态效果加成
4. **crafting_recipe**：玩家如何制作或合成该物品
5. **drop_sources**：物品的掉落来源、商人、任务奖励等
6. **suitable_heroes**：推荐哪些职业或角色使用该物品
7. **lore_background**：与该物品相关的游戏故事或设定

仅提取文本中明确提及的信息。如果某个字段没有描述，空置即可。
重点是全面捕捉所有提到的物品及其详细信息。

### 源文本：
"""


# ==============================================================================
# 模板类
# ==============================================================================

class GameItemCompendium(AutoSet[GameItemSchema]):
    """适用于：游戏 Wiki 页面、策略指南、官方物品手册、补丁说明

    通过自动去重和合并来自多个来源的物品信息来提取游戏物品图鉴。

    当多个文本块描述同一物品（通过精确名称匹配识别）时，其属性被智能合并为单一条目。
    这允许跨多个文档逐步积累关于每个物品的知识。

    示例：
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.zh.game import GameItemCompendium
        >>>
        >>> llm = ChatOpenAI(model="gpt-4", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>>
        >>> compendium = GameItemCompendium(
        ...     llm_client=llm,
        ...     embedder=embedder
        ... )
        >>>
        >>> # 输入多个来源
        >>> compendium.feed_text(
        ...     "无尽之刃是一件传奇武器，提供+80攻击力。"
        ...     "可以通过长剑和魔晶合成获得。"
        ... )
        >>> compendium.feed_text(
        ...     "无尽之刃与亚索和亚托克斯完美契合，"
        ...     "能够启动这些英雄的强大暴击连击。"
        ... )
        >>>
        >>> # 所有信息自动在"无尽之刃"下合并
        >>> compendium.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        """初始化游戏物品图鉴模板。

        参数：
            llm_client：语言模型客户端，用于物品提取（如 ChatOpenAI）
            embedder：嵌入模型，用于语义索引（如 OpenAIEmbeddings）
            chunk_size：单个文本块的最大字符数（默认2048）
            chunk_overlap：相邻块之间的重叠字符数（默认256）
            **kwargs：传递给 AutoSet 父类的其他参数
        """
        super().__init__(
            item_schema=GameItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.item_name.strip().lower(),
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
        """展示游戏物品图鉴为交互式知识图谱。

        参数：
            top_k_for_search：语义搜索返回的前 K 个结果数
            top_k_for_chat：对话上下文中显示的前 K 个结果数
        """

        def item_label_extractor(item: GameItemSchema) -> str:
            """提取展示标签：物品名称带分类"""
            category_label = f" ({item.category})" if item.category else ""
            return f"{item.item_name}{category_label}"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
