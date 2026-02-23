"""禁忌症清单 - 提取绝对禁忌（如孕妇、严重肾衰竭等）的明确列表。

适用于药品说明书中关于禁忌症的内容。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class ContraindicationItem(BaseModel):
    """禁忌症条目"""
    contraindication: str = Field(description="禁忌症描述")
    contraindicationType: str = Field(description="禁忌症类型：绝对禁忌、相对禁忌等")
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的临床药师，请从文本中提取绝对禁忌（如孕妇、严重肾衰竭等）的明确列表，构建禁忌症清单。

## 核心概念定义
- **条目 (Item)**：本模板中的"条目"指禁忌症条目，包含禁忌症描述、禁忌症类型和详细描述的结构化信息。

## 提取规则
1. 提取所有禁忌症，包括绝对禁忌和相对禁忌
2. 为每个禁忌症指定类型：绝对禁忌、相对禁忌等
3. 为每个禁忌症添加详细描述（如果文本中提供）
4. 保持禁忌症描述与原文一致

### 约束条件
- 只提取文本中明确提及的禁忌症
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""


class ContraindicationList(AutoList[ContraindicationItem]):
    """
    适用文档: 药品说明书、临床用药指南

    功能介绍:
    提取绝对禁忌（如孕妇、严重肾衰竭等）的明确列表，适用于处方拦截、用药安全监测。

    Example:
        >>> template = ContraindicationList(llm_client=llm, embedder=embedder)
        >>> template.feed_text("绝对禁忌症：对二甲双胍及其他成分过敏者...")
        >>> template.show()
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
        初始化禁忌症清单模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=ContraindicationItem,
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
        展示禁忌症清单。
        
        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """
        def item_label_extractor(item: ContraindicationItem) -> str:
            return f"{item.contraindication} ({item.contraindicationType})"
        
        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )