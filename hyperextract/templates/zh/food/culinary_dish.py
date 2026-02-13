from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class CulinaryDish(BaseModel):
    """
    菜肴条目，包括其身份、成分和烹饪特征。
    """

    name: str = Field(description="菜肴的标准名称，例如宫保鸡丁或红烧肉。")
    cuisine: Optional[str] = Field(
        None, description="烹饪传统或菜系，例如四川、法式、意大利、日式。"
    )
    region: Optional[str] = Field(
        None, description="地理原产地，例如中国四川、法国普罗旺斯。"
    )
    primary_ingredients: Optional[str] = Field(
        None,
        description="主要成分列表，例如鸡、花生、干辣椒、酱油、糖。"
    )
    protein_type: Optional[str] = Field(
        None, description="主要蛋白质或基础：鸡肉、猪肉、鱼、豆腐、蔬菜。"
    )
    flavor_profile: Optional[str] = Field(
        None,
        description="总体味道特征，例如辛辣甜蜜、香气温暖、咸香鲜美。"
    )
    cooking_method: Optional[str] = Field(
        None, description="烹饪技术，例如炒、炖、烧烤、炸、蒸。"
    )
    dietary_attributes: Optional[str] = Field(
        None,
        description="饮食特征，例如素食、无麸质、低钠、高蛋白。"
    )
    serving_suggestion: Optional[str] = Field(
        None, description="典型的供菜方式或配菜，例如配米饭和蔬菜。"
    )
    seasonal_note: Optional[str] = Field(
        None, description="季节性或时间相关性，例如冬季舒适食物、夏季开胃菜。"
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是美食知识库管理员。从菜单、食谱甚至非结构化美食文本中提取菜肴。\n\n"
    "规则:\n"
    "- 识别每个不同的菜肴名称和变体。\n"
    "- 捕捉烹饪传统、地理原产地、主要成分。\n"
    "- 记录烹饪方法、风味特征和任何特殊属性。\n"
    "- 保持原始文本中的名称和描述。\n"
    "- 为后续去重标准化做准备（名称、成分）。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class CulinaryDishSet(AutoSet[CulinaryDish]):
    """
    适用文档: 餐厅菜单、美食博客、烹饪书籍、食材供应商列表、菜肴数据库、美食指南、社交媒体。

    模板用于从多个来源提取和去重菜肴条目。在菜肴名称的变体（例如"宫保鸡丁"与"宫爆鸡丁"）中自动融合相同的菜肴。支持菜单标准化、美食知识积累和跨文化菜肴对应。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> dishes = CulinaryDishSet(llm_client=llm, embedder=embedder)
        >>> menu = "1. Kung Pao Chicken - 宫保鸡丁。2. 宫爆鸡丁(四川焦糖鸡丁)"
        >>> dishes.feed_text(menu)
        >>> dishes.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化食物菜肴集合模板。

        Args:
            llm_client (BaseChatModel): 用于提取的 LLM。
            embedder (Embeddings): 用于检索和可视化的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoSet 的其他参数。
        """
        super().__init__(
            item_schema=CulinaryDish,
            key_extractor=lambda x: x.name.strip().lower(),
            llm_client=llm_client,
            embedder=embedder,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_items_for_search: int = 10,
        top_k_items_for_chat: int = 10,
    ) -> None:
        """
        使用 OntoSight 可视化菜肴集合。

        Args:
            top_k_items_for_search (int): 检索的菜肴数。默认 10。
            top_k_items_for_chat (int): 对话上下文中的菜肴数。默认 10。
        """

        def item_label_extractor(item: CulinaryDish) -> str:
            parts = [item.name]
            if item.cuisine:
                parts.append(f"({item.cuisine})")
            return " ".join(parts)

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_items_for_search=top_k_items_for_search,
            top_k_items_for_chat=top_k_items_for_chat,
        )
