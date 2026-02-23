"""Regulation Profile - Extract the name, version, scope, effective date, and core purpose of a regulation.

Suitable for regulation overview, version management, etc.
"""

from typing import Any, Optional, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class RegulationInfo(BaseModel):
    """Regulation metadata information"""
    title: str = Field(description="Regulation title")
    version: Optional[str] = Field(description="Version number", default=None)
    issuer: Optional[str] = Field(description="Issuing authority", default=None)
    issueDate: Optional[str] = Field(description="Issue date", default=None)
    effectiveDate: Optional[str] = Field(description="Effective date", default=None)
    expiryDate: Optional[str] = Field(description="Expiry date", default=None)
    scope: List[str] = Field(description="Applicable scope", default_factory=list)
    targetAudience: List[str] = Field(description="Target audience", default_factory=list)
    corePurpose: str = Field(description="Core purpose/objective", default="")
    keywords: List[str] = Field(description="Keywords/tags", default_factory=list)
    relatedRegulations: List[str] = Field(description="Related regulations", default_factory=list)


_PROMPT = """## Role and Task
You are a professional regulation analysis expert. Please extract metadata information of this regulation from the text to build a regulation profile.

## Extraction Rules
1. Extract the full name of the regulation
2. Extract version number (if available)
3. Extract issuing authority
4. Extract issue date, effective date, expiry date (if available)
5. Extract applicable scope
6. Extract target audience
7. Extract core purpose or objective (100-200 words)
8. Extract keywords or tags
9. Extract related other regulations

### Constraints
- Only extract information explicitly mentioned in the text, do not add additional content
- Maintain objectivity and accuracy
- Leave blank if information is missing, do not fabricate

### Source text:
"""


class RegulationProfile(AutoModel[RegulationInfo]):
    """
    Applicable documents: Company internal management systems, administrative regulations, operation manuals, compliance guidelines

    Function introduction:
    Extract the name, version, scope, effective date, and core purpose of a regulation. Suitable for regulation overview, version management, etc.

    Example:
        >>> template = RegulationProfile(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Universe First Slacker Company Employee Attendance Management System...")
        >>> print(template.data.title)
        >>> print(template.data.effectiveDate)
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
        Initialize regulation profile template.
        
        Args:
            llm_client: LLM client for knowledge extraction
            embedder: Embedding model for semantic search
            max_workers: Maximum number of worker threads, default: 10
            verbose: Whether to output detailed logs, default: False
            **kwargs: Other technical parameters, passed to base class
        """
        super().__init__(
            data_schema=RegulationInfo,
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
        Display regulation profile.
        
        Args:
            top_k: Number of items to use for chat, default: 3
        """
        def label_extractor(item: RegulationInfo) -> str:
            if item.version:
                return f"{item.title} (v{item.version})"
            return item.title
        
        super().show(
            label_extractor=label_extractor,
            top_k=top_k,
        )
