from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class MarketDriver(BaseModel):
    """
    A macroeconomic or company-specific factor that influences market outlook.
    """

    name: str = Field(
        description="Name of the driver (e.g., 'AI Demand', 'Interest Rate Cut', 'Regulatory Clarity')."
    )
    driver_type: str = Field(
        description="Type: 'Macro', 'Industry', 'Company-Specific', 'Catalyst'."
    )
    description: Optional[str] = Field(
        None, description="Detailed explanation of why this driver matters."
    )


class MarketTarget(BaseModel):
    """
    A trading asset or financial metric that is influenced by market drivers.
    """

    ticker: str = Field(description="Ticker symbol (e.g., 'AAPL', 'AI Index').")
    asset_type: str = Field(
        description="Type: 'Equity', 'Index', 'Bond', 'Commodity', 'Currency'."
    )
    metric: Optional[str] = Field(
        None, description="Specific metric if applicable (e.g., 'EPS', 'P/E Ratio')."
    )


class AnalystInfluence(BaseModel):
    """
    Represents how a market driver influences an asset's outlook.
    """

    source: str = Field(description="The market driver name.")
    target: str = Field(description="The affected asset/metric ticker.")
    sentiment: str = Field(
        description="Sentiment direction: 'Positive', 'Negative', 'Neutral'."
    )
    strength: str = Field(
        description="Influence strength: 'Strong', 'Moderate', 'Weak'."
    )
    analyst_view: str = Field(
        description="Analyst recommendation or target adjustment (e.g., 'Upgrade to Buy', 'Raise PT to $150')."
    )
    time_horizon: Optional[str] = Field(
        None, description="Expected timeline (e.g., 'FY24', '6-12 months', 'Long-term')."
    )
    source_firm: Optional[str] = Field(
        None, description="Name of the research firm or analyst source."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an equity research analyst. Extract market drivers, target assets, and analyst sentiment "
    "from research reports and macroeconomic commentary.\n\n"
    "Rules:\n"
    "- Identify market drivers (catalysts, policy changes, sector trends).\n"
    "- Identify which assets (stocks, indices, bonds) are affected.\n"
    "- Extract the sentiment direction and analyst recommendations.\n"
    "- Capture time horizons and source attributions."
)

_NODE_PROMPT = (
    "You are an equity research analyst. Extract all market drivers and target assets (Nodes) from the text.\n\n"
    "Extraction Rules:\n"
    "- Identify macroeconomic factors, policy shifts, and catalyst events.\n"
    "- Identify tickers and specific financial metrics being discussed.\n"
    "- Classify each node by type (Macro, Company-Specific, etc.).\n"
    "- DO NOT establish how drivers influence assets at this stage."
)

_EDGE_PROMPT = (
    "You are an equity research analyst. Given the list of market drivers and target assets, extract "
    "the influence relationships (Edges).\n\n"
    "Extraction Rules:\n"
    "- Connect each driver to the specific assets it influences.\n"
    "- Extract analyst sentiment (upgrade/downgrade language, target price changes).\n"
    "- Classify sentiment direction and influence strength.\n"
    "- Document the firm/analyst source and expected time horizon.\n"
    "- Only create edges between nodes that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class MarketSentimentGraph(AutoGraph[MarketDriver, AnalystInfluence]):
    """
    Applicable to: Equity Research Reports, Macro Strategy Calls, Earnings Call Transcripts,
    Macroeconomic Commentary, Analyst Alerts and Updates.

    Template for extracting and mapping market drivers to their expected impact on 
    asset valuations and analyst recommendations. Enables tracking of investment thesis 
    evolution and consensus shifts.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> sentiment = MarketSentimentGraph(llm_client=llm, embedder=embedder)
        >>> report = "AI demand acceleration is a key driver. We upgrade Tech stocks to Overweight..."
        >>> sentiment.feed_text(report)
        >>> sentiment.show()
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
        Initialize the Market Sentiment Graph template.

        Args:
            llm_client (BaseChatModel): The LLM for driver and sentiment extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoGraph.
        """
        super().__init__(
            node_schema=MarketDriver,
            edge_schema=AnalystInfluence,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.sentiment})-->{x.target.strip()}"
            ),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ) -> None:
        """
        Visualize the market sentiment graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of drivers to retrieve. Default 3.
            top_k_edges_for_search (int): Number of influences to retrieve. Default 3.
            top_k_nodes_for_chat (int): Drivers for chat context. Default 3.
            top_k_edges_for_chat (int): Influences for chat context. Default 3.
        """

        def node_label_extractor(node: MarketDriver) -> str:
            return f"{node.name} ({node.driver_type})"

        def edge_label_extractor(edge: AnalystInfluence) -> str:
            return f"[{edge.sentiment}/{edge.strength}] {edge.analyst_view}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
