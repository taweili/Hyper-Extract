"""规章条文清单 - 将规章制度拆解为逐条的原子化条文，方便快速索引。

适用于条文检索、全文比对等。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class Clause(BaseModel):
    """规章条文"""
    clauseId: str = Field(description="条文编号，如第1条、第2.1款")
    title: str = Field(description="条目标题/主题", default="")
    content: str = Field(description="条文内容")
    category: str = Field(description="条文分类：总则、权利义务、程序、处罚、附则、其他", default="其他")


_PROMPT = """## 角色与任务
你是一位专业的规章制度条文拆解专家，请将文本拆解为逐条的原子化条文。

## 提取规则
1. 将规章制度按其自然结构拆解为独立的条文
2. 为每条条文分配编号（如第1条、第2.1款等）
3. 提取条文的内容
4. 为条文添加适当的标题或主题（如有）
5. 为每条条文指定分类：总则、权利义务、程序、处罚、附则、其他

### 约束条件
- 保持条文内容与原文一致
- 不要遗漏任何条文
- 保持条文的完整性

## 源文本:
{source_text}
"""


class ClauseList(AutoList[Clause]):
    """
    适用文档: 公司内部管理制度、行政法规、操作手册、合规指南

    功能介绍:
    将规章制度拆解为逐条的原子化条文，方便快速索引。适用于条文检索、全文比对等。

    Example:
        >>> template = ClauseList(llm_client=llm, embedder=embedder)
        >>> template.feed_text("宇宙第一摸鱼公司员工考勤管理制度...")
        >>> for clause in template:
        ...     print(f"{clause.clauseId}: {clause.content}")
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
        初始化规章条文清单模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=Clause,
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
        展示规章条文清单。
        
        Args:
            top_k_for_search: 语义检索返回的条文数量，默认为 3
            top_k_for_chat: 问答使用的条文数量，默认为 3
        """
        def itemLabelExtractor(item: Clause) -> str:
            if item.title:
                return f"{item.clauseId}: {item.title}"
            return f"{item.clauseId}"
        
        super().show(
            item_label_extractor=itemLabelExtractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
