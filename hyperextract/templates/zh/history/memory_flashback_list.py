"""回忆片段清单 - 提取口述中提到的具体轶事、感悟或对特定历史时刻的侧面描写。

适用于口述历史、回忆录、个人日记。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class MemoryFragment(BaseModel):
    """回忆片段条目"""
    content: str = Field(description="回忆内容原文")
    type: str = Field(description="类型：轶事、感悟、历史时刻、人物描写")
    time: str = Field(description="相关时间", default="")
    location: str = Field(description="相关地点", default="")
    emotion: str = Field(description="情感色彩：感慨、怀念、愤慨、欣慰", default="")
    description: str = Field(description="补充描述", default="")


_PROMPT = """## 角色与任务
请从文本中提取口述历史或回忆录中的回忆片段。

## 提取规则
### 核心约束
1. 每个条目对应一个独立的回忆片段
2. 内容应与原文保持一致

### 领域特定规则
- 类型：轶事、感悟、历史时刻、人物描写
- 情感色彩：感慨、怀念、愤慨、欣慰
- 尽量提取原文中的具体描述

## 源文本:
{source_text}
"""


class MemoryFlashbackList(AutoList[MemoryFragment]):
    """
    适用文档: 口述历史、回忆录、个人日记

    功能介绍:
    提取口述中提到的具体轶事、感悟或对特定历史时刻的侧面描写，适用于历史细节补充、情感分析。

    设计说明:
    - 条目（MemoryFragment）：存储回忆片段信息，包括内容、类型、时间、地点、情感

    Example:
        >>> template = MemoryFlashbackList(llm_client=llm, embedder=embedder)
        >>> template.feed_text("苏轼回忆起在黄州的日子，感慨万千...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化回忆片段清单模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            chunk_size: 每个分块的最大字符数，默认为 512（历史文本信息量大，需较小分块）
            chunk_overlap: 分块之间的重叠字符数，默认为 64
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=MemoryFragment,
            llm_client=llm_client,
            embedder=embedder,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 5,
        top_k_for_chat: int = 5,
    ):
        """
        展示回忆片段清单。

        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 5
            top_k_for_chat: 问答使用的条目数量，默认为 5
        """
        def item_label_extractor(item: MemoryFragment) -> str:
            return f"[{item.type}] {item.content[:30]}..."

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
