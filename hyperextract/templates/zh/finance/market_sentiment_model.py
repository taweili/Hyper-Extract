"""市场情绪模型 - 从财经新闻中提取情绪快照。

从财经新闻中提取情绪极性（看涨/看跌/中性）、提及的实体和预期价格影响，
用于实时情绪数据流。
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


class MarketSentimentSnapshot(BaseModel):
    """
    从财经新闻或市场评论中提取的结构化情绪快照。
    """

    headline: Optional[str] = Field(
        None, description='新闻文章/评论的标题。'
    )
    source: Optional[str] = Field(
        None, description='出版物或来源（例如"彭博社"、"路透社"、"CNBC"）。'
    )
    publication_date: Optional[str] = Field(
        None, description='发布日期。'
    )
    overall_sentiment: Optional[str] = Field(
        None,
        description='整体情绪："看涨"、"看跌"、"中性"、"混合"。',
    )
    sentiment_confidence: Optional[str] = Field(
        None,
        description='情绪评估的置信度："高"、"中"、"低"。',
    )
    mentioned_tickers: Optional[List[str]] = Field(
        None,
        description="提及的股票代码（例如 ['AAPL', 'MSFT', 'GOOGL']）。",
    )
    mentioned_sectors: Optional[List[str]] = Field(
        None,
        description="涉及的行业板块（例如 ['科技', '金融', '能源']）。",
    )
    key_events: Optional[List[str]] = Field(
        None,
        description="驱动情绪的关键事件（例如 ['美联储利率决议', 'NVDA 财报超预期']）。",
    )
    expected_impact: Optional[str] = Field(
        None,
        description='预期的价格/市场影响（例如"科技股短期上行"、"板块轮动可能性大"）。',
    )
    time_horizon: Optional[str] = Field(
        None,
        description='隐含时间范围："盘中"、"短期"、"中期"、"长期"。',
    )
    contrarian_signals: Optional[List[str]] = Field(
        None,
        description='任何逆向或不同意见的观点。',
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是金融情绪分析师。从这篇财经新闻文章或市场评论中提取情绪快照。\n\n"
    "规则:\n"
    "- 判断整体情绪极性（看涨/看跌/中性/混合）。\n"
    "- 识别所有提及的股票代码和行业板块。\n"
    "- 提取驱动情绪的关键事件。\n"
    "- 评估预期市场影响和时间范围。\n"
    "- 记录任何逆向或不同意见的观点。\n\n"
    "### 源文本:\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class MarketSentimentModel(AutoModel[MarketSentimentSnapshot]):
    """
    适用文档: 财经新闻文章、市场评论、分析师博客、交易台笔记、市场总结、盘前简报。

    模板用于从财经新闻中提取结构化情绪快照。为每篇文章生成一个综合情绪视图，
    用于实时情绪数据流和交易信号生成。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> sentiment = MarketSentimentModel(llm_client=llm, embedder=embedder)
        >>> news = "科技股在 NVDA 公布创纪录财报后大幅上涨..."
        >>> sentiment.feed_text(news)
        >>> print(sentiment.data)
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
        初始化市场情绪模型模板。

        Args:
            llm_client (BaseChatModel): 用于情绪提取的 LLM。
            embedder (Embeddings): 用于索引的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoModel 的其他参数。
        """
        super().__init__(
            data_schema=MarketSentimentSnapshot,
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
