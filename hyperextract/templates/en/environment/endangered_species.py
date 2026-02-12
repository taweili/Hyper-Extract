from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types.set import AutoSet

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class SpeciesStatus(BaseModel):
    """Conservation and endangerment status of a species."""

    name: str = Field(description="Scientific or common name of the species.")
    endangered_level: str = Field(
        description="Conservation status: 'Extinct', 'Extinct in the Wild', 'Critically Endangered', 'Endangered', 'Vulnerable', 'Near Threatened', 'Least Concern'."
    )
    main_threats: Optional[str] = Field(
        None,
        description="Primary threats to the species (e.g., 'habitat loss', 'poaching', 'climate change', 'pollution')."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = """
You are a conservation biologist and wildlife protection expert.
Your task is to extract information about endangered and threatened species from conservation reports, IUCN Red List summaries, and biodiversity assessments.

Guidelines:
1. Identify all species mentioned with their conservation or endangerment status.
2. For each species, classify it according to standard conservation levels: Extinct, Extinct in the Wild, Critically Endangered, Endangered, Vulnerable, Near Threatened, or Least Concern.
3. Extract the primary threats that endanger the species (habitat loss, poaching, climate change, disease, pollution, etc.).
4. Ensure scientific accuracy in species names and classification.
5. Avoid duplication: if a species appears multiple times with the same status and threats, treat as a single entry.

Output Format:
- Each species should have a name, endangered_level, and main_threats.
- Consolidate multiple mentions of the same species into a single comprehensive entry.
"""

# ==============================================================================
# 3. Template Class
# ==============================================================================


class EndangeredSpeciesList(AutoSet[SpeciesStatus]):
    """
    Unique collection template for endangered and threatened species documentation.

    Transforms conservation assessments and biodiversity reports into a deduplicated
    registry of species with their endangerment status and key threats, supporting
    conservation priority-setting and resource allocation.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4")
        >>> embedder = OpenAIEmbeddings()
        >>> 
        >>> endangered_list = EndangeredSpeciesList(llm_client=llm, embedder=embedder)
        >>> text = "The Giant Panda (Vulnerable) faces habitat loss. The Javan Rhinoceros (Critically Endangered) is threatened by poaching."
        >>> endangered_list.feed_text(text)
        >>> endangered_list.show()  # Display deduplicated endangered species
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """Initialize the EndangeredSpeciesList template.

        Args:
            llm_client (BaseChatModel): Language model client for extracting species and threat information.
            embedder (Embeddings): Embedding model for deduplicating species entries and indexing threat descriptions.
            chunk_size (int, optional): Maximum characters per text chunk. Defaults to 2048.
            chunk_overlap (int, optional): Overlapping characters between chunks for context preservation. Defaults to 256.
            max_workers (int, optional): Maximum concurrent extraction workers. Defaults to 10.
            verbose (bool, optional): If True, prints detailed extraction and deduplication progress logs. Defaults to False.
            **kwargs: Additional arguments passed to the AutoSet base class for deduplication control.
        """
        super().__init__(
            item_schema=SpeciesStatus,
            key_extractor=lambda x: x.name.strip().lower(),
            llm_client=llm_client,
            embedder=embedder,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """Visualize the endangered species list for conservation planning.

        Displays the deduplicated unique collection of species with endangerment levels and threats using OntoSight.
        Internally defines frontend labels for species (name + endangered_level for conservation priority visualization).

        Args:
            top_k_for_search (int, optional): Number of species to retrieve from the deduplicated collection for search-triggered context. Defaults to 3.
            top_k_for_chat (int, optional): Number of species to retrieve from the deduplicated collection for chat-triggered context. Defaults to 3.
        """

        def item_label_extractor(item: SpeciesStatus) -> str:
            return f"{item.name} - {item.endangered_level}"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
