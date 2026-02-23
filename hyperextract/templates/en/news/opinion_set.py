from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema Definition
# ==============================================================================

class OpinionStance(BaseModel):
    """The stance and viewpoint held by an entity on a specific topic."""
    entity: str = Field(description="The individual, organization, media outlet, or group expressing the view.")
    stance: str = Field(description="Core stance label (e.g., Support, Strong Opposition, Neutral, Questioning).")
    key_argument: str = Field(description="The central argument or demand supporting this stance.")
    evidence_provided: List[str] = Field(description="Supporting evidence, data, or facts provided by the entity.")
    potential_interest: Optional[str] = Field(description="Implicit interests or motivations behind this stance.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a multi-dimensional public opinion analyst. Your task is to identify and summarize the viewpoints and stances of different stakeholders from reports or commentaries.\n\n"
    "Extraction Requirements:\n"
    "1. **Entity Definition**: Clearly identify who is speaking.\n"
    "2. **Stance Deconstruction**: Don't just record what was said; interpret the core attitude (stance) through tone and context.\n"
    "3. **Argument Mapping**: Extract persuasive evidence from their statements.\n"
    "4. **Horizontal Consolidation**: If multiple texts mention the same stance from the same entity, accumulate the new evidence into the existing entry.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class OpinionSet(AutoSet[OpinionStance]):
    """
    Applicable to: [Public Opinion Analysis, Media Reviews, Debate Transcripts, Editorial Columns]

    A knowledge mining template for summarizing the distribution of viewpoints and evidence across different actors in news and discourse.

    Uses an AutoSet structure, accumulating knowledge based on the 'Entity + Stance' key, suitable for mapping complex debates.

    Example:
        >>> opinion_set = OpinionSet(llm_client=llm, embedder=embedder)
        >>> text = "Organization A opposed the project, citing wetland destruction. The government argued it creates jobs."
        >>> opinion_set.feed_text(text).show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs: Any
    ):
        super().__init__(
            schema=OpinionStance,
            # Use combination of Entity and Stance as the key to accumulate similar views
            key_extractor=lambda x: f"{x.entity.strip()}:{x.stance.strip()}",
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            **kwargs
        )

    def show(self, **kwargs):
        def label_func(item: OpinionStance) -> str:
            return f"[{item.stance}] {item.entity}: {item.key_argument}"
        super().show(item_label_extractor=label_func, **kwargs)
