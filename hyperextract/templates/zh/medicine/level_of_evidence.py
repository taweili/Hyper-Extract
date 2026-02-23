"""证据评级表 - 提取指南中的具体推荐意见及其对应的证据等级。

适用于临床诊疗指南中关于推荐意见和证据等级的内容。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class EvidenceItem(BaseModel):
    """证据条目"""

    recommendation: str = Field(description="推荐意见")
    evidenceLevel: str = Field(description="证据等级，如A、B、C、1a、1b等")
    recommendationLevel: str = Field(description="推荐级别，如强推荐、弱推荐等")
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的循证医学专家，请从文本中提取指南中的具体推荐意见及其对应的证据等级，构建证据评级表。

## 核心概念定义
- **条目 (Item)**：本模板中的"条目"指证据条目，包含推荐意见、证据等级、推荐级别和详细描述的结构化信息。

## 提取规则
1. 提取所有推荐意见及其对应的证据等级
2. 为每个推荐意见指定推荐级别（如强推荐、弱推荐等）
3. 为每个推荐意见添加详细描述（如果文本中提供）
4. 保持推荐意见与原文一致

### 约束条件
- 只提取文本中明确提及的推荐意见和证据等级
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""


class LevelOfEvidence(AutoList[EvidenceItem]):
    """
    适用文档: 临床诊疗指南、循证医学指南

    功能介绍:
    提取指南中的具体推荐意见及其对应的证据等级，适用于设计临床质控方案、科研引用。

    Example:
        >>> template = LevelOfEvidence(llm_client=llm, embedder=embedder)
        >>> template.feed_text("推荐级别A，证据等级1a：所有2型糖尿病患者应接受生活方式干预...")
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
        初始化证据评级表模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=EvidenceItem,
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
        展示证据评级表。

        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """

        def item_label_extractor(item: EvidenceItem) -> str:
            return f"{item.recommendationLevel} (证据等级: {item.evidenceLevel})"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_items_for_search=top_k_for_search,
            top_k_items_for_chat=top_k_for_chat,
        )
