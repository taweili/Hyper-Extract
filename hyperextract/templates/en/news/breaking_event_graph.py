from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definition
# ==============================================================================

class NewsEntity(BaseModel):
    """Actors or objects involved in a breaking news event."""
    name: str = Field(description="Name of the person, organization, location, or country.")
    category: str = Field(description="Type (e.g., Politician, NGO, Media, Government Body).")
    attributes: List[str] = Field(description="Key descriptors or current status (e.g., 'Sanctioned', 'Reporting', 'Victim').")

class NewsAction(BaseModel):
    """Actions, statements, or events linking two news entities."""
    source: str = Field(description="The initiator of the action.")
    target: str = Field(description="The recipient or object of the action.")
    action_type: str = Field(description="Nature of the action (e.g., Condemnation, Signing Agreement, Direct Strike).")
    details: str = Field(description="Specific context or key information about the interaction.")
    evidence: List[str] = Field(description="Source quotes or specific facts supporting this action.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an expert geopolitical intelligence analyst. Your task is to extract the core structure of breaking events from news reports.\n\n"
    "Extraction Requirements:\n"
    "1. **Entity Identification**: Focus on main stakeholders (individuals, organizations, or nations).\n"
    "2. **Dynamic Interaction**: Capture the 'Who did What to Whom'.\n"
    "3. **Evidence Extraction**: Ensure specific actions are backed by verified statements or observable facts reported in the text.\n"
)

_NODE_PROMPT = "Identify all significant stakeholders in the breaking news. Categorize them and list their current roles or status mentioned."
_EDGE_PROMPT = "Connect the stakeholders through their interactions. Define the nature of these actions and provide supporting evidence from the text."

# ==============================================================================
# 3. Template Class
# ==============================================================================

class BreakingEventGraph(AutoGraph[NewsEntity, NewsAction]):
    """
    Applicable to: [Breaking News, Flash Reports, International Incidents, Press Releases]

    A template designed for rapid mapping of key actors and their interactions in urgent news scenarios.

    It excels at clarifying complex multilateral relationships during sudden events or crises.

    Example:
        >>> graph = BreakingEventGraph(llm_client=llm, embedder=embedder)
        >>> text = "Country A imposed sanctions on Entity B, while Organization C called for a ceasefire."
        >>> graph.feed_text(text).show()
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
            node_schema=NewsEntity,
            edge_schema=NewsAction,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source}->{x.action_type}->{x.target}",
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
        def n_label(node: NewsEntity) -> str: return f"{node.name} ({node.category})"
        def e_label(edge: NewsAction) -> str: return f"{edge.action_type}"
        super().show(node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs)
