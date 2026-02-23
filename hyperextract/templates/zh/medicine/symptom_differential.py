"""鉴别诊断表 - 汇总症状与其对应的鉴别疾病列表，形成症状-疾病映射。

适用于医学教科书与专著中关于症状鉴别诊断的内容。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet


class SymptomDifferentialItem(BaseModel):
    """鉴别诊断条目"""
    symptom: str = Field(description="症状名称")
    diseases: list[str] = Field(description="对应的鉴别疾病列表")
    description: str = Field(description="症状描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的诊断学家，请从文本中提取症状与其对应的鉴别疾病列表，构建鉴别诊断表。

## 核心概念定义
- **元素 (Element)**：本模板中的"元素"指鉴别诊断条目，包含症状名称、对应的鉴别疾病列表和症状描述的结构化信息。

## 提取规则
1. 提取所有症状及其对应的鉴别疾病列表
2. 为每个症状添加简要描述（如果文本中提供）
3. 保持症状名称与原文一致
4. 确保每个症状对应的疾病列表完整

### 约束条件
- 只提取文本中明确提及的症状和疾病
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""


class SymptomDifferential(AutoSet[SymptomDifferentialItem]):
    """
    适用文档: 医学教科书、医学专著、诊断学教材

    功能介绍:
    汇总症状与其对应的鉴别疾病列表，形成症状-疾病映射，适用于CDSS辅助诊断、教学系统。

    Example:
        >>> template = SymptomDifferential(llm_client=llm, embedder=embedder)
        >>> template.feed_text("胸痛的鉴别诊断包括冠心病、胸膜炎、肺炎等...")
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
        初始化鉴别诊断表模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=SymptomDifferentialItem,
            key_extractor=lambda x: x.symptom,
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
        展示鉴别诊断表。
        
        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """
        def label_extractor(item: SymptomDifferentialItem) -> str:
            return f"{item.symptom}: {', '.join(item.diseases[:3])}{'...' if len(item.diseases) > 3 else ''}"
        
        super().show(
            label_extractor=label_extractor,
            top_k_items_for_search=top_k_for_search,
            top_k_items_for_chat=top_k_for_chat,
        )