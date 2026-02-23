"""药物性味归经 - 提取单味药的四气五味、归经、毒性及推荐剂量。

适用于中药基础数据库构建。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class HerbProperty(BaseModel):
    """药物性味归经信息"""
    name: str = Field(description="药物正名")
    alternativeNames: List[str] = Field(description="别名、俗称", default_factory=list)
    properties: List[str] = Field(description="四气：寒、热、温、凉、平", default_factory=list)
    flavors: List[str] = Field(description="五味：酸、苦、甘、辛、咸", default_factory=list)
    meridians: List[str] = Field(description="归经：如肺经、肝经、脾经等", default_factory=list)
    toxicity: str = Field(description="毒性：无毒、小毒、有毒、大毒", default="无毒")
    dosage: str = Field(description="推荐剂量", default="")
    collection: str = Field(description="采集时间和方法", default="")
    processing: str = Field(description="炮制方法", default="")
    indications: List[str] = Field(description="功效主治", default_factory=list)
    contraindications: List[str] = Field(description="配伍禁忌", default_factory=list)


_PROMPT = """## 角色与任务
你是一位专业的中药学家，请从文本中提取单味药的性味归经、毒性及推荐剂量等信息。

## 核心概念定义
- **对象 (Object)**：本模板中的"对象"指单一中药药物，包含正名、别名、四气、五味、归经、毒性、剂量、采集、炮制、功效主治、配伍禁忌等多个字段的结构化信息。

## 提取规则
1. 识别文本的核心药物主体
2. 提取药物的正名和所有别名、俗称
3. 提取药物的四气（寒、热、温、凉、平）
4. 提取药物的五味（酸、苦、甘、辛、咸）
5. 提取药物的归经（如肺经、肝经、脾经等）
6. 提取药物的毒性（无毒、小毒、有毒、大毒）
7. 提取药物的推荐剂量
8. 提取药物的采集时间和方法
9. 提取药物的炮制方法
10. 提取药物的功效主治
11. 提取药物的配伍禁忌

### 约束条件
- 只提取文本中明确提及的信息，不添加额外内容
- 保持客观准确，符合中药学专业术语规范

### 源文本:
"""


class HerbPropertyModel(AutoModel[HerbProperty]):
    """
    适用文档: 本草典籍、中药志、中药大辞典等
    
    功能介绍:
    提取单味药的四气五味、归经、毒性及推荐剂量，适用于中药基础数据库构建。
    
    Example:
        >>> template = HerbPropertyModel(llm_client=llm, embedder=embedder)
        >>> template.feed_text("人参，味甘，微寒，无毒。主补五脏，安精神...")
        >>> print(template.data.name)
        >>> print(template.data.properties)
        >>> print(template.data.flavors)
        >>> print(template.data.meridians)
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
        初始化药物性味归经模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            data_schema=HerbProperty,
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
        展示药物性味归经信息。
        
        Args:
            top_k: 问答使用的条目数量，默认为 3
        """
        def label_extractor(item: HerbProperty) -> str:
            return f"{item.name} ({', '.join(item.properties)}，{', '.join(item.flavors)})"
        
        super().show(
            label_extractor=label_extractor,
            top_k=top_k,
        )
