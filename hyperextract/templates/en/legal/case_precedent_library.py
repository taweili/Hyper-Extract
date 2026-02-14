"""Case Precedent Library - Extracts and indexes legal precedents.

Builds a searchable legal precedent database by automatically merging information
about the same case from multiple sources.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

class PrecedentSchema(BaseModel):
    case_citation: str = Field(..., description="Official case citation/reference")
    court_name: Optional[str] = Field(None, description="Court that decided the case")
    judgment_year: Optional[str] = Field(None, description="Year of judgment")
    legal_issues: Optional[str] = Field(None, description="Legal questions raised")
    holding: Optional[str] = Field(None, description="Court's decision and legal principle")
    cited_statutes: Optional[str] = Field(None, description="Laws referenced in judgment")
    presiding_judges: Optional[str] = Field(None, description="Judge(s) who decided")
    impact_assessment: Optional[str] = Field(None, description="Impact on subsequent law")

_PROMPT = """You are a legal research specialist.
Extract precedent case information:
1. case_citation: Official case name/citation
2. court_name: Court that heard it
3. judgment_year: Decision year
4. legal_issues: Legal questions
5. holding: Court's ruling and principle
6. cited_statutes: Applicable laws
7. presiding_judges: Deciding judges
8. impact_assessment: Influence on future cases

### Source Text:
"""

class CasePrecedentLibrary(AutoSet[PrecedentSchema]):
    """Applicable to: Court decisions, Legal databases, Case law reports

    Extracts and indexes legal precedents by automatically merging case information
    from multiple sources into a unified searchable library.
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
            item_schema=PrecedentSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.case_citation.strip().lower(),
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(self, *, top_k_for_search: int = 3, top_k_for_chat: int = 3) -> None:
        def label_extractor(item: PrecedentSchema) -> str:
            year = f" ({item.judgment_year})" if item.judgment_year else ""
            return f"{item.case_citation}{year}"
        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
