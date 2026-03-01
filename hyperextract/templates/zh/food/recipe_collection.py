"""菜谱名录 - 去重提取文本中出现的所有独立菜品实体及基本分类。

适用于菜单数字化、菜品库索引构建。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet


class RecipeEntry(BaseModel):
    """菜品条目"""

    name: str = Field(description="菜品名称，保持与原文一致")
    category: str = Field(description="菜品分类：凉菜、热菜、主食、甜品、小吃、饮品等")
    price: str = Field(description="价格，如 ¥68、18元", default="")
    description: str = Field(description="简要描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的餐饮知识专家，请从文本中提取所有独立菜品实体，形成菜谱名录。

## 核心概念定义
- **元素 (Element)**：具有唯一键的知识单元，即菜品实体

## 提取规则
### 核心约束
1. 提取所有独立菜品：每个菜品只能对应一条记录，禁止重复
2. 为每个菜品指定分类：凉菜、热菜、主食、甜品、小吃、饮品等
3. 保持菜品名称与原文一致
4. 如有价格信息，一并提取

### 约束条件
- 去重：同一菜品只保留一条记录
- 保持客观准确，不添加文本中没有的信息
- 菜品名称大小写需与原文保持一致

### 领域特定规则
- 菜单中常见的分类：凉菜、热菜、主食、甜品、小吃、饮品
- 同一菜品在不同分类下出现时，保留所有出现过的分类

## 源文本:
{source_text}
"""


class RecipeCollection(AutoSet[RecipeEntry]):
    """
    适用文档: 餐厅菜单、菜谱集、美食手册

    功能介绍:
    去重提取文本中出现的所有独立菜品实体及基本分类，适用于菜单数字化、菜品库索引构建。

    Example:
        >>> template = RecipeCollection(llm_client=llm, embedder=embedder)
        >>> template.feed_text("凉拌黄瓜 ¥18, 红烧肉 ¥68, 扬州炒饭 ¥28...")
        >>> print(list(template))
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化菜谱名录模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=RecipeEntry,
            key_extractor=lambda x: x.name,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        展示菜谱名录。

        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """

        def item_label_extractor(item: RecipeEntry) -> str:
            return f"{item.name} ({item.category})"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
