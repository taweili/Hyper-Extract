"""Clause List - Break down regulations into atomic clauses for quick indexing.

Suitable for clause retrieval, full-text comparison, etc.
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class Clause(BaseModel):
    """Regulation clause"""
    clauseId: str = Field(description="Clause ID, e.g., Article 1, Section 2.1")
    title: str = Field(description="Clause title/subject", default="")
    content: str = Field(description="Clause content")
    category: str = Field(description="Clause category: GeneralProvisions, RightsAndObligations, Procedures, Penalties, SupplementaryProvisions, Other", default="Other")


_PROMPT = """You are a professional regulation clause breakdown expert. Please break down the text into atomic clauses.

### Extraction Rules
1. Break down the regulation into independent clauses according to its natural structure
2. Assign an ID to each clause (e.g., Article 1, Section 2.1, etc.)
3. Extract the content of each clause
4. Add an appropriate title or subject to the clause (if available)
5. Assign a category to each clause: GeneralProvisions, RightsAndObligations, Procedures, Penalties, SupplementaryProvisions, Other

### Constraints
- Keep clause content consistent with the original text
- Do not omit any clauses
- Maintain the integrity of clauses

### Source text:
"""


class ClauseList(AutoList[Clause]):
    """
    Applicable documents: Company internal management systems, administrative regulations, operation manuals, compliance guidelines

    Function introduction:
    Break down regulations into atomic clauses for quick indexing. Suitable for clause retrieval, full-text comparison, etc.

    Example:
        >>> template = ClauseList(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Universe First Slacker Company Employee Attendance Management System...")
        >>> for clause in template:
        ...     print(f"{clause.clauseId}: {clause.content}")
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
        Initialize clause list template.
        
        Args:
            llm_client: LLM client for knowledge extraction
            embedder: Embedding model for semantic search
            max_workers: Maximum number of worker threads, default: 10
            verbose: Whether to output detailed logs, default: False
            **kwargs: Other technical parameters, passed to base class
        """
        super().__init__(
            item_schema=Clause,
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
        Display clause list.
        
        Args:
            top_k_for_search: Number of clauses to return for semantic search, default: 3
            top_k_for_chat: Number of clauses to use for chat, default: 3
        """
        def itemLabelExtractor(item: Clause) -> str:
            if item.title:
                return f"{item.clauseId}: {item.title}"
            return f"{item.clauseId}"
        
        super().show(
            item_label_extractor=itemLabelExtractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
