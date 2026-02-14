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
    material: Optional[str] = Field(None, description="Primary material composition")
    excavation_year: Optional[str] = Field(
        None, description="Year the artifact was discovered"
    )
    excavation_location: Optional[str] = Field(
        None, description="Geographic location of excavation"
    )
    current_museum: Optional[str] = Field(
        None, description="Current museum or collection location"
    )
    dimensions: Optional[str] = Field(
        None, description="Size and weight specifications"
    )
    symbolic_meaning: Optional[str] = Field(
        None, description="Cultural or religious significance"
    )
    historical_period: Optional[str] = Field(
        None, description="Civilization or historical era"
    )


_PROMPT = """You are a professional archaeologist and museum curator.
Extract comprehensive artifact information from the text:
1. artifact_name: Official artifact name
2. material: Material composition
3. excavation_year: Discovery year
4. excavation_location: Excavation site
5. current_museum: Current location/museum
6. dimensions: Physical measurements
7. symbolic_meaning: Cultural significance
8. historical_period: Historical era/dynasty

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
            period = f" ({item.historical_period})" if item.historical_period else ""
            return f"{item.artifact_name}{period}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
