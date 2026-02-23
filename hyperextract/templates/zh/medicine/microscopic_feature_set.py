"""微观特征集 - 提取免疫组化指标（如 HER2+, Ki67）及基因突变状态。

适用于病理报告中关于免疫组化和分子检测的内容。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet


class MicroscopicFeatureItem(BaseModel):
    """微观特征条目"""
    featureName: str = Field(description="特征名称，如免疫组化指标、基因突变等")
    featureType: str = Field(description="特征类型：免疫组化、基因突变、其他等")
    value: str = Field(description="特征值，如阳性、阴性、百分比等")
    description: str = Field(description="特征描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的病理学家，请从文本中提取免疫组化指标（如 HER2+, Ki67）及基因突变状态，构建微观特征集。

## 核心概念定义
- **元素 (Element)**：本模板中的"元素"指微观特征条目，包含特征名称、特征类型、特征值和特征描述的结构化信息。

## 提取规则
1. 提取所有免疫组化指标和基因突变状态
2. 为每个特征指定类型：免疫组化、基因突变、其他等
3. 为每个特征添加特征值，如阳性、阴性、百分比等
4. 为每个特征添加简要描述（如果文本中提供）
5. 保持特征名称与原文一致

### 约束条件
- 只提取文本中明确提及的特征和值
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""


class MicroscopicFeatureSet(AutoSet[MicroscopicFeatureItem]):
    """
    适用文档: 病理报告、免疫组化结果、分子检测报告

    功能介绍:
    提取免疫组化指标（如 HER2+, Ki67）及基因突变状态，适用于靶向药匹配、科研入组筛选。

    Example:
        >>> template = MicroscopicFeatureSet(llm_client=llm, embedder=embedder)
        >>> template.feed_text("免疫组化结果：ER(+, 90%), PR(+, 70%), HER2(2+)...")
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
        初始化微观特征集模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=MicroscopicFeatureItem,
            key_extractor=lambda x: x.featureName,
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
        展示微观特征集。
        
        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """
        def label_extractor(item: MicroscopicFeatureItem) -> str:
            return f"{item.featureName} ({item.featureType}): {item.value}"
        
        super().show(
            label_extractor=label_extractor,
            top_k_items_for_search=top_k_for_search,
            top_k_items_for_chat=top_k_for_chat,
        )