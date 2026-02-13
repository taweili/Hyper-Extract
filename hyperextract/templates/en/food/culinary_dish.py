from typing import Optional, List, Any
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
        description="Standardized dish name (e.g., 'Kung Pao Chicken', 'Mapo Tofu', 'Risotto')."
    )
    cuisine: str = Field(
        description="Cuisine origin (e.g., 'Sichuan', 'Italian', 'French', 'Indian', 'Thai')."
    )
    region: Optional[str] = Field(
        None, description="Specific geographic region or city of origin if applicable."
    )
    primary_ingredients: List[str] = Field(
        default_factory=list, description="Core ingredients defining the dish (e.g., ['Chicken', 'Peanuts', 'Dried Chilies'])."
    )
    protein_type: Optional[str] = Field(
        None,
        description="Main protein: 'Chicken', 'Beef', 'Pork', 'Seafood', 'Plant-based', 'No protein'.",
    )
    flavor_profile: str = Field(
        description="Predominant taste characteristics (e.g., 'Spicy & Numbing', 'Sweet & Sour', 'Umami-rich')."
    )
    cooking_method: Optional[str] = Field(
        None, description="Primary cooking technique (e.g., 'Stir-fry', 'Braised', 'Steamed', 'Grilled')."
    )
    dietary_attributes: List[str] = Field(
        default_factory=list,
        description="Dietary tags (e.g., 'Contains Nuts', 'Gluten-Free', 'Vegetarian', 'Dairy-Free').",
    )
    serving_suggestion: Optional[str] = Field(
        None, description="Typical serving context (e.g., 'Appetizer', 'Main course', 'Side dish')."
    )
    seasonal_note: Optional[str] = Field(
        None, description="Seasonal availability or association (e.g., 'Summer dish', 'Winter comfort food')."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a culinary expert and food historian. Your task is to extract and standardize "
    "representative culinary dishes from menus, cookbooks, recipe collections, and food reviews.\n\n"
    "Extraction Rules:\n"
    "- Standardize dish names to their most recognized form (e.g., 'Kung Pao Chicken' vs. 'Gong Bao Ji Ding').\n"
    "- Identify the cuisine origin and specific geographic region.\n"
    "- Extract core ingredients that define the dish.\n"
    "- Capture the predominant flavor profile using precise descriptors.\n"
    "- Note dietary attributes and allergenic ingredients.\n"
    "- Deduplicate: If the same dish appears with slight variations, merge into one entry.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class CulinaryDishSet(AutoSet[CulinaryDish]):
    """
    Applicable to: Restaurant Menus, Cookbooks, Food Encyclopedias, Recipe Websites,
    Food Blogs, Culinary Magazine Articles, Restaurant Review Databases, Dining Guides.

    Template for building a deduplicated collection of canonical culinary dishes. 
    Standardizes dish names across cultural and linguistic variations, capturing their 
    defining characteristics. Useful for culinary reference systems, recipe discovery, 
    and food journalism.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> dishes = CulinaryDishSet(llm_client=llm, embedder=embedder)
        >>> menu_text = "Our menu features Gong Bao Chicken, Kung Pao Chicken, and authentic Sichuan peanut chicken..."
        >>> dishes.feed_text(menu_text)
        >>> dishes.show()  # Automatically accumulates information for identical dish keys (e.g. 'Kung Pao Chicken')
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
        Initialize the Culinary Dish Set template.

        Args:
            llm_client (BaseChatModel): The LLM for dish extraction and standardization.
            embedder (Embeddings): Embedding model for retrieval and visualization.
            chunk_size (int): Size of text chunks for processing.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional parameters for AutoSet.
        """
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
        """
        Display the culinary dish collection using OntoSight.

        Args:
            top_k_for_search (int): Number of dishes to retrieve for search context. Default 3.
            top_k_for_chat (int): Number of dishes to retrieve for chat context. Default 3.
        """

        def item_label_extractor(dish: CulinaryDish) -> str:
            return f"{dish.name} ({dish.cuisine})"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
