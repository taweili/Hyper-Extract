from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema 定义
# ==============================================================================

class AcademicTerm(BaseModel):
    """
    从多个来源聚合的标准学术词条、概念或定义。
    """
    term: str = Field(
        description="学术词条/概念的主名称。作为唯一标识符。"
    )
    domain: str = Field(
        description="研究领域或学科（如：'热力学'、'语言学'）。"
    )
    definition: str = Field(
        description="综合多个来源后形成的权威、详细的定义描述。"
    )
    synonyms: List[str] = Field(
        default_factory=list,
        description="同义词或高度相关的别称列表。"
    )
    key_expression: Optional[str] = Field(
        None, description="与该词条相关的核心公式、符号或标志性表达。"
    )

# ==============================================================================
# 2. Prompts 提示词
# ==============================================================================

_PROMPT = (
    "你是一位学术百科全书编辑和词典编纂者。你的目标是提取并标准化学术定义。\n\n"
    "提取规则：\n"
    "- 识别唯一的学术术语及其高度精确的定义。\n"
    "- 寻找文本中出现的同义词、简称或别称。\n"
    "- 如果存在对同一术语的多个描述，优先选择数学上或逻辑上更严谨的描述，并尝试进行信息互补。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class AcademicLexiconSet(AutoSet[AcademicTerm]):
    """
    用于构建学术名词百科集的教育模板，通过**精确的术语键值进行信息累加**。
    自动将来自多个文本源的同一术语信息合并为一条完整条目，从各源中丰富定义内容。

    用法示例：
        >>> lexicon = AcademicLexiconSet(llm_client, embedder)
        >>> lexicon.feed_text("来源A：光合作用是植物利用太阳能进行的生化反应...")  # 提取：term='光合作用', definition=...
        >>> lexicon.feed_text("来源B：光合作用在叶绿体中进行，包含光反应和暗反应...")  # 自动合并到已有的'光合作用'条目中
        >>> lexicon.show()  # 显示合并后的学术术语集
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化学术名词百科模板。

        参数描述:
            llm_client (BaseChatModel): 用于提取的语言模型客户端。
            embedder (Embeddings): 用于语义检索和知识图谱可视化的嵌入模型。注意：信息累加基于术语名称（key），而非嵌入向量。
            extraction_mode (str): 提取模式策略。
            chunk_size (int): 文本分片大小。
            chunk_overlap (int): 分片重叠大小。
            max_workers (int): 并行处理进程数。
            verbose (bool): 是否开启详细日志。
            **kwargs: 透传给 AutoSet 基类的其他参数。
        """
        super().__init__(
            item_schema=AcademicTerm,
            key_extractor=lambda x: x.term.strip().lower(),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
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
    ) -> None:
        """
        Visualize the collection using OntoSight.
    
        Args:
            top_k_for_search (int): Number of items to retrieve for search context. Default 3.
            top_k_for_chat (int): Number of items to retrieve for chat context. Default 3.
        """
        def item_label_extractor(item: AcademicTerm) -> str:
            return f"{item.term}"
    
        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
