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
    菜肴知识条目。
    """

    name: str = Field(description="菜肴的标准名称，例如宫保鸡丁。")
    origin: Optional[str] = Field(
        None, description="菜系、地理原产地及适应季节（如：四川/夏季）。"
    )
    ingredients: Optional[str] = Field(
        None,
        description="主要食材、蛋白质类型及核心酱料。"
    )
    profile: Optional[str] = Field(
        None,
        description="风味特征（酸甜苦辣）、口感及烹饪方法（蒸炒炸）。"
    )
    description: Optional[str] = Field(
        None,
        description="其它描述，包括饮食宜忌、配菜建议及历史背景。"
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是美食知识库管理员。从文本中提取菜肴信息。\n\n"
    "提取规则:\n"
    "- 识别菜肴标准名称。\n"
    "- **origin**: 整合菜系、城市及季节信息。\n"
    "- **ingredients**: 列出核心食材和配料。\n"
    "- **profile**: 描述味道、质地及烹饪工艺。\n"
    "- **description**: 包含文化背景、饮食特征等补充信息。\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class CulinaryDishSet(AutoSet[CulinaryDish]):
    """
    适用文档: 菜单、食谱、美食博客。

    模板用于构建标准化的菜肴知识库。
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
        top_k_for_search: int = 10,
        top_k_for_chat: int = 10,
    ) -> None:
        def item_label_extractor(item: CulinaryDish) -> str:
            parts = [item.name]
            if item.origin:
                parts.append(f"({item.origin})")
            return " ".join(parts)

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
