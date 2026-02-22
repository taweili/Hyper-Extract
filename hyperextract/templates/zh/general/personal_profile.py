"""个人档案 - 聚合人物的静态属性（生卒年、学历、核心身份）。

适用于简历、人物简介、讣告摘要等。
"""

from typing import Any, Optional, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class PersonalInfo(BaseModel):
    """个人档案信息"""
    name: str = Field(description="姓名")
    gender: Optional[str] = Field(description="性别", default=None)
    birthDate: Optional[str] = Field(description="出生日期，格式为年-月-日或年份", default=None)
    deathDate: Optional[str] = Field(description="逝世日期，格式为年-月-日或年份", default=None)
    nationality: Optional[str] = Field(description="国籍", default=None)
    birthPlace: Optional[str] = Field(description="出生地", default=None)
    education: List[str] = Field(description="教育经历", default_factory=list)
    occupations: List[str] = Field(description="职业/身份", default_factory=list)
    coreIdentity: List[str] = Field(description="核心身份/标签", default_factory=list)
    majorAchievements: List[str] = Field(description="主要成就", default_factory=list)
    affiliations: List[str] = Field(description="所属组织/机构", default_factory=list)
    summary: str = Field(description="个人简介", default="")


_PROMPT = """你是一位专业的人物档案编辑。请从文本中提取该人物的静态属性信息，构建个人档案。

### 提取规则
1. 提取姓名、性别、出生日期、逝世日期、国籍、出生地等基本信息
2. 提取教育经历
3. 提取职业或身份信息
4. 提取核心身份标签
5. 提取主要成就
6. 提取所属组织或机构
7. 撰写 100-200 字的个人简介

### 时间格式要求
所有日期信息统一转换为「年-月-日」格式（如 429-01-01）或年份（如 429）。

### 约束条件
- 只提取文本中明确提及的信息，不添加额外内容
- 保持客观准确
- 若信息缺失时留空，不要编造

### 源文本:
"""


class PersonalProfile(AutoModel[PersonalInfo]):
    """
    适用文档: 简历、人物简介、讣告摘要、维基百科人物条目

    功能介绍:
    聚合人物的静态属性（生卒年、学历、核心身份）。适用于简历、人物简介、讣告摘要等。

    Example:
        >>> template = PersonalProfile(llm_client=llm, embedder=embedder)
        >>> template.feed_text("祖冲之（429年－500年），字文远，范阳遒县人...")
        >>> print(template.data.name)
        >>> print(template.data.birthDate)
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
        初始化个人档案模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            data_schema=PersonalInfo,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )
