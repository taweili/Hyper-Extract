"""TNM 分期表 - 提取肿瘤大小(T)、淋巴结(N)、转移(M)及分期结果。

适用于病理报告中关于肿瘤分期的内容。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class TumorStagingInfo(BaseModel):
    """肿瘤分期信息"""
    tStage: str = Field(description="T分期，如T1、T2、T3、T4等")
    nStage: str = Field(description="N分期，如N0、N1、N2、N3等")
    mStage: str = Field(description="M分期，如M0、M1等")
    pathologicalStage: str = Field(description="病理分期，如I期、II期、III期、IV期等")
    tDetails: str = Field(description="T分期详细描述，如肿瘤大小")
    nDetails: str = Field(description="N分期详细描述，如淋巴结转移数量")
    mDetails: str = Field(description="M分期详细描述，如远处转移部位")


_PROMPT = """## 角色与任务
你是一位专业的病理学家，请从文本中提取肿瘤大小(T)、淋巴结(N)、转移(M)及分期结果，构建TNM分期表。

## 提取规则
1. 提取T分期、N分期、M分期和病理分期
2. 为每个分期添加详细描述：
   - T分期详细描述：肿瘤大小、浸润深度等
   - N分期详细描述：淋巴结转移数量、部位等
   - M分期详细描述：远处转移部位等
3. 保持信息与原文一致

### 领域特定规则
- TNM分期表示法保持原文，如 T1、T2、N0、M0
- 分期表示法保持原文，如 I期、II期、III期、IV期

### 约束条件
- 只提取文本中明确提及的信息
- 保持客观准确，不添加文本中没有的信息

## 病理报告:
{source_text}
"""


class TumorStagingItem(AutoModel[TumorStagingInfo]):
    """
    适用文档: 病理报告、肿瘤分期记录

    功能介绍:
    提取肿瘤大小(T)、淋巴结(N)、转移(M)及分期结果，适用于肿瘤登记、预后评估。

    Example:
        >>> template = TumorStagingItem(llm_client=llm, embedder=embedder)
        >>> template.feed_text("T分期：T2（肿瘤最大径>2cm且≤5cm）...")
        >>> print(template.data.pathologicalStage)
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
        初始化TNM分期表模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            data_schema=TumorStagingInfo,
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
        展示TNM分期表。
        
        Args:
            top_k: 问答使用的条目数量，默认为 3
        """
        def label_extractor(item: TumorStagingInfo) -> str:
            return f"TNM分期: {item.tStage}{item.nStage}{item.mStage} ({item.pathologicalStage})"
        
        super().show(
            label_extractor=label_extractor,
            top_k=top_k,
        )