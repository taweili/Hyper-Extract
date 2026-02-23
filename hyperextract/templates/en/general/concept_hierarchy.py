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
You are a professional concept structure analysis expert. Please extract concepts and their hierarchical relationships from the text to build a concept hierarchy graph.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a concept unit, categorized into types such as CoreConcept, Subconcept, Attribute, and Instance, used to represent basic concepts in a knowledge system.
- **Edge**: In this template, "Edge" refers to a hierarchical relationship between concepts, including binary relationships such as Subclass-Of (taxonomy), Part-Of (composition), and Instance-Of (instance).

## Extraction Rules
### Node Extraction Rules
1. Extract all concepts: CoreConcept, Subconcept, Attribute, Instance, etc.
2. Assign a type to each concept: CoreConcept, Subconcept, Attribute, Instance, Other
3. Add a brief description for each concept

### Edge Extraction Rules
1. Only create edges from extracted concepts
2. Relationship types include:
   - Subclass-Of: Taxonomy relationship (e.g., "Dog" is a subclass of "Animal")
   - Part-Of: Composition relationship (e.g., "Tire" is part of "Car")
   - Instance-Of: Instance relationship (e.g., "Zu Chongzhi" is an instance of "Mathematician")
   - Other: Other relationships
3. Each edge must connect extracted nodes

### Constraints
- Maintain clear hierarchical relationships, avoid circular dependencies
- Do not create concepts or relationships not mentioned in the text
- Maintain objectivity and accuracy, do not add information not in the text

### Source text:
"""

_NODE_PROMPT = """## Role and Task
You are a professional concept recognition expert. Please extract all concepts as nodes from the text.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a concept unit, categorized into types such as CoreConcept, Subconcept, Attribute, and Instance, used to represent basic concepts in a knowledge system.

## Extraction Rules
1. Extract all concepts: CoreConcept, Subconcept, Attribute, Instance, etc.
2. Assign a type to each concept: CoreConcept, Subconcept, Attribute, Instance, Other
3. Add a brief description for each concept

### Source text:
"""

_EDGE_PROMPT = """## Role and Task
You are a professional hierarchical relationship extraction expert. Please extract hierarchical relationships between concepts (nodes) from the given concept list.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a concept unit, as participants in hierarchical relationships.
- **Edge**: In this template, "Edge" refers to a hierarchical relationship between concepts, including binary relationships such as Subclass-Of (taxonomy), Part-Of (composition), and Instance-Of (instance).

## Extraction Rules
### Relationship Type Explanation
- Subclass-Of: Taxonomy relationship (subclass and superclass)
- Part-Of: Composition relationship (part and whole)
- Instance-Of: Instance relationship (instance and class)
- Other: Other relationships

### Constraints
1. Only extract edges from the known concept list below
2. Do not create unlisted concepts
3. Maintain clear hierarchical relationships, avoid circular dependencies

"""


class ConceptHierarchy(AutoGraph[ConceptNode, HierarchyRelation]):
    """
    Applicable documents: Science textbooks, knowledge base documents, classification system descriptions

    Function introduction:
    Build subclass relationships (Subclass-Of) or composition relationships (Part-Of). Suitable for scientific disciplines, textbook knowledge points, etc.

    Example:
        >>> template = ConceptHierarchy(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Machine learning is a branch of artificial intelligence...")
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
        Initialize concept hierarchy graph template.

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
        Display concept hierarchy graph.

        Args:
            top_k_nodes_for_search: Number of nodes to return for semantic search, default: 3
            top_k_edges_for_search: Number of edges to return for semantic search, default: 3
            top_k_nodes_for_chat: Number of nodes to use for chat, default: 3
            top_k_edges_for_chat: Number of edges to use for chat, default: 3
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
