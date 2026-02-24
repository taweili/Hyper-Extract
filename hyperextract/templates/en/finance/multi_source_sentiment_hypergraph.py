"""Multi-Source Sentiment Hypergraph - Integrates sentiment signals from multiple sources.

Integrates sentiment signals from multiple sources: {News Article, Social Media Post,
Analyst Note} -> Aggregated Sentiment -> Affected Entity for ensemble scoring.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class SentimentSource(BaseModel):
    """
    A source of sentiment signal or an affected market entity.
    """

    name: str = Field(
        description="Name of the source or entity (e.g., 'Bloomberg Article', 'Analyst Note from GS', 'AAPL', 'Tech Sector')."
    )
    source_type: str = Field(
        description="Type: 'News Article', 'Analyst Note', 'Social Media', 'Market Data', 'Company Filing', "
        "'Affected Entity', 'Sector', 'Index'."
    )
    sentiment_signal: Optional[str] = Field(
        None,
        description="Individual sentiment from this source: 'Bullish', 'Bearish', 'Neutral'.",
    )
    credibility: Optional[str] = Field(
        None,
        description="Source credibility assessment: 'Tier 1', 'Tier 2', 'Unverified'.",
    )


class AggregatedSentiment(BaseModel):
    """
    An aggregated sentiment signal fusing multiple sources for an affected entity.
    """

    fusion_name: str = Field(
        description="Descriptive name (e.g., 'AAPL Bullish Consensus from 3 Sources')."
    )
    participating_sources: List[str] = Field(
        description="Names of all sources and affected entities in this fusion."
    )
    aggregated_polarity: str = Field(
        description="Fused sentiment: 'Strong Bullish', 'Bullish', 'Neutral', 'Bearish', 'Strong Bearish', 'Conflicting'."
    )
    agreement_level: str = Field(
        description="Source agreement: 'Unanimous', 'Majority', 'Split', 'Contradictory'."
    )
    affected_entity: Optional[str] = Field(
        None,
        description="Primary entity the sentiment applies to (ticker or sector).",
    )
    signal_strength: Optional[str] = Field(
        None,
        description="Overall signal strength for trading: 'Actionable', 'Informational', 'Noise'.",
    )
    conflicting_views: Optional[str] = Field(
        None,
        description="Summary of any dissenting or conflicting sentiment signals.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a multi-source sentiment fusion analyst. Extract sentiment signals from different "
    "sources and create aggregated sentiment views.\n\n"
    "Rules:\n"
    "- Identify each distinct source of sentiment (news, analyst notes, social media).\n"
    "- Extract the individual sentiment signal from each source.\n"
    "- Create aggregated sentiment hyperedges connecting sources to affected entities.\n"
    "- Assess agreement level across sources.\n"
    "- Note conflicting views and signal strength."
)

_NODE_PROMPT = (
    "You are a sentiment fusion analyst. Extract all sentiment sources and affected entities (Nodes).\n\n"
    "Extraction Rules:\n"
    "- Identify news articles, analyst notes, and social media posts.\n"
    "- Identify affected entities (tickers, sectors, indices).\n"
    "- Capture individual sentiment from each source.\n"
    "- DO NOT create aggregated views at this stage."
)

_EDGE_PROMPT = (
    "You are a sentiment fusion analyst. Given the sources and entities, create aggregated "
    "sentiment fusions (Hyperedges).\n\n"
    "Extraction Rules:\n"
    "- Each hyperedge connects multiple sources to an affected entity.\n"
    "- Assess the aggregated sentiment polarity and agreement level.\n"
    "- Evaluate signal strength for trading purposes.\n"
    "- Note any conflicting views.\n"
    "- Only reference elements that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class MultiSourceSentimentHypergraph(
    AutoHypergraph[SentimentSource, AggregatedSentiment]
):
    """
    Applicable to: Financial News feeds, Analyst Report collections,
    Social Media streams, Multi-source Market Intelligence.

    Template for integrating sentiment signals from multiple sources. Uses
    hyperedges to connect multiple sources to aggregated sentiment views,
    enabling ensemble sentiment scoring and fake signal filtering.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> fusion = MultiSourceSentimentHypergraph(llm_client=llm, embedder=embedder)
        >>> text = "Bloomberg reports tech rally. Meanwhile, GS upgrades AAPL. Twitter sentiment bullish."
        >>> fusion.feed_text(text)
        >>> fusion.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize the Multi-Source Sentiment Hypergraph template.

        Args:
            llm_client (BaseChatModel): The LLM for sentiment fusion.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoHypergraph.
        """
        super().__init__(
            node_schema=SentimentSource,
            edge_schema=AggregatedSentiment,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: x.fusion_name.strip().lower(),
            nodes_in_edge_extractor=lambda x: tuple(
                s.strip().lower() for s in x.participating_sources
            ),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
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
        Visualize the multi-source sentiment hypergraph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of sources to retrieve. Default 3.
            top_k_edges_for_search (int): Number of fusions to retrieve. Default 3.
            top_k_nodes_for_chat (int): Sources for chat context. Default 3.
            top_k_edges_for_chat (int): Fusions for chat context. Default 3.
        """

        def node_label_extractor(node: SentimentSource) -> str:
            signal = f" [{node.sentiment_signal}]" if node.sentiment_signal else ""
            return f"{node.name} ({node.source_type}){signal}"

        def edge_label_extractor(edge: AggregatedSentiment) -> str:
            return f"[{edge.aggregated_polarity}] {edge.fusion_name}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
