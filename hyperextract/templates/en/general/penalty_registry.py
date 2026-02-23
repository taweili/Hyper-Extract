"""Penalty Registry - Deduplicate and summarize specific violations and their corresponding consequences to form a clear penalty ledger.

Suitable for internal risk control, compliance checks, etc.
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet


class PenaltyEntry(BaseModel):
    """Violation penalty entry"""
    violation: str = Field(description="Violation description")
    severity: str = Field(description="Severity: Minor, Moderate, Serious, VerySerious")
    penalty: str = Field(description="Penalty measure")
    applicableClause: str = Field(description="Applicable clause", default="")
    notes: str = Field(description="Notes", default="")


_PROMPT = """## Role and Task
You are a professional compliance analysis expert. Please extract all violations and their corresponding penalty measures from the text to form a violation penalty registry.

## Extraction Rules
1. Extract all violations and their corresponding penalty measures
2. Assign a severity level to each violation: Minor, Moderate, Serious, VerySerious
3. Maintain the accuracy of violations and penalty measures
4. Record applicable clauses (if available)
5. Add notes (if available)

### Constraints
- Deduplication: Only keep one record for the same violation and penalty measure combination
- Maintain objectivity and accuracy, do not add information not in the text

### Source text:
"""


class PenaltyRegistry(AutoSet[PenaltyEntry]):
    """
    Applicable documents: Company internal management systems, administrative regulations, compliance guidelines

    Function introduction:
    Deduplicate and summarize specific violations and their corresponding consequences to form a clear penalty ledger. Suitable for internal risk control, compliance checks, etc.

    Example:
        >>> template = PenaltyRegistry(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Universe First Slacker Company Employee Attendance Management System...")
        >>> for entry in template:
        ...     print(f"{entry.violation} -> {entry.penalty}")
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
        Initialize penalty registry template.
        
        Args:
            llm_client: LLM client for knowledge extraction
            embedder: Embedding model for semantic search
            max_workers: Maximum number of worker threads, default: 10
            verbose: Whether to output detailed logs, default: False
            **kwargs: Other technical parameters, passed to base class
        """
        super().__init__(
            item_schema=PenaltyEntry,
            key_extractor=lambda x: f"{x.violation}_{x.penalty}",
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
        Display penalty registry.
        
        Args:
            top_k_for_search: Number of entries to return for semantic search, default: 3
            top_k_for_chat: Number of entries to use for chat, default: 3
        """
        def itemLabelExtractor(item: PenaltyEntry) -> str:
            return f"{item.violation} ({item.severity})"
        
        super().show(
            item_label_extractor=itemLabelExtractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
