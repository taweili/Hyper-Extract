"""规章元数据快照 - 提取制度的名称、版本、适用范围、生效日期及核心宗旨。

适用于制度概览、版本管理等。
"""

from typing import Any, Optional, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class RegulationInfo(BaseModel):
    """规章元数据信息"""
    title: str = Field(description="规章名称")
    version: Optional[str] = Field(description="版本号", default=None)
    issuer: Optional[str] = Field(description="发布机构", default=None)
    issueDate: Optional[str] = Field(description="发布日期", default=None)
    effectiveDate: Optional[str] = Field(description="生效日期", default=None)
    expiryDate: Optional[str] = Field(description="失效日期", default=None)
    scope: List[str] = Field(description="适用范围", default_factory=list)
    targetAudience: List[str] = Field(description="适用对象", default_factory=list)
    corePurpose: str = Field(description="核心宗旨/目的", default="")
    keywords: List[str] = Field(description="关键词/标签", default_factory=list)
    relatedRegulations: List[str] = Field(description="关联规章", default_factory=list)


_PROMPT = """## 角色与任务
你是一位专业的规章制度分析专家，请从文本中提取该规章制度的元数据信息，构建规章元数据快照。

## 提取规则
1. 提取规章的完整名称
2. 提取版本号（如有）
3. 提取发布机构
4. 提取发布日期、生效日期、失效日期（如有）
5. 提取适用范围
6. 提取适用对象
7. 提取核心宗旨或目的（100-200字）
8. 提取关键词或标签
9. 提取关联的其他规章

### 约束条件
- 只提取文本中明确提及的信息，不添加额外内容
- 保持客观准确
- 信息缺失时留空，不要编造

## 源文本:
{source_text}
"""


class RegulationProfile(AutoModel[RegulationInfo]):
    """
    适用文档: 公司内部管理制度、行政法规、操作手册、合规指南

    功能介绍:
    提取制度的名称、版本、适用范围、生效日期及核心宗旨。适用于制度概览、版本管理等。

    Example:
        >>> template = RegulationProfile(llm_client=llm, embedder=embedder)
        >>> template.feed_text("宇宙第一摸鱼公司员工考勤管理制度...")
        >>> print(template.data.title)
        >>> print(template.data.effectiveDate)
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
        初始化规章元数据快照模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            data_schema=RegulationInfo,
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
        top_k: int = 3,
    ):
        """
        展示规章元数据快照。
        
        Args:
            top_k: 问答使用的条目数量，默认为 3
        """
        def label_extractor(item: RegulationInfo) -> str:
            if item.version:
                return f"{item.title} (v{item.version})"
            return item.title
        
        super().show(
            label_extractor=label_extractor,
            top_k=top_k,
        )
