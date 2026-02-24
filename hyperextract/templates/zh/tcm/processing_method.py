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
- **条目 (Item)**：从文本中提取的重复模式实例，如炮制方法条目

## 提取规则
### 核心约束
1. 识别文本中提到的所有药物及其炮制方法
2. 提取每种炮制方法的名称
3. 提取每种炮制方法的具体工艺流程
4. 提取炮制对药效的影响

### 领域特定规则
- 常用炮制方法：蜜炙、酒炒、醋制、盐制、炒、煅等

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
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
