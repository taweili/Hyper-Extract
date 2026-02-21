"""Call Sentiment Hypergraph - Models topic-sentiment analysis across earnings calls.

Models multi-dimensional sentiment: {Topic, Speaker, Sentiment, Driving Factor}
across the call for sentiment-driven trading signals and tone shift detection.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class CallTopic(BaseModel):
    """
    A topic, speaker, or sentiment driver discussed in an earnings call.
    """

    name: str = Field(
        description="Name of the topic element (e.g., 'Revenue Growth', 'CEO Tim Cook', 'AI Investment Cycle', 'Cautious')."
    )
    element_type: str = Field(
        description="Type: 'Topic', 'Speaker', 'Sentiment', 'Driving Factor'."
    )
    description: Optional[str] = Field(
        None, description="Context or explanation for this element."
    )


class SentimentCluster(BaseModel):
    """
    A multi-dimensional sentiment cluster connecting topic, speaker, sentiment, and driver.
    """

    cluster_name: str = Field(
        description="Descriptive name (e.g., 'CEO Positive on AI Revenue', 'CFO Cautious on Margins')."
    )
    participating_elements: List[str] = Field(
        description="Names of all elements in this sentiment cluster (topic + speaker + sentiment + driver)."
    )
    sentiment_polarity: str = Field(
        description="Overall sentiment: 'Bullish', 'Bearish', 'Neutral', 'Mixed'."
    )
    intensity: str = Field(
        description="Sentiment intensity: 'Strong', 'Moderate', 'Mild'."
    )
    evidence: Optional[str] = Field(
        None,
        description="Key quote or paraphrase supporting the sentiment assessment.",
    )
    shift_from_prior: Optional[str] = Field(
        None,
        description="Change from prior quarter's tone if notable (e.g., 'More cautious than Q2', 'Upgraded from neutral').",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a sentiment analysis specialist for earnings calls. Extract topics, speakers, "
    "sentiment signals, and their multi-dimensional relationships.\n\n"
    "Rules:\n"
    "- Identify key topics discussed (revenue, margins, guidance, strategy).\n"
    "- Identify speakers and their roles.\n"
    "- Assess sentiment polarity and intensity for each topic-speaker combination.\n"
    "- A hyperedge connects a Topic + Speaker + Sentiment + Driving Factor.\n"
    "- Note shifts from prior quarter's tone."
)

_NODE_PROMPT = (
    "You are a sentiment analysis specialist. Extract all topics, speakers, sentiments, "
    "and driving factors (Nodes) from the earnings call.\n\n"
    "Extraction Rules:\n"
    "- Identify financial topics discussed.\n"
    "- Identify speakers (analysts, management).\n"
    "- Identify sentiment labels and driving factors.\n"
    "- DO NOT create sentiment clusters at this stage."
)

_EDGE_PROMPT = (
    "You are a sentiment analysis specialist. Given the elements, create multi-dimensional "
    "sentiment clusters (Hyperedges).\n\n"
    "Extraction Rules:\n"
    "- Each cluster connects a Topic + Speaker + Sentiment + Driving Factor.\n"
    "- Assess overall polarity and intensity.\n"
    "- Capture supporting evidence.\n"
    "- Note tone shifts from prior quarters.\n"
    "- Only reference elements that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class CallSentimentHypergraph(AutoHypergraph[CallTopic, SentimentCluster]):
    """
    Applicable to: Earnings Call Transcripts, Investor Day Transcripts,
    Management Presentations, Conference Transcripts.

    Template for multi-dimensional sentiment analysis of earnings calls. Uses
    hyperedges to model {Topic, Speaker, Sentiment, Driving Factor} clusters,
    enabling sentiment-driven trading signals and tone shift detection.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> sentiment = CallSentimentHypergraph(llm_client=llm, embedder=embedder)
        >>> transcript = "CEO: We are very excited about AI revenue growth..."
        >>> sentiment.feed_text(transcript)
        >>> sentiment.show()
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
        Initialize the Call Sentiment Hypergraph template.

        Args:
            llm_client (BaseChatModel): The LLM for sentiment extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoHypergraph.
        """
        super().__init__(
            node_schema=CallTopic,
            edge_schema=SentimentCluster,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: x.cluster_name.strip().lower(),
            nodes_in_edge_extractor=lambda x: tuple(
                e.strip().lower() for e in x.participating_elements
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
        Visualize the call sentiment hypergraph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of elements to retrieve. Default 3.
            top_k_edges_for_search (int): Number of sentiment clusters to retrieve. Default 3.
            top_k_nodes_for_chat (int): Elements for chat context. Default 3.
            top_k_edges_for_chat (int): Clusters for chat context. Default 3.
        """

        def node_label_extractor(node: CallTopic) -> str:
            return f"{node.name} [{node.element_type}]"

        def edge_label_extractor(edge: SentimentCluster) -> str:
            return f"[{edge.sentiment_polarity}/{edge.intensity}] {edge.cluster_name}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
