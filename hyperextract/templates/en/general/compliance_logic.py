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

    name: str = Field(description="Element name, exact name from text")
    category: str = Field(
        description="Element category: Subject, Action, Condition, Other"
    )
    description: str = Field(description="Brief description", default="")


class ComplianceRule(BaseModel):
    """Compliance Rule - Hyperedge"""

    ruleType: str = Field(description="Rule type: Must, MustNot, May, Other")
    participants: List[str] = Field(
        description="List of participating element names, must use names from extracted nodes"
    )
    action: str = Field(description="Required or prohibited action content")
    condition: str = Field(
        description="Applicable conditions/prerequisites", default=""
    )
    consequence: str = Field(
        description="Violation consequences/incentives", default=""
    )
    sourceClause: str = Field(description="Source clause of the rule", default="")


_PROMPT = """## Role and Task
You are a professional compliance assessor, skilled in extracting compliance elements and analyzing rule logic from documents. Please extract compliance elements and rules from the text to build a compliance behavior hypergraph.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to basic elements that make up rules, divided into four categories:
  - **Subject**: Entities that perform actions (individuals, departments, organizations, roles, etc.)
  - **Action**: Specific actions or behaviors (submit, approve, execute, prohibit, etc.)
  - **Condition**: Prerequisites or scenarios where the rule applies (time, location, status, quantity, etc.)
  - **Other**: Elements that don't fall into the above categories (documents, files, status, results, etc.)
- **Hyperedge（Edge）**: In this template, "Hyperedge" is also known as "rule", connects multiple nodes and expresses the logic of "under what conditions, which subjects must/may not perform which actions".

## Extraction Rules
### Node Extraction
1. Extract elements involved in rules as nodes
2. Assign category to each element: Subject, Action, Condition, Other
3. Add brief description for each element

### Hyperedge Extraction
1. Only create rules from extracted nodes
2. Rule type: Must, MustNot, May, Other
3. Must contain ruleType, participants, and action
4. participants must strictly use names from extracted nodes
5. Try to fill other fields, use empty string for missing fields

### Source text:
"""

_NODE_PROMPT = """## Role and Task
You are a professional compliance element recognition expert, skilled in accurately identifying core compliance-related elements from documents. Please extract all compliance-related elements as nodes from the text.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to basic elements that make up rules, divided into four categories:
  - **Subject**: Entities that perform actions (individuals, departments, organizations, roles, etc.)
  - **Action**: Specific actions or behaviors (submit, approve, execute, prohibit, etc.)
  - **Condition**: Prerequisites or scenarios where the rule applies (time, location, status, quantity, etc.)
  - **Other**: Elements that don't fall into the above categories (documents, files, status, results, etc.)

## Extraction Rules
1. Extract concrete, atomic elements, not abstract "processes" or "comparison tables"
2. Use exact nouns or verbs from the text as element names
3. Assign correct category to each element
4. Add brief description (1-2 sentences) for each element

### Source text:
"""

_EDGE_PROMPT = """## Role and Task
You are a professional compliance rule analyst, skilled in building clear compliance rule relationships from given elements. Please extract compliance rule hyperedges from the given node list.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to basic elements that make up rules, serving as participants in hyperedges.
- **Hyperedge(Edge)**: In this template, "Hyperedge" is also known as "rule", connects multiple nodes and expresses the logic of "under what conditions, which subjects must/may not perform which actions".

## Extraction Rules
1. **participants must strictly use names from the "Known Elements List" below**, do not create new names
2. Rules must contain ruleType, participants, and action
3. participants should include: involved subjects, executed actions, and related other elements

### Rule Types
- **Must**: Mandatory actions to perform
- **MustNot**: Prohibited actions
- **May**: Permissible actions
- **Other**: Rules that don't fall into the above categories

"""


class ComplianceLogic(AutoHypergraph[ComplianceElement, ComplianceRule]):
    """
    Applicable documents: Compliance guidelines, administrative regulations, company management systems

    Function introduction:
    Model complex logic of "under what conditions, which subjects must/may not perform which actions". Suitable for compliance auditing, risk identification, etc.

    Example:
        >>> template = ComplianceLogic(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Company Compliance Manual...")
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
            edge_key_extractor=lambda x: (
                f"{sorted(x.participants)}_{x.ruleType}_{x.action}"
            ),
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
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ):
        """
        Display compliance logic hypergraph.

        Args:
            top_k_nodes_for_search: Number of nodes to return for semantic search, default: 3
            top_k_edges_for_search: Number of edges to return for semantic search, default: 3
            top_k_nodes_for_chat: Number of nodes to use for chat, default: 3
            top_k_edges_for_chat: Number of edges to use for chat, default: 3
        """

        def node_label_extractor(node: ComplianceElement) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: ComplianceRule) -> str:
            return f"[{edge.ruleType}] {edge.action}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
