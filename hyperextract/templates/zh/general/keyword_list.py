"""关键词列表 - 从文本中提取关键词并附带分类、出现频次信息。

适用于内容标签生成、主题分析等场景。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class Keyword(BaseModel):
    """关键词条目"""
    term: str = Field(description="关键词")
    category: str = Field(description="分类：核心概念、术语、人名、机构名、其他")
    description: str = Field(description="关键词简要描述或上下文说明", default="")


_PROMPT = """## 角色与任务
你是一位专业的关键词提取专家，请从文本中提取所有关键词并附带分类和描述信息。

## 提取规则
1. 提取文本中的所有关键词和核心短语
2. 为每个关键词指定分类：核心概念、术语、人名、机构名、其他
3. 为每个关键词添加简要描述，说明其在文本中的含义或上下文

### 约束条件
- 确保关键词准确，不添加文本中没有的信息
- 保持关键词大小写与原文一致

### 源文本:
"""


class KeywordList(AutoList[Keyword]):
    """
    适用文档: 任意文本、博客文章、学术论文

    功能介绍:
    从文本中提取关键词并附带分类和描述信息。适用于内容标签生成和主题分析。

    Example:
        >>> template = KeywordList(llm_client=llm, embedder=embedder)
        >>> template.feed_text("银河星际宣布神舟-50首飞成功...")
        >>> for keyword in template:
        ...     print(f"{keyword.term} ({keyword.category}): {keyword.description}")
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
        初始化关键词列表模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=Keyword,
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
        展示关键词列表。
        
        Args:
            top_k_for_search: 语义检索返回的关键词数量，默认为 3
            top_k_for_chat: 问答使用的关键词数量，默认为 3
        """
        def itemLabelExtractor(item: Keyword) -> str:
            return f"{item.term} ({item.category})"
        
        super().show(
            item_label_extractor=itemLabelExtractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
