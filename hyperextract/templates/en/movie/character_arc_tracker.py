from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class CharacterState(BaseModel):
    """The state of a film character at a specific narrative point."""
    character_name: str = Field(description="Name of the character.")
    psychological_state: str = Field(description="The core emotional or psychological state of the character at this moment.")
    current_goal: str = Field(description="The primary objective of the character at this moment.")
    situation: str = Field(description="The external circumstances or conflicts the character is facing.")

class CharacterDevelopment(BaseModel):
    """Evolution and arc shifts between character states."""
    source: str = Field(description="Starting state.")
    target: str = Field(description="Resulting state.")
    time: str = Field(description="The point or phase in the plot where the shift occurs (e.g., 'Act II', 'Pre-climax').")
    trigger_event: str = Field(description="The key plot event that triggers this shift in state.")
    arc_direction: str = Field(description="Direction of the arc (e.g., Growth, Corruption, Awakening, Realization).")

# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a sophisticated script analyst and character study expert. Your task is to track the 'character arc' from scripts or deep film reviews.\n\n"
    "Extraction Guidelines:\n"
    "1. **State Slicing**: Extract nodes representing the character's psychology, goals, and situation at different stages of the story.\n"
    "2. **Trigger Identification**: Identify the key driving events that cause the transition between two character states.\n"
    "3. **Timeline Resolution**: Clearly specify when the shift occurs (e.g., script page numbers, acts, or relative story phases).\n"
)

_NODE_PROMPT = "Identify and extract the character's internal and external states at key plot points. Record their emotions, current goals, and primary situations."
_EDGE_PROMPT = "Analyze the evolution between character states. Point out what plot events triggered the psychological journey and summarize the direction of the arc."

# ==============================================================================
# 3. Template Class
# ==============================================================================

class CharacterArcTracker(AutoTemporalGraph[CharacterState, CharacterDevelopment]):
    """
    Applicable to: [Character Biographies, Dramatic Scripts, Literary Adaptations, Film Reviews]

    Template for analyzing film character growth paths and psychological arcs.

    This template focuses on 'why' and 'how' a character changes, ideal for deep character studies and dramatic conflict analysis.

    Example:
        >>> arc = CharacterArcTracker(llm_client=llm, embedder=embedder)
        >>> text = "At the start, Jack is a timid clerk. After the explosion, he realizes the value of life and shows incredible courage in the finale."
        >>> arc.feed_text(text).show()
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
            node_schema=CharacterState,
            edge_schema=CharacterDevelopment,
            node_key_extractor=lambda x: f"{x.character_name}-{x.psychological_state[:10]}",
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
        def n_label(node: CharacterState) -> str: return f"{node.character_name}: {node.psychological_state}"
        def e_label(edge: CharacterDevelopment) -> str: return f"[{edge.time}] {edge.arc_direction}"
        super().show(node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs)
