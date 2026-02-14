from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definition
# ==============================================================================

class NewsEventNode(BaseModel):
    """Core milestone nodes in a topical news story."""
    event_summary: str = Field(description="Short title or summary of the event.")
    location: Optional[str] = Field(description="Specific geographic location of the event.")
    key_participants: List[str] = Field(description="List of core people or organizations involved.")

class NewsTimelineProgression(BaseModel):
    """The logic of event evolution over time."""
    source: str = Field(description="Summary of the preceding event.")
    target: str = Field(description="Summary of the subsequent event.")
    time: str = Field(description="Exact point in time. You MUST resolve relative expressions (e.g., 'two weeks later') into absolute dates based on the context.")
    evolution_type: str = Field(description="Nature of the development (e.g., Escalation, Turning Point, De-escalation, Chain Reaction).")
    description: str = Field(description="Detailed description of this specific stage of evolution.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a senior investigative journalist. Your task is to organize scattered news reports into a coherent narrative thread of development.\n\n"
    "Extraction Requirements:\n"
    "1. **Event Extraction**: Identify single, milestone events.\n"
    "2. **Temporal Alignment**: Resolve all temporal markers into absolute formats and place them on the edges (Progression).\n"
    "3. **Dynamic Links**: Emphasize how events are logically triggered by time and causality.\n"
)

_NODE_PROMPT = "Identify key milestone events in the reporting. Provide concise titles, locations, and core participants for each."
_EDGE_PROMPT = "Establish a chronological chain between milestone events. Resolve relative time based on the provided reference dates."

# ==============================================================================
# 3. Template Class
# ==============================================================================

class TopicTimeline(AutoTemporalGraph[NewsEventNode, NewsTimelineProgression]):
    """
    Applicable to: [Series Reports, Long-form Investigative Journalism, Dossiers, Historical Retrospectives]

    A template used to link disconnected news reports into a coherent topical evolution timeline.

    Focuses on the vertical development trajectory of an issue, suitable for tracking long-term social trends or policy changes.

    Example:
        >>> timeline = TopicTimeline(llm_client=llm, embedder=embedder)
        >>> text = "Bill proposed in 2023. Six months later, it passed after debate. Effective next month."
        >>> timeline.feed_text(text).show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        **kwargs: Any
    ):
        super().__init__(
            node_schema=NewsEventNode,
            edge_schema=NewsTimelineProgression,
            node_key_extractor=lambda x: x.event_summary.strip(),
            edge_key_extractor=lambda x: f"{x.source}>>{x.target}",
            time_in_edge_extractor=lambda x: x.time,
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            extraction_mode=extraction_mode,
            **kwargs
        )

    def show(self, **kwargs):
        def n_label(node: NewsEventNode) -> str: return node.event_summary
        def e_label(edge: NewsTimelineProgression) -> str: return f"[{edge.time}] {edge.evolution_type}"
        super().show(node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs)
