"""Market Sentiment Model - Extracts sentiment snapshots from financial news.

Extracts sentiment polarity (Bullish/Bearish/Neutral), mentioned entities,
and expected price impact from financial news for real-time sentiment feeds.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from ontomem.merger import MergeStrategy
from hyperextract.types import AutoModel

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class MarketSentimentSnapshot(BaseModel):
    """
    A structured sentiment snapshot from financial news or market commentary.
    """

    headline: Optional[str] = Field(
        None, description="Headline or title of the news article/commentary."
    )
    source: Optional[str] = Field(
        None, description="Publication or source (e.g., 'Bloomberg', 'Reuters', 'CNBC')."
    )
    publication_date: Optional[str] = Field(
        None, description="Date of publication."
    )
    overall_sentiment: Optional[str] = Field(
        None,
        description="Overall sentiment: 'Bullish', 'Bearish', 'Neutral', 'Mixed'.",
    )
    sentiment_confidence: Optional[str] = Field(
        None,
        description="Confidence in sentiment assessment: 'High', 'Medium', 'Low'.",
    )
    mentioned_tickers: Optional[List[str]] = Field(
        None,
        description="Stock tickers mentioned (e.g., ['AAPL', 'MSFT', 'GOOGL']).",
    )
    mentioned_sectors: Optional[List[str]] = Field(
        None,
        description="Sectors referenced (e.g., ['Technology', 'Financials', 'Energy']).",
    )
    key_events: Optional[List[str]] = Field(
        None,
        description="Key events driving sentiment (e.g., ['Fed rate decision', 'NVDA earnings beat']).",
    )
    expected_impact: Optional[str] = Field(
        None,
        description="Expected price/market impact (e.g., 'Near-term upside for tech', 'Sector rotation likely').",
    )
    time_horizon: Optional[str] = Field(
        None,
        description="Implied time horizon: 'Intraday', 'Short-term', 'Medium-term', 'Long-term'.",
    )
    contrarian_signals: Optional[List[str]] = Field(
        None,
        description="Any contrarian or dissenting views noted.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a financial sentiment analyst. Extract the sentiment snapshot from this financial "
    "news article or market commentary.\n\n"
    "Rules:\n"
    "- Determine the overall sentiment polarity (Bullish/Bearish/Neutral/Mixed).\n"
    "- Identify all mentioned tickers and sectors.\n"
    "- Extract key events driving the sentiment.\n"
    "- Assess expected market impact and time horizon.\n"
    "- Note any contrarian or dissenting views.\n\n"
    "### Source Text:\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class MarketSentimentModel(AutoModel[MarketSentimentSnapshot]):
    """
    Applicable to: Financial News Articles, Market Commentary, Analyst Blogs,
    Trading Desk Notes, Market Wrap-ups, Pre-market Briefings.

    Template for extracting a structured sentiment snapshot from financial news.
    Produces a single consolidated sentiment view per article for real-time
    sentiment feeds and trading signal generation.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> sentiment = MarketSentimentModel(llm_client=llm, embedder=embedder)
        >>> news = "Tech stocks rallied sharply after NVDA reported record earnings..."
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
        Initialize the Market Sentiment Model template.

        Args:
            llm_client (BaseChatModel): The LLM for sentiment extraction.
            embedder (Embeddings): Embedding model for indexing.
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoModel.
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
