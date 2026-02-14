from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class CulinaryDish(BaseModel):
    """
    A representative culinary dish with standardized characteristics.
    """

    name: str = Field(
        description="Standardized dish name (e.g., 'Kung Pao Chicken')."
    )
    origin: Optional[str] = Field(
        None, description="Cuisine type, geographic origin, and seasonal relevance."
    )
    ingredients: Optional[str] = Field(
        None, description="Core ingredients, proteins, and key spices."
    )
    profile: Optional[str] = Field(
        None,
        description="Flavor characteristics, texture notes, and cooking techniques."
    )
    description: Optional[str] = Field(
        None,
        description="General description including dietary info, serving suggestions, and history.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a culinary expert. Extract representative culinary dishes from text.\n\n"
    "Extraction Rules:\n"
    "- Standardize dish names.\n"
    "- **origin**: Combine cuisine, region, and seasonality.\n"
    "- **ingredients**: List main proteins and vegetables/spices.\n"
    "- **profile**: Describe flavor, texture, and method (e.g. 'Spicy, Stir-fried').\n"
    "- **description**: Capture dietary notes, serving context, and any cultural backstory.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class CulinaryDishSet(AutoSet[CulinaryDish]):
    """
    Applicable to: Restaurant Menus, Cookbooks, Food Encyclopedias.

    Template for building a standardized culinary foundation through **key-based information accumulation**.
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
        super().__init__(
            item_schema=CulinaryDish,
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
        def item_label_extractor(item: CulinaryDish) -> str:
            parts = [item.name]
            if item.origin:
                parts.append(f"({item.origin})")
            return " ".join(parts)

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
