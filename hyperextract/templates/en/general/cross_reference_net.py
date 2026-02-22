"""Cross Reference Network - Map hyperlinks or mutual reference relationships between concepts.

Suitable for encyclopedia internal links, cross-entry association graphs, etc.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class ReferenceNode(BaseModel):
    """Reference node"""
    name: str = Field(description="Concept/entry name")
    type: str = Field(description="Node type: Entry, Section, Concept, Person, Location, Other")
    description: str = Field(description="Brief description", default="")


class ReferenceRelation(BaseModel):
    """Reference relationship edge"""
    source: str = Field(description="Source entry/concept")
    target: str = Field(description="Referenced entry/concept")
    relationType: str = Field(description="Relationship type: Hyperlink, Reference, SeeAlso, Related, Other")
    context: str = Field(description="Reference context description", default="")


_PROMPT = """You are a professional knowledge network analysis expert. Please extract concepts/entries and their mutual reference relationships from the text to build a cross-reference network.

### Node Extraction Rules
1. Extract all mentioned concepts or entries
2. Assign a type to each node: Entry, Section, Concept, Person, Location, Other
3. Add a brief description for each node

### Edge Extraction Rules
1. Only create edges from extracted nodes
2. Relationship types include:
   - Hyperlink: Hyperlink relationship
   - Reference: Reference relationship
   - SeeAlso: See also relationship
   - Related: Related relationship
   - Other: Other relationships
3. Record reference context description

### Constraints
- Each edge must connect extracted nodes
- Do not create nodes or relationships not mentioned in the text
- Maintain objectivity and accuracy, do not add information not in the text

### Source text:
"""

_NODE_PROMPT = """You are a professional entry recognition expert. Please extract all concepts or entries as nodes from the text.

### Extraction Rules
1. Extract all mentioned concepts or entries
2. Assign a type to each node: Entry, Section, Concept, Person, Location, Other
3. Add a brief description for each node

### Source text:
"""

_EDGE_PROMPT = """You are a professional reference relationship extraction expert. Please extract mutual reference relationships between nodes from the given node list.

### Relationship Type Explanation
- Hyperlink: Hyperlink relationship
- Reference: Reference relationship
- SeeAlso: See also relationship
- Related: Related relationship
- Other: Other relationships

### Constraints
1. Only extract edges from the known node list below
2. Do not create unlisted nodes

"""


class CrossReferenceNet(AutoGraph[ReferenceNode, ReferenceRelation]):
    """
    Applicable documents: Wikipedia entries, knowledge base documents, web content with internal links

    Function introduction:
    Map hyperlinks or mutual reference relationships between concepts. Suitable for encyclopedia internal links, cross-entry association graphs, etc.

    Example:
        >>> template = CrossReferenceNet(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Machine Learning is a branch of Artificial Intelligence...")
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
        Initialize cross-reference network template.
        
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
            node_schema=ReferenceNode,
            edge_schema=ReferenceRelation,
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
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        Display cross-reference network.
        
        Args:
            top_k_for_search: Number of nodes/edges to return for semantic search, default: 3
            top_k_for_chat: Number of nodes/edges to use for chat, default: 3
        """
        def node_label_extractor(node: ReferenceNode) -> str:
            return f"{node.name} ({node.type})"
        
        def edge_label_extractor(edge: ReferenceRelation) -> str:
            return edge.relationType
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
