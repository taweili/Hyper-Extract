from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from ontomem.merger import MergeStrategy
from hyperextract.types import AutoModel

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class EarningsCallSummarySchema(BaseModel):
    """
    财报电话会议的结构化摘要。
    """

    company_name: Optional[str] = Field(
        None, description="公司名称。"
    )
    ticker: Optional[str] = Field(
        None, description="股票代码。"
    )
    quarter: Optional[str] = Field(
        None, description="报告季度（例如'Q3 FY2024'、'2024 年第四季度'）。"
    )
    call_date: Optional[str] = Field(
        None, description="财报电话会议日期。"
    )
    reported_revenue: Optional[str] = Field(
        None, description="本季度报告收入（例如'948 亿美元'）。"
    )
    revenue_vs_consensus: Optional[str] = Field(
        None,
        description="收入与市场一致预期对比（例如'超出 12 亿美元'、'符合预期'、'低于预期 5 亿美元'）。",
    )
    reported_eps: Optional[str] = Field(
        None, description="报告的稀释每股收益（例如'1.46 美元'）。"
    )
    eps_vs_consensus: Optional[str] = Field(
        None, description="每股收益与一致预期对比（例如'超出 0.05 美元'）。"
    )
    guidance_revenue: Optional[str] = Field(
        None,
        description="前瞻性收入指引（例如'第四季度 950-970 亿美元'、'2025 财年收入 3800-3900 亿美元'）。",
    )
    guidance_eps: Optional[str] = Field(
        None, description="前瞻性每股收益指引（如有提供）。"
    )
    overall_tone: Optional[str] = Field(
        None,
        description="电话会议整体基调：'积极'、'审慎乐观'、'中性'、'谨慎'、'消极'。",
    )
    key_highlights: Optional[List[str]] = Field(
        None,
        description="管理层准备发言中的 3-5 项核心亮点。",
    )
    key_concerns: Optional[List[str]] = Field(
        None,
        description="管理层或分析师在问答环节提出的主要关切。",
    )
    strategic_priorities: Optional[List[str]] = Field(
        None,
        description="管理层强调的战略重点。",
    )
    ceo_name: Optional[str] = Field(
        None, description="CEO 或主要发言人姓名。"
    )
    cfo_name: Optional[str] = Field(
        None, description="CFO 姓名。"
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是买方分析师，正在审阅财报电话会议记录。"
    "提取关键财务指标、业绩指引和整体基调。\n\n"
    "规则:\n"
    "- 提取确切的报告数据（收入、每股收益）并与一致预期进行对比。\n"
    "- 捕捉收入和盈利的前瞻性指引。\n"
    "- 评估电话会议的整体基调（管理层措辞、分析师反应）。\n"
    "- 列出准备发言中的核心亮点和问答环节中的主要关切。\n"
    "- 识别管理层强调的战略重点。\n\n"
    "### 原文:\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class EarningsCallSummary(AutoModel[EarningsCallSummarySchema]):
    """
    适用文档: 季度财报电话会议记录、业绩新闻稿、
    投资者日活动记录、年度股东大会记录。

    模板用于从财报电话会议记录中提取结构化摘要。生成已报告指标、业绩指引、
    基调和核心主题的统一视图，便于季度复盘仪表板和一致预期跟踪。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> summary = EarningsCallSummary(llm_client=llm, embedder=embedder)
        >>> transcript = "下午好。第三季度收入为 948 亿美元，超出一致预期..."
        >>> summary.feed_text(transcript)
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
        初始化财报电话会议摘要模板。

        Args:
            llm_client (BaseChatModel): 用于会议记录提取的 LLM。
            embedder (Embeddings): 用于索引的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoModel 的其他参数。
        """
        super().__init__(
            data_schema=EarningsCallSummarySchema,
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
