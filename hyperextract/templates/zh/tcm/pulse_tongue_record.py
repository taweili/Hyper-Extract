"""舌脉特征提取 - 结构化提取舌象（质、苔）与脉象描述，用于统计分析。

适用于中医诊断客观化研究。
"""

from typing import Any
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import AutoList

class PulseTongueItem(BaseModel):
    """舌脉特征项"""
    type: str = Field(description="特征类型：舌象、脉象")
    subType: str = Field(description="子类型：如舌质、舌苔、脉位、脉率、脉势等")
    feature: str = Field(description="具体特征描述，如淡红、薄白、浮、沉、迟、数等")
    description: str = Field(description="详细描述", default="")
    clinicalSignificance: str = Field(description="临床意义", default="")
    source: str = Field(description="来源，如医案名称、章节等", default="")

_PROMPT = """## 角色与任务
你是一位专业的中医诊断专家，请从文本中提取舌象和脉象的特征信息。

## 核心概念定义
- **条目 (Item)**：从文本中提取的重复模式实例，如舌象特征或脉象特征

## 提取规则
1. 提取所有舌象特征，包括舌质（颜色、形态）、舌苔（颜色、厚薄、干湿等）
2. 提取所有脉象特征，包括脉位（浮、沉）、脉率（迟、数）、脉势（有力、无力）等
3. 为每个特征指定类型和子类型
4. 保持特征描述与原文一致
5. 提取特征的临床意义（如果有）
6. 提取特征的来源信息（如果有）

### 文言文特殊处理指导
- **舌象描述解析**：文言舌象常采用连写表述（如"舌淡红苔薄白"→拆分为舌质淡红、舌苔薄白）
- **脉象术语理解**：文言脉象术语需准确识别（如"浮紧脉"→浮脉、紧脉）
- **复合特征拆分**：文言中常将多个特征合并描述，需分别提取到对应字段
- **临床意义关联**：文言中舌脉特征与临床意义常关联表述，需准确提取对应关系

### 源文本:
"""

# ==============================================================================
# 3. 模板类
# ==============================================================================

class PulseTongueRecord(AutoList[PulseTongueItem]):
    """
    适用文档: 中医医案、诊断记录
    
    功能介绍:
    从中医文本中结构化提取舌象（质、苔）与脉象描述，用于统计分析和中医诊断客观化研究。
    
    Example:
        >>> template = PulseTongueRecord(llm_client=llm, embedder=embedder)
        >>> template.feed_text("...")
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
        初始化舌脉特征提取模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=PulseTongueItem,
            llm_client=llm_client,
            embedder=embedder,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        展示舌脉特征记录。
        
        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """
        def item_label_extractor(item: PulseTongueItem) -> str:
            return f"{item.type} - {item.subType}"
        
        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
