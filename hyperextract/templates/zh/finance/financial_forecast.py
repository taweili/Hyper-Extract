"""财务预测 - 从股票研究报告中提取预测财务数据。

提取分析师报告中的收入、每股收益、市盈率等未来期间的财务预测，
用于一致性预期分析和财务建模。
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class ForecastItem(BaseModel):
    """
    特定指标和期间的单项财务预测。
    """

    metric: str = Field(
        description="被预测的财务指标（例如 '收入'、'每股收益'、'EBITDA'、'营业利润率'、'自由现金流'）。"
    )
    period: str = Field(
        description="预测期间（例如 'FY2025E'、'Q1 2025E'、'CY2026E'）。"
    )
    estimate: str = Field(
        description="预测值（例如 '$120.5B'、'$6.25'、'35.2%'）。"
    )
    prior_estimate: Optional[str] = Field(
        None, description="如有修订，之前的预测值（例如 '$115.0B'）。"
    )
    consensus: Optional[str] = Field(
        None, description="用于对比的市场一致性预期（例如 '$118.2B'）。"
    )
    growth_rate: Optional[str] = Field(
        None,
        description="隐含增长率（例如 '同比+15%'、'持平'）。",
    )
    assumptions: Optional[str] = Field(
        None,
        description="预测所依据的关键假设（例如 '假设销量增加 500 万台'）。",
    )
    source_firm: Optional[str] = Field(
        None, description="提供该预测的研究机构。"
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一名构建盈利模型的金融分析师。从本股票研究报告中提取所有财务预测和估算。\n\n"
    "规则:\n"
    "- 提取每个预测指标及其对应的具体时间段。\n"
    "- 在注明修订时，同时捕获当前和之前的预测值。\n"
    "- 在进行对比时提取一致性预期。\n"
    "- 捕获增长率和关键假设。\n"
    "- 将每项预测作为独立条目单独提取。\n\n"
    "### 源文本:\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class FinancialForecast(AutoList[ForecastItem]):
    """
    适用文档: 股票研究报告、盈利预测、财务模型、一致性预期报告、分析师预测。

    模板用于从分析师报告中提取预测财务数据。每项预测作为独立列表项捕获，
    支持一致性预期分析、预测修订跟踪和财务模型构建。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> forecast = FinancialForecast(llm_client=llm, embedder=embedder)
        >>> report = "我们将 FY2025 收入预测上调至 1205 亿美元（此前为 1150 亿美元）..."
        >>> forecast.feed_text(report)
        >>> forecast.show()
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
        初始化财务预测模板。

        Args:
            llm_client (BaseChatModel): 用于预测提取的 LLM。
            embedder (Embeddings): 用于索引的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoList 的其他参数。
        """
        super().__init__(
            item_schema=ForecastItem,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """
        可视化财务预测列表。

        Args:
            top_k_for_search (int): 检索的条目数。默认 3。
            top_k_for_chat (int): 对话上下文中的条目数。默认 3。
        """

        def label_extractor(item: ForecastItem) -> str:
            return f"{item.metric} ({item.period}): {item.estimate}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
