"""游戏角色百科 - 从多个来源自动合并游戏角色信息。

该模板通过合并来自官方背景故事、策略指南、角色指南和补丁说明的多个来源的信息
来提取全面的游戏角色百科。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# Schema 定义
# ==============================================================================


class GameCharacterSchema(BaseModel):
    """游戏角色百科中单个角色的数据结构。"""

    character_name: str = Field(..., description="角色的标准名称，如'亚索'")
    class_role: str = Field(
        ...,
        description="角色职业/定位（如'战士'、'法师'）及玩法风格简述。",
    )
    affiliation: Optional[str] = Field(
        None, description="所属阵营、团队或出身地区。"
    )
    abilities: Optional[str] = Field(
        None,
        description="招牌技能、终极技能及核心基础数值属性。",
    )
    lore: Optional[str] = Field(
        None, description="背景故事、性格特质、配音演员等设定信息。"
    )


# ==============================================================================
# 提取 Prompt
# ==============================================================================

_PROMPT = """你是一位游戏背景设定专家和角色指南作者。
你的任务是从文本中提取游戏角色的全面信息。

对于文本中提到的每个角色，提取：
1. **character_name**：角色的官方名称
2. **class_role**：角色的职业定位与玩法概述
3. **affiliation**：角色所属的组织、阵营或家乡
4. **abilities**：角色的核心技能、大招说明及关键数值
5. **lore**：角色的背景故事、身世细节、配音等设定

仅提取文本中明确说明的信息。如果某个字段未提及，空置即可。
全面捕捉所有角色详情，即使它们分散在文本中。

### 源文本：
"""


# ==============================================================================
# 模板类
# ==============================================================================


class GameCharacterCompendium(AutoSet[GameCharacterSchema]):
    """适用于：角色背景故事、技能指南、官方角色资料、策略指南

    通过自动去重和合并来自多个来源的角色信息来提取全面的游戏角色百科。

    来自不同来源（官方背景、策略指南、补丁说明）关于同一角色的信息会自动
    组合成单个富集的角色档案。

    示例：
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.zh.game import GameCharacterCompendium
        >>>
        >>> llm = ChatOpenAI(model="gpt-4", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>>
        >>> characters = GameCharacterCompendium(
        ...     llm_client=llm,
        ...     embedder=embedder
        ... )
        >>>
        >>> # 输入多个来源
        >>> characters.feed_text(
        ...     "亚索是来自印度群岛的一位荣誉剑士。"
        ...     "他以无与伦比的精准度和速度挥舞刀刃。"
        ... )
        >>> characters.feed_text(
        ...     "亚索的能力包括：钢铁飓风(Q)、风之障壁(W)、"
        ...     "逐风剑术(E)、最后通牒(R)。"
        ...     "属性：550生命值，50攻击力，25护甲。"
        ... )
        >>>
        >>> # 所有信息自动合并为单个亚索档案
        >>> characters.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        """初始化游戏角色百科模板。

        参数：
            llm_client：语言模型客户端，用于角色提取（如 ChatOpenAI）
            embedder：嵌入模型，用于语义索引（如 OpenAIEmbeddings）
            chunk_size：单个文本块的最大字符数（默认2048）
            chunk_overlap：相邻块之间的重叠字符数（默认256）
            **kwargs：传递给 AutoSet 父类的其他参数
        """
        super().__init__(
            item_schema=GameCharacterSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.character_name.strip().lower(),
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
        """展示游戏角色百科为交互式知识图谱。

        参数：
            top_k_for_search：语义搜索返回的前 K 个结果数
            top_k_for_chat：对话上下文中显示的前 K 个结果数
        """

        def character_label_extractor(item: GameCharacterSchema) -> str:
            """提取展示标签：角色名称带职业"""
            class_label = f" ({item.class_role})" if item.class_role else ""
            return f"{item.character_name}{class_label}"

        super().show(
            item_label_extractor=character_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
