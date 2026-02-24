from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class PlotPoint(BaseModel):
    """A significant event or moment in the narrative flow."""

    name: str = Field(
        description="A short title for the plot point or event (e.g., 'The Departure', 'Unexpected Reunion')."
    )
    location: Optional[str] = Field(description="Where the event takes place.")
    characters_involved: List[str] = Field(
        default_factory=list,
        description="List of characters participating in this event.",
    )
    description: str = Field(
        description="Detailed description of the plot content, including key actions and shifts."
    )


class TimeProgression(BaseModel):
    """The temporal and logical connection between plot points."""

    source: str = Field(description="The name of the preceding plot point.")
    target: str = Field(description="The name of the subsequent plot point.")
    time: str = Field(
        description="The resolved timestamp or absolute date of the event. You MUST resolve relative time expressions (e.g., 'three days later', 'next morning') into absolute dates (e.g., '2024-05-12') or specific years based on context and observation time."
    )
    logic: str = Field(
        description="The logical relationship between events (e.g., Causality, Escalation, Sudden Twist)."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a narrative structure analyst. Your task is to reconstruct the temporal and logical blueprint of the story from the text.\n\n"
    "Extraction Requirements:\n"
    "1. **Event Identification**: Extract nodes with narrative significance, recording location and participants.\n"
    "2. **Timeline Construction**: Establish connections with temporal attributes. Pay close attention to time indicators and markers.\n"
    "3. **Logical Chains**: Beyond chronological order, identify the causal drivers between events.\n"
    "Note: Time must be extracted on the edge (Progression), not as a standalone node."
)

_NODE_PROMPT = "Identify and extract all key plot points. Name each point and provide its location and the characters involved."

_EDGE_PROMPT = "Establish connections between the plot points. Accurately resolve temporal cues mentioned in the text into absolute dates or years, and describe how these events are linked in narrative logic."

# ==============================================================================
# 3. Template Class
# ==============================================================================


class NarrativeTimeline(AutoTemporalGraph[PlotPoint, TimeProgression]):
    """
    Applicable to: [Chronicles, Epic Literature, Detective Novels, History Books]

    Knowledge pattern for reconstructing narrative timelines and plot progressions.

    Leveraging AutoTemporalGraph, this template embeds temporal information within relationships
    to visualize the 'Cause-Process-Effect' dynamic of a story.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> # Initialize template
        >>> timeline = NarrativeTimeline(llm_client=llm, embedder=embedder)
        >>> # Feed text with temporal shifts
        >>> text = "After the council, Frodo left the Shire. Months later, he reached the gates of Mordor."
        >>> timeline.feed_text(text)
        >>> timeline.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: Optional[str] = None,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize NarrativeTimeline template.

        Args:
            llm_client: The language model client.
            embedder: Embeddings model for deduplication and indexing.
            observation_time: Base date for resolving relative time expressions like 'today' or 'yesterday'.
            extraction_mode: Defaults to 'two_stage' for higher temporal resolution accuracy.
            chunk_size: Max characters per processing chunk.
            chunk_overlap: Overlap between chunks.
            max_workers: Number of parallel extraction workers.
            verbose: Enable detailed logging.
            **kwargs: Extra arguments for AutoTemporalGraph.
        """
        super().__init__(
            node_schema=PlotPoint,
            edge_schema=TimeProgression,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source}->{x.target}",
            time_in_edge_extractor=lambda x: x.time,
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            extraction_mode=extraction_mode,
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
        Visualize the narrative timeline.

        Args:
            top_k_nodes_for_search: Number of nodes to retrieve for search context.
            top_k_edges_for_search: Number of edges to retrieve for search context.
            top_k_nodes_for_chat: Number of nodes to retrieve for chat context.
            top_k_edges_for_chat: Number of edges to retrieve for chat context.
        """

        def node_label_extractor(node: PlotPoint) -> str:
            return node.name

        def edge_label_extractor(edge: TimeProgression) -> str:
            return f"[{edge.time}] {edge.logic}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
