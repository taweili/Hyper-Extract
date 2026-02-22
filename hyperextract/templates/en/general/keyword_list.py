"""Keyword List - Extract keywords from text with category and description information.

Suitable for content tag generation, topic analysis, etc.
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class Keyword(BaseModel):
    """Keyword entry"""
    term: str = Field(description="Keyword")
    category: str = Field(description="Category: CoreConcept, Term, PersonName, OrganizationName, Other")
    description: str = Field(description="Brief description or context explanation of the keyword", default="")


_PROMPT = """You are a professional keyword extraction expert. Please extract all keywords from the text with category and description information.

### Extraction Rules
1. Extract all keywords and core phrases from the text
2. Assign a category to each keyword: CoreConcept, Term, PersonName, OrganizationName, Other
3. Add a brief description for each keyword, explaining its meaning or context in the text

### Constraints
- Ensure keyword accuracy, do not add information not in the text
- Keep keyword case consistent with the original text

### Source text:
"""


class KeywordList(AutoList[Keyword]):
    """
    Applicable documents: Arbitrary text, blog articles, academic papers

    Function introduction:
    Extract keywords from text with category and description information. Suitable for content tag generation and topic analysis.

    Example:
        >>> template = KeywordList(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Galaxy Interstellar announces successful maiden flight of Shenzhou-50...")
        >>> for keyword in template:
        ...     print(f"{keyword.term} ({keyword.category}): {keyword.description}")
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
        Initialize keyword list template.
        
        Args:
            llm_client: LLM client for knowledge extraction
            embedder: Embedding model for semantic search
            max_workers: Maximum number of worker threads, default: 10
            verbose: Whether to output detailed logs, default: False
            **kwargs: Other technical parameters, passed to base class
        """
        super().__init__(
            item_schema=Keyword,
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
        Display keyword list.
        
        Args:
            top_k_for_search: Number of keywords to return for semantic search, default: 3
            top_k_for_chat: Number of keywords to use for chat, default: 3
        """
        def itemLabelExtractor(item: Keyword) -> str:
            return f"{item.term} ({item.category})"
        
        super().show(
            item_label_extractor=itemLabelExtractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
