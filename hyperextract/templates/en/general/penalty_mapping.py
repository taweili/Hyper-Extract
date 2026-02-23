"""Penalty Mapping - Describe the evolution path from "violation behavior" to "handling procedure" to "final result".

Suitable for risk tracing, penalty logic analysis, etc.
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class PenaltyNode(BaseModel):
    """Penalty causal node"""
    name: str = Field(description="Node name")
    type: str = Field(description="Node type: Violation, HandlingProcedure, PenaltyResult, Other")
    description: str = Field(description="Detailed description")


class PenaltyPath(BaseModel):
    """Penalty causal path edge"""
    source: str = Field(description="Source node name")
    target: str = Field(description="Target node name")
    relation: str = Field(description="Relationship type: Causes, Triggers, Executes, Produces, Other")
    details: str = Field(description="Detailed explanation", default="")


_PROMPT = """## Role and Task
You are a professional penalty logic analysis expert. Please extract the evolution path from "violation behavior" to "handling procedure" to "final result" from the text to build a penalty mapping.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a key unit in the penalty causal chain, including types such as Violation, HandlingProcedure, and PenaltyResult, used to represent key links in the penalty process.
- **Edge**: In this template, "Edge" refers to a causal relationship between nodes, including binary relationships such as Causes, Triggers, Executes, and Produces, used to represent the evolution path from violation to penalty.

## Extraction Rules
### Node Extraction Rules
1. Extract all key nodes: Violation, HandlingProcedure, PenaltyResult, etc.
2. Assign a type to each node: Violation, HandlingProcedure, PenaltyResult, Other
3. Add a detailed description to each node

### Edge Extraction Rules
1. Only create causal path edges from extracted nodes
2. Record the causal relationship between nodes
3. Relationship types include: Causes, Triggers, Executes, Produces, Other
4. Add detailed explanations (if available)

### Constraints
- Ensure the logical order of causal relationships is correct
- Maintain objectivity and accuracy, do not add information not in the text

### Source text:
"""

_NODE_PROMPT = """## Role and Task
You are a professional penalty node recognition expert. Please extract all key nodes from the text.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a key unit in the penalty causal chain, including types such as Violation, HandlingProcedure, and PenaltyResult, used to represent key links in the penalty process.

## Extraction Rules
1. Extract all key nodes: Violation, HandlingProcedure, PenaltyResult, etc.
2. Assign a type to each node: Violation, HandlingProcedure, PenaltyResult, Other
3. Add a detailed description to each node

### Source text:
"""

_EDGE_PROMPT = """## Role and Task
You are a professional penalty causal relationship recognition expert. Please extract the causal relationship between nodes from the given node list.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a key unit in the penalty causal chain, as participants in causal relationships.
- **Edge**: In this template, "Edge" refers to a causal relationship between nodes, including binary relationships such as Causes, Triggers, Executes, and Produces, used to represent the evolution path from violation to penalty.

## Extraction Rules
### Constraints
1. Only extract edges from the known node list below
2. Do not create unlisted nodes

"""


class PenaltyMapping(AutoGraph[PenaltyNode, PenaltyPath]):
    """
    Applicable documents: Company internal management systems, administrative regulations, compliance guidelines, penalty cases

    Function introduction:
    Describe the evolution path from "violation behavior" to "handling procedure" to "final result". Suitable for risk tracing, penalty logic analysis, etc.

    Example:
        >>> template = PenaltyMapping(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Universe First Slacker Company Employee Penalty Regulations...")
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
        Initialize penalty mapping template.
        
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
            node_schema=PenaltyNode,
            edge_schema=PenaltyPath,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relation}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
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
        Display penalty mapping.
        
        Args:
            top_k_for_search: Number of nodes/edges to return for semantic search, default: 3
            top_k_for_chat: Number of nodes/edges to use for chat, default: 3
        """
        def node_label_extractor(node: PenaltyNode) -> str:
            return f"{node.name} ({node.type})"
        
        def edge_label_extractor(edge: PenaltyPath) -> str:
            return edge.relation
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
