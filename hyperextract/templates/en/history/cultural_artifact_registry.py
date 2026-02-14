"""Cultural Artifact Registry - Extracts artifact information from historical sources.

Builds a unified artifact knowledge base by merging data from museum catalogs,
archaeological reports, and artifact descriptions.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet


class ArtifactSchema(BaseModel):
    artifact_name: str = Field(..., description="Official name of the artifact")
    period: Optional[str] = Field(None, description="Historical era, dynasty, or date")
    location: Optional[str] = Field(None, description="Excavation site and current museum location")
    physical_traits: Optional[str] = Field(None, description="Material, dimensions, and craftsmanship")
    significance: Optional[str] = Field(None, description="Cultural meaning, usage, and historical value")


_PROMPT = """You are an archaeologist. Extract artifact information from text.

Field Guide:
1. **artifact_name**: Name of the artifact
2. **period**: Historical era
3. **location**: Combine excavation site and current location
4. **physical_traits**: Describe material, size, and craft
5. **significance**: Explain functionality and cultural meaning

Extract only explicitly mentioned information.

### Source Text:
"""


class CulturalArtifactRegistry(AutoSet[ArtifactSchema]):
    """Applicable to: Museum catalogs, Archaeological reports, Artifact documentation

    Extracts comprehensive artifact encyclopedia by automatically merging information
    from multiple historical sources.
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        super().__init__(
            item_schema=ArtifactSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.artifact_name.strip().lower(),
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(self, *, top_k_for_search: int = 3, top_k_for_chat: int = 3) -> None:
        def label_extractor(item: ArtifactSchema) -> str:
            period = f" ({item.period})" if item.period else ""
            return f"{item.artifact_name}{period}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
