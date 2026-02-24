"""Concept Hierarchy - Build subclass relationships (Subclass-Of) or composition relationships (Part-Of).

Suitable for scientific disciplines, textbook knowledge points, etc.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class ConceptNode(BaseModel):
    """Concept node"""

    name: str = Field(description="Concept name")
    category: str = Field(
        description="Concept type: CoreConcept, Subconcept, Attribute, Instance, Other"
    )
    description: str = Field(description="Brief concept description", default="")


class HierarchyRelation(BaseModel):
    """Hierarchy relationship edge"""

    source: str = Field(description="Parent concept/whole concept")
    target: str = Field(description="Subconcept/part concept")
    relationType: str = Field(
        description="Relationship type: Subclass-Of (taxonomy), Part-Of (composition), Instance-Of (instance), Other"
    )
    details: str = Field(description="Detailed relationship explanation", default="")


_PROMPT = """## Role and Task
You are a professional concept structure analysis expert. Please extract concepts and their hierarchical relationships from the text.

## Core Concept Definitions
- **Node**: concept unit
- **Edge**: hierarchical relationship between concepts

## Extraction Rules
### Node Extraction Rules
1. Extract all concepts
2. Assign a type to each concept

### Edge Extraction Rules
1. Only create edges from extracted concepts
2. Each edge must connect extracted nodes

### Source text:
"""

_NODE_PROMPT = """## Role and Task
Please extract concepts as nodes from the text.

## Core Concept Definitions
- **Node**: concept unit

## Extraction Rules
1. Extract all concepts
2. Assign a type to each concept

### Source text:
"""

_EDGE_PROMPT = """## Role and Task
Please extract hierarchical relationships between concepts from the known concept list.

## Core Concept Definitions
- **Edge**: hierarchical relationship between concepts

## Constraints
1. Only extract edges from the known concept list
2. Do not create unlisted concepts
"""


class ConceptHierarchy(AutoGraph[ConceptNode, HierarchyRelation]):
    """
    Applicable Documents: Scientific disciplines, textbook knowledge points, ontology documents

    Function Introduction:
    Extract concepts and build subclass relationships (Subclass-Of) or composition relationships (Part-Of),
    suitable for scientific disciplines, textbook knowledge points, etc.

    Example:
        >>> template = ConceptHierarchy(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Animals are divided into mammals, birds, reptiles, amphibians and fish...")
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
        Initialize the concept hierarchy template.

        Args:
            llm_client: LLM client for knowledge extraction
            embedder: Embedding model for semantic retrieval
            extraction_mode: Extraction mode, optional "one_stage" (extract nodes and edges simultaneously)
                or "two_stage" (extract nodes first, then edges), default is "two_stage"
            max_workers: Maximum worker threads, default is 10
            verbose: Whether to output detailed logs, default is False
            **kwargs: Other technical parameters, passed to the base class
        """
        super().__init__(
            node_schema=ConceptNode,
            edge_schema=HierarchyRelation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
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
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ):
        """
        Display the concept hierarchy.

        Args:
            top_k_nodes_for_search: Number of nodes returned by semantic search, default is 3
            top_k_edges_for_search: Number of edges returned by semantic search, default is 3
            top_k_nodes_for_chat: Number of nodes used for Q&A, default is 3
            top_k_edges_for_chat: Number of edges used for Q&A, default is 3
        """

        def node_label_extractor(node: ConceptNode) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: HierarchyRelation) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
