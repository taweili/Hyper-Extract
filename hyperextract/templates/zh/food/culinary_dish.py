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

    模板用于构建标准化的菜肴知识库，通过**精确的菜肴名称为键进行信息累加**。
    自动将来自多个文本源的同一菜肴信息合并为一条完整条目，从各源中积累食材、烹饪方法、地域特征和风味描述。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> dishes = CulinaryDishSet(llm_client=llm, embedder=embedder)
        >>> # 来源 1：提取基本信息（名称、菜系、地域）
        >>> dishes.feed_text("宫保鸡丁是来源于四川的著名菜肴，主要食材有鸡肉、花生、干辣椒。")
        >>> # 来源 2：提取补充信息（风味、烹饪手法）
        >>> dishes.feed_text("宫保鸡丁采用大火快速炒制，花生要烘烤，整体风味是甜辣鲜香。")
        >>> dishes.show()  # 显示合并后包含两个来源信息的"宫保鸡丁"条目
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
            embedder (Embeddings): 用于语义检索和知识图谱可视化的嵌入模型。
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
