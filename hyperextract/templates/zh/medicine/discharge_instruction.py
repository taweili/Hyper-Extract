"""出院医嘱摘要 - 提取出院带药、复诊计划及康复建议的结构化信息。

适用于出院小结中关于出院医嘱的内容。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class MedicationItem(BaseModel):
    """出院带药项"""
    name: str = Field(description="药物名称")
    dosage: str = Field(description="剂量")
    usage: str = Field(description="用法")
    frequency: str = Field(description="频次")


class FollowUpItem(BaseModel):
    """复诊计划项"""
    time: str = Field(description="时间")
    department: str = Field(description="科室")
    examItems: List[str] = Field(description="检查项目", default_factory=list)


class DischargeInstructionInfo(BaseModel):
    """出院医嘱信息"""

    medications: List[MedicationItem] = Field(
        description="出院带药列表，每个药物包含名称、剂量、用法、频次等信息",
        default_factory=list
    )
    followUp: List[FollowUpItem] = Field(
        description="复诊计划列表，每个复诊包含时间、科室、检查项目等信息",
        default_factory=list
    )
    rehabilitation: List[str] = Field(description="康复建议列表", default_factory=list)
    diet: List[str] = Field(description="饮食建议列表", default_factory=list)
    activity: List[str] = Field(description="活动建议列表", default_factory=list)
    notes: List[str] = Field(description="其他注意事项列表", default_factory=list)


_PROMPT = """## 角色与任务
你是一位专业的医生，请从文本中提取出院带药、复诊计划及康复建议的结构化信息，构建出院医嘱摘要。

## 提取规则
1. 提取所有出院带药信息，每个药物包含名称、剂量、用法、频次等信息
2. 提取所有复诊计划信息，每个复诊包含时间、科室、检查项目等信息
3. 提取所有康复建议、饮食建议、活动建议和其他注意事项
4. 保持信息与原文一致

### 领域特定规则
- 药物名称保持原文，如阿司匹林、二甲双胍
- 剂量单位保持原文，如 mg、ml
- 医学缩写保持原文，如 qd（每日一次）、bid（每日两次）

### 约束条件
- 只提取文本中明确提及的信息
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""


class DischargeInstruction(AutoModel[DischargeInstructionInfo]):
    """
    适用文档: 出院小结、出院记录

    功能介绍:
    提取出院带药、复诊计划及康复建议的结构化信息，适用于患者随访、慢病续方。

    Example:
        >>> template = DischargeInstruction(llm_client=llm, embedder=embedder)
        >>> template.feed_text("出院带药：阿司匹林100mg qd...")
        >>> print(template.data.medications)
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
        初始化出院医嘱摘要模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            data_schema=DischargeInstructionInfo,
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
        展示出院医嘱摘要。

        Args:
            top_k: 问答使用的条目数量，默认为 3
        """

        def label_extractor(item: DischargeInstructionInfo) -> str:
            return "出院医嘱摘要"

        super().show(
            label_extractor=label_extractor,
            top_k=top_k,
        )
