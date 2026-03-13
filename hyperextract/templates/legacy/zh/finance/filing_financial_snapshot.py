"""财报财务快照 - 从 SEC 申报文件中提取关键财务数据。

从 10-K/10-Q 申报文件中提取利润表、资产负债表和现金流量表数据，
整合为单一结构化对象，用于基本面筛选和数据库填充。
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


class FilingFinancialSnapshotSchema(BaseModel):
    """
    从 SEC 申报文件中提取的关键财务数据结构化快照。
    """

    company_name: Optional[str] = Field(None, description="申报实体的法定名称。")
    ticker: Optional[str] = Field(None, description="股票代码（例如 'AAPL'、'MSFT'）。")
    filing_type: Optional[str] = Field(
        None, description="申报类型：'10-K'、'10-Q'、'8-K'、'20-F'。"
    )
    filing_period: Optional[str] = Field(
        None,
        description="涵盖的财务期间（例如 'FY2024'、'Q3 2024'）。",
    )
    revenue: Optional[str] = Field(
        None,
        description="总营收或净销售额（例如 '3943亿美元'）。",
    )
    net_income: Optional[str] = Field(None, description="净利润。")
    earnings_per_share: Optional[str] = Field(
        None, description="稀释每股收益（例如 '$6.13'）。"
    )
    total_assets: Optional[str] = Field(None, description="总资产。")
    total_liabilities: Optional[str] = Field(None, description="总负债。")
    shareholders_equity: Optional[str] = Field(None, description="股东权益。")
    operating_cash_flow: Optional[str] = Field(
        None, description="经营活动现金流。"
    )
    free_cash_flow: Optional[str] = Field(
        None, description="自由现金流。"
    )
    key_metrics: Optional[List[str]] = Field(
        None,
        description="其他关键财务指标列表（如毛利率、ROE、市盈率等）。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = """## 角色与任务
你是一位专业的财务分析师，请从 SEC 申报文件中提取关键财务数据。

## 提取规则
### 核心约束
1. 每个对象对应一个独立的实体，禁止合并
2. 实体名称与原文保持一致

### 领域特定规则
- 按报告原文提取精确的金额数据，保留单位（百万、十亿）
- 识别申报实体、股票代码、申报类型和财务期间
- 在可获取时同时提取最近期间和前期对比数据
- 捕获申报文件中明确列出的关键财务比率
- 使用表格中的精确数据；除非文件明确给出，否则不要计算衍生数值

## 源文本:
{source_text}
"""

# ==============================================================================
# 3. 模板类
# ==============================================================================


class FilingFinancialSnapshot(AutoModel[FilingFinancialSnapshotSchema]):
    """
    适用文档: SEC 10-K 年度报告、10-Q 季度报告、20-F 外国发行人年报、
    包含嵌入式财务报表的年度报告。

    模板用于从 SEC 申报文件中提取合并财务数据快照。
    将利润表、资产负债表和现金流量表中的财务数据跨多个章节合并为单一结构化对象。

    使用示例:
        >>> snapshot = FilingFinancialSnapshot(llm_client=llm, embedder=embedder)
        >>> filing_text = "第8项 财务报表：营收为3943亿美元..."
        >>> snapshot.feed_text(filing_text)
        >>> print(snapshot.data)
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
        初始化财报财务快照模板。

        Args:
            llm_client (BaseChatModel): 用于财务数据提取的 LLM。
            embedder (Embeddings): 用于索引的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoModel 的其他参数。
        """
        super().__init__(
            data_schema=FilingFinancialSnapshotSchema,
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

    def show(
        self,
        *,
        top_k: int = 3,
    ):
        """
        展示财务快照。

        Args:
            top_k (int): 展示的快照数量。
        """

        def label_extractor(data: FilingFinancialSnapshotSchema) -> str:
            return f"{data.company_name or ''} ({data.ticker or ''}) - {data.filing_period or ''}"

        super().show(label_extractor=label_extractor, top_k=top_k)
