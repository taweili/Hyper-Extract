"""Personal Profile - Aggregate static attributes of a person (birth/death dates, education, core identity).

Suitable for resumes, person introductions, obituary summaries, etc.
"""

from typing import Any, Optional, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class PersonalInfo(BaseModel):
    """Personal profile information"""
    name: str = Field(description="Name")
    gender: Optional[str] = Field(description="Gender", default=None)
    birthDate: Optional[str] = Field(description="Date of birth, format: YYYY-MM-DD or YYYY", default=None)
    deathDate: Optional[str] = Field(description="Date of death, format: YYYY-MM-DD or YYYY", default=None)
    nationality: Optional[str] = Field(description="Nationality", default=None)
    birthPlace: Optional[str] = Field(description="Place of birth", default=None)
    education: List[str] = Field(description="Education background", default_factory=list)
    occupations: List[str] = Field(description="Occupations/identities", default_factory=list)
    coreIdentity: List[str] = Field(description="Core identity/tags", default_factory=list)
    majorAchievements: List[str] = Field(description="Major achievements", default_factory=list)
    affiliations: List[str] = Field(description="Affiliated organizations/institutions", default_factory=list)
    summary: str = Field(description="Personal introduction", default="")


_PROMPT = """## Role and Task
You are a professional personal profile editor. Please extract static attribute information of this person from the text to build a personal profile.

## Extraction Rules
1. Extract basic information: name, gender, date of birth, date of death, nationality, place of birth, etc.
2. Extract education background
3. Extract occupation or identity information
4. Extract core identity tags
5. Extract major achievements
6. Extract affiliated organizations or institutions
7. Write a 100-200 word personal introduction

### Date Format Requirements
All date information should be converted to "YYYY-MM-DD" format (e.g., 429-01-01) or year only (e.g., 429).

### Constraints
- Only extract information explicitly mentioned in the text, do not add additional content
- Maintain objectivity and accuracy
- Leave blank if information is missing, do not fabricate

### Source text:
"""


class PersonalProfile(AutoModel[PersonalInfo]):
    """
    Applicable documents: Resumes, person introductions, obituary summaries, Wikipedia person entries

    Function introduction:
    Aggregate static attributes of a person (birth/death dates, education, core identity). Suitable for resumes, person introductions, obituary summaries, etc.

    Example:
        >>> template = PersonalProfile(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Zu Chongzhi (429-500), courtesy name Wenyuan, was from Qiuxian, Fanyang...")
        >>> print(template.data.name)
        >>> print(template.data.birthDate)
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
        Initialize personal profile template.
        
        Args:
            llm_client: LLM client for knowledge extraction
            embedder: Embedding model for semantic search
            max_workers: Maximum number of worker threads, default: 10
            verbose: Whether to output detailed logs, default: False
            **kwargs: Other technical parameters, passed to base class
        """
        super().__init__(
            data_schema=PersonalInfo,
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
        Display personal profile.
        
        Args:
            top_k: Number of items to use for chat, default: 3
        """
        def label_extractor(item: PersonalInfo) -> str:
            if item.birthDate and item.deathDate:
                return f"{item.name} ({item.birthDate}-{item.deathDate})"
            return item.name
        
        super().show(
            label_extractor=label_extractor,
            top_k=top_k,
        )
