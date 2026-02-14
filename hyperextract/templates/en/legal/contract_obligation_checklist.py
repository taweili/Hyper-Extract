"""Contract Obligation Checklist - Extracts obligations and prohibitions from contracts.

Builds a comprehensive compliance checklist by extracting all duties, responsibilities,
and restrictions without deduplication to preserve complete audit trails.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList

class ObligationSchema(BaseModel):
    obligated_party: str = Field(..., description="Party responsible for performance")
    obligation_type: str = Field(..., description="'MUST' (required) or 'MUST_NOT' (prohibited)")
    action_description: str = Field(..., description="Specific action or requirement")
    trigger_condition: Optional[str] = Field(None, description="When/if the obligation applies")
    breach_penalty: Optional[str] = Field(None, description="Consequences of non-performance")
    clause_reference: Optional[str] = Field(None, description="Original contract clause number")

_PROMPT = """You are a contract lawyer and compliance auditor.
Extract all obligations and restrictions from the contract:
1. obligated_party: Who must perform
2. obligation_type: MUST (required) or MUST_NOT (prohibited)
3. action_description: Specific action/requirement
4. trigger_condition: When obligation applies
5. breach_penalty: Penalty for non-compliance
6. clause_reference: Contract clause number

Extract EVERY obligation independently. No merging.

### Source Text:
"""

class ContractObligationChecklist(AutoList[ObligationSchema]):
    """Applicable to: Contracts, ToS, Agreements, Compliance documents

    Extracts a complete compliance checklist preserving every obligation separately
    for comprehensive audit and risk analysis.
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
            item_schema=ObligationSchema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(self, *, top_k_for_search: int = 3, top_k_for_chat: int = 3) -> None:
        def label_extractor(item: ObligationSchema) -> str:
            return f"{item.obligation_type}: {item.action_description[:50]}"
        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
