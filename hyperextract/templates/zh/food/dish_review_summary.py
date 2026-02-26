"""食评摘要清单 - 按菜品提取核心评价点、推荐等级及价格感知。

适用于探店笔记结构化、必吃榜单生成。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class ReviewItem(BaseModel):
    """食评条目"""

    dish_name: str = Field(description="菜品名称")
    recommendation_level: str = Field(description="推荐指数，如⭐⭐⭐⭐⭐ 或 4.5/5")
    highlights: List[str] = Field(description="亮点列表", default_factory=list)
    improvements: List[str] = Field(description="改进空间列表", default_factory=list)
    price_perception: str = Field(description="价格感知，如性价比高、略贵但值")
    description: str = Field(description="详细描述")


_PROMPT = """## 角色与任务
你是一位专业的美食评论家，请从文本中提取每道菜品的核心评价信息，形成食评摘要清单。

## 核心概念定义
- **条目 (Item)**：从文本中提取的重复模式实例，即单个菜品的评价信息

## 提取规则
### 核心约束
1. 提取文本中出现的每道菜品的评价信息
2. 为每个菜品提取推荐等级（如⭐⭐⭐⭐⭐）
3. 提取菜品亮点和可能的改进空间
4. 提取价格感知信息

### 约束条件
- 每个菜品作为独立条目提取
- 保持菜品名称与原文一致
- 推荐等级使用原文的表达方式

### 领域特定规则
- 推荐指数常用表达：⭐⭐⭐⭐⭐、4.5/5、强烈推荐
- 价格感知常用表达：性价比极高、实惠、略贵但值

### 源文本:
"""


class DishReviewSummary(AutoList[ReviewItem]):
    """
    适用文档: 美食探店评论、食评文章、必吃榜单

    功能介绍:
    按菜品提取核心评价点、推荐等级及价格感知，适用于探店笔记结构化、必吃榜单生成。

    Example:
        >>> template = DishReviewSummary(llm_client=llm, embedder=embedder)
        >>> template.feed_text("红烧肉：强烈推荐，肥而不腻，入口即化...")
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
        初始化食评摘要清单模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=ReviewItem,
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
        展示食评摘要清单。

        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """

        def label_extractor(item: ReviewItem) -> str:
            return f"{item.dish_name} - {item.recommendation_level}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
