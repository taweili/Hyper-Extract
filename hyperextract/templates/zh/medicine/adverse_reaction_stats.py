"""不良反应统计 - 提取各系统的不良反应表现及其发生率描述。

适用于药品说明书中关于不良反应的内容。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class AdverseReactionItem(BaseModel):
    """不良反应条目"""
    system: str = Field(description="系统名称，如胃肠道、全身、皮肤等")
    reaction: str = Field(description="不良反应表现")
    incidence: str = Field(description="发生率")
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的临床药师，请从文本中提取各系统的不良反应表现及其发生率描述，构建不良反应统计。

## 核心概念定义
- **条目 (Item)**：从文本中提取的条目

## 提取规则
1. 提取所有不良反应，包括系统名称、不良反应表现和发生率
2. 为每个不良反应添加详细描述（如果文本中提供）
3. 保持不良反应表现与原文一致

### 领域特定规则
- 不良反应名称保持原文
- 发生率表示法保持原文，如 5.2%、常见、罕见

### 约束条件
- 只提取文本中明确提及的不良反应和发生率
- 保持客观准确，不添加文本中没有的信息

## 药品说明书:
{source_text}
"""


class AdverseReactionStats(AutoList[AdverseReactionItem]):
    """
    适用文档: 药品说明书、药物安全性监测报告

    功能介绍:
    提取各系统的不良反应表现及其发生率描述，适用于药物警戒、安全性评价。

    Example:
        >>> template = AdverseReactionStats(llm_client=llm, embedder=embedder)
        >>> template.feed_text("胃肠道不良反应：恶心(5.2%)、呕吐(2.6%)...")
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
        初始化不良反应统计模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=AdverseReactionItem,
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
        展示不良反应统计。
        
        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """
        def item_label_extractor(item: AdverseReactionItem) -> str:
            return f"{item.system}: {item.reaction} ({item.incidence})"
        
        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )