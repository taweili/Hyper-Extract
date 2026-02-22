"""百科条目 - 针对单一主体提取结构化的属性信息（类似信息框 Infobox）。

适用于维基百科、专业词典词条等。
"""

from typing import Any, Optional, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class EncyclopediaInfo(BaseModel):
    """百科条目信息框"""
    title: str = Field(description="条目标题")
    entityType: str = Field(description="实体类型：人物、地点、组织、事件、概念、物品、其他")
    alternativeNames: List[str] = Field(description="别名、俗称、外文名称", default_factory=list)
    category: List[str] = Field(description="分类标签", default_factory=list)
    summary: str = Field(description="摘要/简介", default="")
    attributes: List[str] = Field(description="关键属性列表，每个元素格式为'属性名: 属性值'", default_factory=list)
    keyEvents: List[str] = Field(description="重要事件/里程碑", default_factory=list)
    relatedConcepts: List[str] = Field(description="相关概念/条目", default_factory=list)


_PROMPT = """你是一位专业的百科全书编辑。请从文本中提取单一主体的结构化属性信息，构建百科条目信息框。

### 提取规则
1. 识别文本的核心主体（人物、地点、组织、事件、概念等）
2. 为主体指定类型：人物、地点、组织、事件、概念、物品、其他
3. 提取所有别名、俗称或外文名称
4. 提取分类标签（如"科学家"、"数学"、"中国古代"）
5. 撰写 100-200 字的摘要
6. 提取关键属性，每个格式为'属性名: 属性值'（如'出生日期: 429年'、'国籍: 中国'）
7. 提取重要事件或里程碑
8. 提取相关概念或条目

### 约束条件
- 只提取文本中明确提及的信息，不添加额外内容
- 属性名尽量简洁明了
- 保持客观准确，符合百科全书风格

### 源文本:
"""


class EncyclopediaItem(AutoModel[EncyclopediaInfo]):
    """
    适用文档: 维基百科条目、百度百科条目、专业词典词条

    功能介绍:
    针对单一主体提取结构化的属性信息（类似信息框 Infobox）。适用于维基百科、专业词典词条等。

    Example:
        >>> template = EncyclopediaItem(llm_client=llm, embedder=embedder)
        >>> template.feed_text("祖冲之（429年－500年），字文远，范阳遒县人...")
        >>> print(template.data.title)
        >>> print(template.data.summary)
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
        初始化百科条目模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            data_schema=EncyclopediaInfo,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )
