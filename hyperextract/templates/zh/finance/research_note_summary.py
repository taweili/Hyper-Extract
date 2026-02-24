"""研究报告摘要 - 从股票研究报告中提取核心投资论点。

提取分析师研究报告中的评级、目标价和顶层投资逻辑，
用于报告数据库填充和筛选。
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from ontomem.merger import MergeStrategy
from hyperextract.types import AutoModel

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class ResearchNoteSummarySchema(BaseModel):
    """
    股票研究报告的结构化摘要。
    """

    company_name: Optional[str] = Field(
        None, description="被覆盖公司的名称。"
    )
    ticker: Optional[str] = Field(
        None, description="股票代码（例如 'AAPL'、'NVDA'）。"
    )
    analyst_name: Optional[str] = Field(
        None, description="首席分析师的姓名。"
    )
    research_firm: Optional[str] = Field(
        None, description="研究机构名称（例如 '高盛'、'摩根士丹利'）。"
    )
    report_date: Optional[str] = Field(
        None, description="报告发布日期。"
    )
    rating: Optional[str] = Field(
        None,
        description="分析师评级：'买入'、'增持'、'持有'、'中性'、'卖出'、'减持'。",
    )
    prior_rating: Optional[str] = Field(
        None, description="如有变更，之前的评级。"
    )
    target_price: Optional[str] = Field(
        None, description="当前目标价（例如 '$150.00'）。"
    )
    prior_target_price: Optional[str] = Field(
        None, description="如有变更，之前的目标价。"
    )
    current_price: Optional[str] = Field(
        None, description="报告发布时的股价。"
    )
    investment_thesis: Optional[str] = Field(
        None,
        description="核心投资论点或评级的关键论据。",
    )
    key_catalysts: Optional[List[str]] = Field(
        None,
        description="已识别的近期催化剂（例如 ['Q4 业绩超预期', '新产品发布', '监管审批']）。",
    )
    key_risks: Optional[List[str]] = Field(
        None,
        description="分析师强调的主要风险。",
    )
    revenue_estimate: Optional[str] = Field(
        None, description="分析师对当前/下一财年的收入预测。"
    )
    eps_estimate: Optional[str] = Field(
        None, description="分析师对当前/下一财年的每股收益预测。"
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一名股票研究分析师。从本研究报告中提取核心投资论点、评级、目标价和关键论据。\n\n"
    "规则:\n"
    "- 提取分析师的评级及任何评级变更。\n"
    "- 捕获目标价以及变更前的目标价（如有变更）。\n"
    "- 简洁地总结核心投资论点。\n"
    "- 列出分析师识别的关键催化剂和风险。\n"
    "- 在提及时提取财务预测（收入、每股收益）。\n\n"
    "### 源文本:\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class ResearchNoteSummary(AutoModel[ResearchNoteSummarySchema]):
    """
    适用文档: 股票研究报告、分析师笔记、评级变更、首次覆盖报告、行业研究。

    模板用于从股票研究报告中提取核心投资论点和关键参数。每份报告生成一个结构化摘要，
    用于数据库填充和筛选。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> summary = ResearchNoteSummary(llm_client=llm, embedder=embedder)
        >>> report = "我们将 AAPL 评级上调为买入，目标价 200 美元..."
        >>> summary.feed_text(report)
        >>> print(summary.data)
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
        **kwargs: Any,
    ):
        """
        初始化研究报告摘要模板。

        Args:
            llm_client (BaseChatModel): 用于报告提取的 LLM。
            embedder (Embeddings): 用于索引的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoModel 的其他参数。
        """
        super().__init__(
            data_schema=ResearchNoteSummarySchema,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=MergeStrategy.LLM.BALANCED,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )
