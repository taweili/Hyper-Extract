"""炮制方法列表 - 提取药物的不同炮制方法（如蜜炙、酒炒）及其对药效的影响。

适用于中药炮制规范、饮片管理。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class ProcessingMethodItem(BaseModel):
    """炮制方法条目"""
    herbName: str = Field(description="药物名称")
    methodName: str = Field(description="炮制方法名称：如蜜炙、酒炒、醋制、盐制等")
    process: str = Field(description="具体炮制工艺流程")
    effectChange: str = Field(description="炮制对药效的影响")
    application: str = Field(description="适用病症或方剂")


_PROMPT = """## 角色与任务
你是一位专业的中药炮制专家，请从文本中提取药物的不同炮制方法及其对药效的影响。

## 核心概念定义
- **条目 (Item)**：本模板中的"条目"指单一炮制方法，包含药物名称、炮制方法名称、具体工艺流程、对药效的影响、适用病症或方剂等字段的结构化信息。

## 提取规则
1. 识别文本中提到的所有药物及其炮制方法
2. 提取每种炮制方法的名称（如蜜炙、酒炒、醋制、盐制等）
3. 提取每种炮制方法的具体工艺流程
4. 提取炮制对药效的影响
5. 提取该炮制方法的适用病症或方剂

### 约束条件
- 只提取文本中明确提及的信息，不添加额外内容
- 保持客观准确，符合中药炮制专业术语规范

### 文言文特殊处理指导
- **炮制术语理解**：文言炮制术语需准确理解（如"炙"、"炒"、"煅"、"蒸"等）
- **工艺流程解析**：文言炮制工艺流程常采用简洁表述，需完整理解其步骤
- **药效变化描述**：文言中对药效变化的描述需准确提取（如"增强"、"缓和"、"改变"等）
- **古代计量单位**：保留古代剂量单位和工艺描述，无需转换

### 源文本:
"""


class ProcessingMethod(AutoList[ProcessingMethodItem]):
    """
    适用文档: 中药炮制规范、饮片管理手册、本草典籍等
    
    功能介绍:
    提取药物的不同炮制方法（如蜜炙、酒炒）及其对药效的影响，适用于中药炮制规范、饮片管理。
    
    Example:
        >>> template = ProcessingMethod(llm_client=llm, embedder=embedder)
        >>> template.feed_text("甘草：蜜炙甘草，取净甘草片，加入炼蜜拌匀...")
        >>> for item in template.data:
        >>>     print(item.methodName)
        >>>     print(item.effectChange)
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
        初始化炮制方法列表模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=ProcessingMethodItem,
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
        展示炮制方法列表。
        
        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """
        def label_extractor(item: ProcessingMethodItem) -> str:
            return f"{item.herbName} - {item.methodName}"
        
        super().show(
            label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
