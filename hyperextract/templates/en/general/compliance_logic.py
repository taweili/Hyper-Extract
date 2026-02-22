"""Compliance Logic - Model complex logic of "under what conditions, which subjects must/may not perform which actions".

Suitable for compliance auditing, risk identification, etc.
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class ComplianceElement(BaseModel):
    """Compliance Element - Node"""
    name: str = Field(description="Element name")
    type: str = Field(description="Element type: Subject, Action, Condition, Other")
    description: str = Field(description="Brief description", default="")


class ComplianceRule(BaseModel):
    """Compliance Rule - Hyperedge"""
    rule_type: str = Field(description="Rule type: Must, MustNot, May, Other")
    action: str = Field(description="Required or prohibited action content")
    condition: str = Field(description="Applicable conditions/prerequisites", default="")
    penalty: str = Field(description="Violation consequences/penalties", default="")
    source_clause: str = Field(description="Source clause of the rule", default="")
    notes: str = Field(description="Additional notes", default="")
    participants: List[str] = Field(description="List of participating element names")


_PROMPT = """You are a professional compliance analysis expert. Please extract compliance elements and rules from the text, modeling the logic of "under what conditions, which subjects must/may not perform which actions" to build a compliance behavior hypergraph.

### Node Extraction Rules
1. Extract elements involved in rules as nodes
2. Assign type to each element: Subject, Action, Condition, Other
3. Add brief description for each element

### Hyperedge Extraction Rules
1. Only create compliance rule hyperedges from extracted elements
2. Assign rule type: Must, MustNot, May, Other
3. Fill in required or prohibited action content (required)
4. Extract applicable conditions/prerequisites (if available)
5. Extract violation consequences/penalties (if available)
6. Extract source clause (if available)
7. Add additional notes (if available)
8. List all participating element names (required)

### Constraints
- Ensure rule logic accuracy
- Maintain objectivity and accuracy, do not add information not in the text
- Each hyperedge must contain rule_type, action, and participants
- Try to fill other fields, use empty string for missing fields

### Source text:
"""

_NODE_PROMPT = """You are a professional compliance element recognition expert. Please extract all compliance-related elements as nodes from the text.

### Extraction Rules
1. Extract elements involved in rules
2. Assign type to each element: Subject, Action, Condition, Other
3. Add brief description for each element

### Source text:
"""

_EDGE_PROMPT = """You are a professional compliance rule extraction expert. Please extract compliance rule hyperedges from the given node (element) list.

### Constraints
1. Only extract rules (hyperedges) from the known element list below
2. Do not create unlisted elements
3. Each rule must contain rule_type, action, and participants
4. Try to fill other fields, use empty string for missing fields

"""


class ComplianceLogic(AutoHypergraph[ComplianceElement, ComplianceRule]):
    """
    Applicable documents: Compliance guidelines, administrative regulations, company management systems

    Function introduction:
    Model complex logic of "under what conditions, which subjects must/may not perform which actions". Suitable for compliance auditing, risk identification, etc.

    Example:
        >>> template = ComplianceLogic(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Universe First Slacker Company Compliance Manual...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize compliance logic hypergraph template.
        
        Args:
            llm_client: LLM client for knowledge extraction
            embedder: Embedding model for semantic search
            extraction_mode: Extraction mode, either "one_stage" (extract nodes and edges simultaneously)
                or "two_stage" (extract nodes first, then edges), default: "two_stage"
            max_workers: Maximum number of worker threads, default: 10
            verbose: Whether to output detailed logs, default: False
            **kwargs: Other technical parameters, passed to base class
        """
        super().__init__(
            node_schema=ComplianceElement,
            edge_schema=ComplianceRule,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{sorted(x.participants)}_{x.rule_type}_{x.action}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        Display compliance logic hypergraph.
        
        Args:
            top_k_for_search: Number of nodes/edges to return for semantic search, default: 3
            top_k_for_chat: Number of nodes/edges to use for chat, default: 3
        """
        def node_label_extractor(node: ComplianceElement) -> str:
            return f"{node.name} ({node.type})"

        def edge_label_extractor(edge: ComplianceRule) -> str:
            return f"[{edge.rule_type}] {edge.action}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
