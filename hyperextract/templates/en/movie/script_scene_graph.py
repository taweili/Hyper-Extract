from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class Scene(BaseModel):
    """A scene node in a screenplay."""
    title: str = Field(description="Standard scene heading (e.g., 'INT. COFFEE SHOP - DAY').")
    location: str = Field(description="Specific location where the scene occurs.")
    time_of_day: str = Field(description="Time period (e.g., DAY, NIGHT, DUSK, DAWN).")
    description: str = Field(description="Brief summary of actions or the core event within the scene.")

class SceneTransition(BaseModel):
    """Transition and logical flow between scenes."""
    source: str = Field(description="Source scene title.")
    target: str = Field(description="Target scene title.")
    time: str = Field(description="Duration or time offset passed between scenes. You MUST resolve this into an absolute duration or precise timestamp/offset.")
    transition_type: str = Field(description="Type of transition (e.g., CUT TO, FADE IN, DISSOLVE).")
    logic: str = Field(description="Narrative logic (e.g., Continuous Action, Time Jump, Parallel Editing).")

# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an expert screenwriter and film director. Your task is to extract the scene flow and narrative logic from screenplays or storyboards.\n\n"
    "Extraction Guidelines:\n"
    "1. **Scene Identification**: Extract all independent scene nodes, recording the exact heading, location, and time of day.\n"
    "2. **Rhythm Analysis**: Identify transition methods and accurately parse the passage of time between scenes.\n"
    "3. **Narrative Logic**: Describe how scenes drive each other on a storytelling level.\n"
)

_NODE_PROMPT = "Extract all scenes from the script. Record the standard heading, location, time period, and a core plot summary for each."
_EDGE_PROMPT = "Establish transitions between identified scenes. Note the transition method, and accurately infer the time span and narrative logical relationship."

# ==============================================================================
# 3. Template Class
# ==============================================================================

class ScriptSceneGraph(AutoTemporalGraph[Scene, SceneTransition]):
    """
    Applicable to: [Movie Screenplays, Teleplays, Storyboards, Narrative Outlines]

    Template for extracting scene flow and editing rhythm from screenplays.

    This template focuses on presenting narrative tempo and scene shifts, 
    ideal for director-level script breakdown and visualization.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> script = ScriptSceneGraph(llm_client=llm, embedder=embedder)
        >>> text = "SCENE 1: INT. LAB - DAY. Scientist experimenting. CUT TO: SCENE 2: EXT. STREET - NIGHT. Three hours later, he's walking."
        >>> script.feed_text(text)
        >>> script.show()
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
            node_schema=Scene,
            edge_schema=SceneTransition,
            node_key_extractor=lambda x: x.title.strip(),
            edge_key_extractor=lambda x: f"{x.source}->{x.target}",
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
        def n_label(node: Scene) -> str: return node.title
        def e_label(edge: SceneTransition) -> str: return f"{edge.transition_type} ({edge.time})"
        super().show(node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs)
