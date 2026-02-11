from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class ConstructionResource(BaseModel):
    """
    A specific asset, material, or labor category assigned to a construction project.
    """
    resource_name: str = Field(description="Name of the resource (e.g., 'Tower Crane TC-01', 'Fly Ash Concrete').")
    category: str = Field(description="Category: 'Heavy Machinery', 'Bulk Material', 'Skilled Labor', 'Fixed Equipment', 'Consumables'.")
    quantity: Optional[str] = Field(None, description="Current quantity or capacity on site.")
    supplier_or_team: Optional[str] = Field(None, description="The entity providing or managing this resource.")
    status: str = Field("Active", description="Current operational status: 'Active', 'Idle', 'Maintenance', 'Depleted'.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

CONSTRUCTION_RESOURCE_PROMPT = (
    "You are a Construction Logistics and Procurement Manager. Extract all project resources and assets.\n\n"
    "Rules:\n"
    "- Identify machinery, materials, and labor types.\n"
    "- Capture specific quantities and supplier names if mentioned.\n"
    "- Deduplicate similar items (e.g., 'Excavator A' and 'The primary excavator' should be merged if referring to the same unit)."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class ResourceRegistrySet(AutoSet[ConstructionResource]):
    """
    Template for managing a consolidated site asset and material registry.
    
    Uses AutoSet for automatic deduplication and merging of multi-chunk resource mentions.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> registry = ResourceRegistrySet(llm_client=llm, embedder=embedder)
        >>> registry.feed_text("We have two 50-ton cranes from Liebherr on site.")
        >>> registry.feed_text("The Liebherr cranes are currently being serviced.")
        >>> print(registry.items)  # Mentions will be merged into a single Tower Crane resource.
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
        """
        Initialize the Resource Registry Set template.

        Args:
            llm_client (BaseChatModel): The language model client used for resource extraction.
            embedder (Embeddings): The embedding model used for resource deduplication.
            chunk_size (int, optional): Maximum characters per text chunk. Defaults to 2048.
            chunk_overlap (int, optional): Overlap between chunks. Defaults to 256.
            max_workers (int, optional): Parallel processing workers. Defaults to 10.
            verbose (bool, optional): If True, enables progress logging. Defaults to False.
            **kwargs (Any): Additional parameters for the AutoSet base class.
        """
        super().__init__(
            item_schema=ConstructionResource,
            key_extractor=lambda x: x.resource_name.strip().lower(),
            llm_client=llm_client,
            embedder=embedder,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CONSTRUCTION_RESOURCE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """
        Visualize the collection using OntoSight.
    
        Args:
            top_k_for_search (int): Number of items to retrieve for search context. Default 3.
            top_k_for_chat (int): Number of items to retrieve for chat context. Default 3.
        """
        def item_label_extractor(item: ConstructionResource) -> str:
            info = f" ({ item.category })" if getattr(item, "category", None) else ""
            return f"{ item.resource_name }{info}"
    
        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
