"""Market Narrative Timeline - Tracks how market narratives evolve over time.

Tracks how market narratives and dominant themes evolve over time (e.g., shift
from "inflation fear" to "soft landing hope") for thematic investing and regime detection.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class NarrativeEntity(BaseModel):
    """
    A market narrative, theme, or market entity involved in narrative evolution.
    """

    name: str = Field(
        description="Name of the narrative or entity (e.g., 'Inflation Fear', 'Soft Landing Hope', 'S&P 500', 'Fed Policy')."
    )
    entity_type: str = Field(
        description="Type: 'Narrative', 'Theme', 'Market Index', 'Asset Class', 'Policy Regime', 'Economic Phase'."
    )
    description: Optional[str] = Field(
        None,
        description="Explanation of the narrative or theme.",
    )


class NarrativeShiftEdge(BaseModel):
    """
    A narrative shift or evolution event with temporal context.
    """

    source: str = Field(description="The prior narrative or triggering entity name.")
    target: str = Field(description="The emerging narrative or affected entity name.")
    shift_type: str = Field(
        description="Type: 'Replaced By', 'Evolved Into', 'Triggered', 'Dominated By', "
        "'Coexists With', 'Undermined By'."
    )
    start_timestamp: Optional[str] = Field(
        None,
        description="When the shift began (e.g., '2024-03', 'March 2024', 'Q1 2024').",
    )
    end_timestamp: Optional[str] = Field(
        None,
        description="When the shift completed or the new narrative became dominant.",
    )
    catalyst: Optional[str] = Field(
        None,
        description="Event or data point that triggered the shift (e.g., 'CPI print of 2.4%').",
    )
    market_impact: Optional[str] = Field(
        None,
        description="How the narrative shift affected markets (e.g., 'rotation from value to growth').",
    )
    description: Optional[str] = Field(
        None,
        description="Detailed explanation of the narrative transition.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a thematic investing strategist. Extract market narratives, dominant themes, "
    "and how they evolve over time from this financial commentary.\n\n"
    "Rules:\n"
    "- Identify dominant market narratives and themes (e.g., 'inflation fear', 'AI boom').\n"
    "- Track how narratives shift, replace, or evolve into new ones.\n"
    "- Extract specific dates or periods when shifts occurred.\n"
    "- Capture the catalysts triggering narrative changes.\n"
    "- Note market impact of narrative shifts."
)

_NODE_PROMPT = (
    "You are a thematic investing strategist. Extract all narratives, themes, and market entities (Nodes).\n\n"
    "Extraction Rules:\n"
    "- Identify dominant narratives and investment themes.\n"
    "- Identify market indices, asset classes, and policy regimes.\n"
    "- DO NOT extract narrative shifts at this stage."
)

_EDGE_PROMPT = (
    "You are a thematic investing strategist. Given the narratives and entities, extract "
    "narrative shifts and evolution events (Edges) with dates.\n\n"
    "Extraction Rules:\n"
    "- Connect narratives through their evolution (replaced by, evolved into, etc.).\n"
    "- Extract specific dates or periods.\n"
    "- Capture catalysts and market impact.\n"
    "- Only create edges between nodes that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class MarketNarrativeTimeline(
    AutoTemporalGraph[NarrativeEntity, NarrativeShiftEdge]
):
    """
    Applicable to: Market Commentary, Macro Strategy Notes, Financial News Archives,
    Investment Outlook Reports, Quarterly Market Reviews.

    Template for tracking how market narratives and dominant themes evolve over time.
    Enables thematic investing, regime detection, and narrative momentum analysis.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> narrative = MarketNarrativeTimeline(llm_client=llm, embedder=embedder)
        >>> commentary = "Markets shifted from inflation fear to soft landing hope in Q2 2024..."
        >>> narrative.feed_text(commentary)
        >>> narrative.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: str = "2024-01-01",
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize the Market Narrative Timeline template.

        Args:
            llm_client (BaseChatModel): The LLM for narrative extraction.
            embedder (Embeddings): Embedding model for deduplication.
            observation_time (str): Reference time for resolving relative dates.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoTemporalGraph.
        """
        super().__init__(
            node_schema=NarrativeEntity,
            edge_schema=NarrativeShiftEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}|{x.shift_type.lower()}|{x.target.strip().lower()}"
            ),
            time_in_edge_extractor=lambda x: x.start_timestamp or "",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
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
        Visualize the market narrative timeline using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of narratives to retrieve. Default 3.
            top_k_edges_for_search (int): Number of shifts to retrieve. Default 3.
            top_k_nodes_for_chat (int): Narratives for chat context. Default 3.
            top_k_edges_for_chat (int): Shifts for chat context. Default 3.
        """

        def node_label_extractor(node: NarrativeEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: NarrativeShiftEdge) -> str:
            date = f" [{edge.start_timestamp}]" if edge.start_timestamp else ""
            return f"{edge.shift_type}{date}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
