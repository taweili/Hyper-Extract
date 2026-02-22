"""Encyclopedia Item - Extract structured attribute information for a single subject (similar to an Infobox).

Suitable for Wikipedia, professional dictionary entries, etc.
"""

from typing import Any, Optional, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class EncyclopediaInfo(BaseModel):
    """Encyclopedia item infobox"""
    title: str = Field(description="Entry title")
    entityType: str = Field(description="Entity type: Person, Location, Organization, Event, Concept, Item, Other")
    alternativeNames: List[str] = Field(description="Aliases, common names, foreign names", default_factory=list)
    category: List[str] = Field(description="Category tags", default_factory=list)
    summary: str = Field(description="Abstract/introduction", default="")
    attributes: List[str] = Field(description="Key attribute list, each element in format 'AttributeName: AttributeValue'", default_factory=list)
    keyEvents: List[str] = Field(description="Important events/milestones", default_factory=list)
    relatedConcepts: List[str] = Field(description="Related concepts/entries", default_factory=list)


_PROMPT = """You are a professional encyclopedia editor. Please extract structured attribute information for a single subject from the text to build an encyclopedia item infobox.

### Extraction Rules
1. Identify the core subject of the text (Person, Location, Organization, Event, Concept, etc.)
2. Assign a type to the subject: Person, Location, Organization, Event, Concept, Item, Other
3. Extract all aliases, common names, or foreign names
4. Extract category tags (e.g., "Scientist", "Mathematics", "Ancient China")
5. Write a 100-200 word summary
6. Extract key attributes, each in format 'AttributeName: AttributeValue' (e.g., 'Date of Birth: 429', 'Nationality: China')
7. Extract important events or milestones
8. Extract related concepts or entries

### Constraints
- Only extract information explicitly mentioned in the text, do not add additional content
- Keep attribute names concise and clear
- Maintain objectivity and accuracy, consistent with encyclopedia style

### Source text:
"""


class EncyclopediaItem(AutoModel[EncyclopediaInfo]):
    """
    Applicable documents: Wikipedia entries, encyclopedia entries, professional dictionary entries

    Function introduction:
    Extract structured attribute information for a single subject (similar to an Infobox). Suitable for Wikipedia, professional dictionary entries, etc.

    Example:
        >>> template = EncyclopediaItem(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Zu Chongzhi (429-500), courtesy name Wenyuan, was from Qiuxian, Fanyang...")
        >>> print(template.data.title)
        >>> print(template.data.summary)
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
        Initialize encyclopedia item template.
        
        Args:
            llm_client: LLM client for knowledge extraction
            embedder: Embedding model for semantic search
            max_workers: Maximum number of worker threads, default: 10
            verbose: Whether to output detailed logs, default: False
            **kwargs: Other technical parameters, passed to base class
        """
        super().__init__(
            data_schema=EncyclopediaInfo,
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
        top_k: int = 3,
    ):
        """
        Display encyclopedia item.
        
        Args:
            top_k: Number of items to use for chat, default: 3
        """
        def label_extractor(item: EncyclopediaInfo) -> str:
            return f"{item.title} ({item.entityType})"
        
        super().show(
            label_extractor=label_extractor,
            top_k=top_k,
        )
