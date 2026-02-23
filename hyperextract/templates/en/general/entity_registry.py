"""Entity Registry - Deduplicate and summarize all unique entities appearing in the text.

Suitable for entity discovery, named entity recognition, etc.
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet


class RegistryEntry(BaseModel):
    """Registry entry"""
    name: str = Field(description="Entity name, consistent with original text")
    category: str = Field(description="Entity type: Person, Organization, Location, Product, Concept, Other")
    description: str = Field(description="Brief description", default="")


_PROMPT = """## Role and Task
You are a professional entity recognition expert. Please extract all unique entities from the text to form an entity registry.

## Extraction Rules
1. Extract all entities: Person, Organization, Location, Product, Concept, etc.
2. Assign a type to each entity: Person, Organization, Location, Product, Concept, Other
3. Keep entity names consistent with the original text
4. Add a brief description for each entity

### Constraints
- Deduplication: Only keep one record for the same entity
- Maintain objectivity and accuracy, do not add information not in the text
- Entity name case should be consistent with the original text

### Source text:
"""


class EntityRegistry(AutoSet[RegistryEntry]):
    """
    Applicable documents: Arbitrary text, web scraped content, news reports

    Function introduction:
    Deduplicate and summarize all unique entities (e.g., person names, organization names) appearing in the text to form an entity registry. Supports entity discovery and named entity recognition.

    Example:
        >>> template = EntityRegistry(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Galaxy Interstellar announces successful maiden flight of Shenzhou-50...")
        >>> print(list(template))
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize entity registry template.
        
        Args:
            llm_client: LLM client for knowledge extraction
            embedder: Embedding model for semantic search
            max_workers: Maximum number of worker threads, default: 10
            verbose: Whether to output detailed logs, default: False
            **kwargs: Other technical parameters, passed to base class
        """
        super().__init__(
            item_schema=RegistryEntry,
            key_extractor=lambda x: x.name,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        Display entity registry.
        
        Args:
            top_k_for_search: Number of items to return for semantic search, default: 3
            top_k_for_chat: Number of items to use for chat, default: 3
        """
        def itemLabelExtractor(item: RegistryEntry) -> str:
            return f"{item.name} ({item.category})"
        
        super().show(
            item_label_extractor=itemLabelExtractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
