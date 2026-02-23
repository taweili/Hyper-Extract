"""违规处罚对照表 - 去重汇总特定的违规行为及其对应的后果，形成清晰的处罚台账。

适用于内部风控、合规检查等。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet


class PenaltyEntry(BaseModel):
    """违规处罚条目"""
    violation: str = Field(description="违规行为描述")
    severity: str = Field(description="严重程度：轻微、一般、严重、特别严重")
    penalty: str = Field(description="处罚措施")
    applicableClause: str = Field(description="适用条款", default="")
    notes: str = Field(description="备注说明", default="")


_PROMPT = """## 角色与任务
你是一位专业的合规分析专家，请从文本中提取所有违规行为及其对应的处罚措施，形成违规处罚对照表。

## 提取规则
1. 提取所有违规行为及其对应的处罚措施
2. 为每条违规行为指定严重程度：轻微、一般、严重、特别严重
3. 保持违规行为和处罚措施的准确性
4. 记录适用的条款（如有）
5. 添加备注说明（如有）

### 约束条件
- 去重：相同的违规行为和处罚措施组合只保留一条
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""


class PenaltyRegistry(AutoSet[PenaltyEntry]):
    """
    适用文档: 公司内部管理制度、行政法规、合规指南

    功能介绍:
    去重汇总特定的违规行为及其对应的后果，形成清晰的处罚台账。适用于内部风控、合规检查等。

    Example:
        >>> template = PenaltyRegistry(llm_client=llm, embedder=embedder)
        >>> template.feed_text("宇宙第一摸鱼公司员工考勤管理制度...")
        >>> for entry in template:
        ...     print(f"{entry.violation} -> {entry.penalty}")
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
        初始化违规处罚对照表模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=PenaltyEntry,
            key_extractor=lambda x: f"{x.violation}_{x.penalty}",
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
        展示违规处罚对照表。
        
        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """
        def itemLabelExtractor(item: PenaltyEntry) -> str:
            return f"{item.violation} ({item.severity})"
        
        super().show(
            item_label_extractor=itemLabelExtractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
