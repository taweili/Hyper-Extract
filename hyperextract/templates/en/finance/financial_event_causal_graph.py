"""Financial Event Causal Graph - Maps financial events to market reactions.

Maps financial events to affected entities and downstream market reactions
(e.g., "Fed rate hike -> Bank sector rally -> Bond yield rise") for event-driven strategy.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class FinancialEventNode(BaseModel):
    """
    A financial event, market entity, or reaction in an event chain.
    """

    name: str = Field(
        description="Name of the event or entity (e.g., 'Fed Rate Hike', 'Bank Sector', 'USD Strengthening')."
    )
    node_type: str = Field(
        description="Type: 'Event', 'Entity', 'Market Reaction', 'Policy', 'Economic Indicator', 'Sector'."
    )
    description: Optional[str] = Field(
        None,
        description="Context or details about the event/entity.",
    )


class EventCausalEdge(BaseModel):
    """
    A causal link from a financial event to a market reaction.
    """

    source: str = Field(description="The cause event or entity name.")
    target: str = Field(description="The effect or downstream reaction name.")
    causal_mechanism: str = Field(
        description="How the source causes the target effect "
        "(e.g., 'higher rates reduce borrowing costs sensitivity')."
    )
    direction: str = Field(
        description="Impact direction: 'Positive', 'Negative', 'Ambiguous'."
    )
    magnitude: Optional[str] = Field(
        None,
        description="Stated or implied magnitude (e.g., 'S&P 500 rose 2%', '50bps impact').",
    )
    timing: Optional[str] = Field(
        None,
        description="Timing of the reaction: 'Immediate', 'Same-day', 'Multi-day', 'Lagged'.",
    )
    confidence: Optional[str] = Field(
        None,
        description="Confidence in causal link: 'Established', 'Likely', 'Speculative'.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a macro strategist and financial news analyst. Extract financial events, affected "
    "market entities, and the causal chains connecting them from this news or commentary.\n\n"
    "Rules:\n"
    "- Identify triggering events (policy decisions, earnings, economic data releases).\n"
    "- Identify affected entities (sectors, stocks, indices, commodities).\n"
    "- Map the causal chains from events to market reactions.\n"
    "- Capture the magnitude and timing of reactions.\n"
    "- Note the confidence level in each causal link."
)

_NODE_PROMPT = (
    "You are a macro strategist. Extract all financial events, entities, and market reactions (Nodes).\n\n"
    "Extraction Rules:\n"
    "- Identify triggering events and policy decisions.\n"
    "- Identify market sectors, indices, and commodities.\n"
    "- Identify market reactions and price movements.\n"
    "- DO NOT establish causal relationships at this stage."
)

_EDGE_PROMPT = (
    "You are a macro strategist. Given the events and entities, extract causal chains (Edges).\n\n"
    "Extraction Rules:\n"
    "- Connect events to their downstream market effects.\n"
    "- Describe the causal mechanism at each link.\n"
    "- Note impact direction, magnitude, and timing.\n"
    "- Only create edges between nodes that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class FinancialEventCausalGraph(AutoGraph[FinancialEventNode, EventCausalEdge]):
    """
    Applicable to: Financial News Articles, Market Commentary, Macro Strategy Notes,
    Economic Data Releases, Central Bank Communications, Geopolitical News.

    Template for mapping financial events to their downstream market reactions.
    Enables event-driven strategy development and macro impact analysis by
    extracting causal chains from news and commentary.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> causal = FinancialEventCausalGraph(llm_client=llm, embedder=embedder)
        >>> news = "The Fed raised rates by 25bps, sending bank stocks higher while tech sold off..."
        >>> causal.feed_text(news)
        >>> causal.show()
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
        Initialize the Financial Event Causal Graph template.

        Args:
            llm_client (BaseChatModel): The LLM for event-chain extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoGraph.
        """
        super().__init__(
            node_schema=FinancialEventNode,
            edge_schema=EventCausalEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}--({x.direction})-->{x.target.strip().lower()}"
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
        Visualize the financial event causal graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of events/entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of causal links to retrieve. Default 3.
            top_k_nodes_for_chat (int): Events/entities for chat context. Default 3.
            top_k_edges_for_chat (int): Causal links for chat context. Default 3.
        """

        def node_label_extractor(node: FinancialEventNode) -> str:
            return f"{node.name} ({node.node_type})"

        def edge_label_extractor(edge: EventCausalEdge) -> str:
            mag = f" [{edge.magnitude}]" if edge.magnitude else ""
            return f"[{edge.direction}]{mag} {edge.causal_mechanism[:50]}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
