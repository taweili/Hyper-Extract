from typing import List, Optional, Any, Callable
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================

class DiagnosticCriteria(BaseModel):
    """疾病的诊断标准与临床分类。"""
    disease_name: str = Field(description="标准化疾病名称（如‘2型糖尿病’、‘急性心肌梗死’）。")
    major_criteria: List[str] = Field(description="主要诊断指标（Major Criteria）或必备条件。")
    minor_criteria: List[str] = Field(description="次要诊断指标（Minor Criteria）或辅助条件。")
    exclusion_criteria: List[str] = Field(description="排除标准（即出现何种情况可排除该疾病）。")
    biomarkers: List[str] = Field(description="相关的关键生物标志物或实验室检查项（如‘HbA1c > 6.5%’）。")
    source_guideline: str = Field(description="该标准的来源，如‘ADA 2024 指南’、‘专家共识’。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位专业的临床指南解读专家。你的任务是从医学文献和指南中提取特定疾病的结构化诊断标准。\n\n"
    "提取原则：\n"
    "1. **疾病名标准化**：确保同一个疾病的所有信息被聚合到其标准的医学名称下。\n"
    "2. **严谨区分**：精确区分哪些是‘主标准’，哪些是‘次标准’或‘排除标准’。\n"
    "3. **信息累加**：如果你从多篇文献中提取了同一个疾病的诊断标准，请合并这些信息，并在 source_guideline 中记录所有来源。\n"
)

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================

class DiagnosticCriteriaSet(AutoSet[DiagnosticCriteria]):
    """
    适用于：[临床实践指南, 专家共识, 医学教材]

    用于从海量医学指南中聚合与维护疾病诊断标准的库模板。

    该模板利用 AutoSet 的键值累加特性，能够将不同年份、不同组织发布的关于同一疾病的诊断标准、标志物要求自动合并，形成最全面的诊疗参考。

    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # 初始化模板
        >>> criteria_lib = DiagnosticCriteriaSet(llm_client=llm, embedder=embedder)
        >>> # 喂入不同版本的指南
        >>> criteria_lib.feed_text("2023指南规定糖尿病需空腹血糖>7.0。").feed_text("2024年指南补充了 HbA1c 作为主指标。")
        >>> criteria_lib.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any
    ):
        """
        初始化 DiagnosticCriteriaSet 模板。

        Args:
            llm_client: 用于提取的语言模型客户端。
            embedder: 用于语义检索和可视化的嵌入模型。
            chunk_size: 文本块大小。
            chunk_overlap: 文本块重叠大小。
            max_workers: 最大并行工作线程数。
            verbose: 是否开启详细日志。
            **kwargs: 其他传给 AutoSet 的参数。
        """
        super().__init__(
            item_schema=DiagnosticCriteria,
            key_extractor=lambda x: x.disease_name.strip().lower(), # 精确键值匹配疾病名
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """
        可视化诊断标准库。

        Args:
            top_k_for_search: 搜索时找回的相关条目数量。
            top_k_for_chat: 聊天时找回的相关条目数量。
        """
        def item_label_extractor(item: DiagnosticCriteria) -> str:
            return item.disease_name

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
