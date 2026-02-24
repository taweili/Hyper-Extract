"""Social Network Graph - Focus on extracting interpersonal relationships, interactions, and organizational affiliations.

Suitable for biography analysis, character setting research, etc.
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class PersonNode(BaseModel):
    """Person/organization node"""

    name: str = Field(description="Name")
    type: str = Field(description="Node type: Person, Organization, Institution, Other")
    description: str = Field(description="Brief description", default="")
    role: str = Field(description="Role/identity", default="")


class SocialRelation(BaseModel):
    """Social relationship edge"""

    source: str = Field(description="Source node")
    target: str = Field(description="Target node")
    relationType: str = Field(
        description="Relationship type: Family, Friend, Colleague, TeacherStudent, SupervisorSubordinate, Collaboration, Competition, Affiliation, Other"
    )
    details: str = Field(description="Detailed relationship explanation", default="")


_PROMPT = """## Role and Task
You are a professional social relationship analysis expert. Please extract people, organizations, and their mutual relationships from the text.

## Core Concept Definitions
- **Node**: person or organization unit
- **Edge**: social relationship between people/organizations

## Extraction Rules
### Node Extraction Rules
1. Extract all people, organizations, institutions
2. Assign a type to each node

### Edge Extraction Rules
1. Only create edges from extracted nodes
2. Each edge must connect extracted nodes

### Source text:
"""

_NODE_PROMPT = """## Role and Task
Please extract people and organizations as nodes from the text.

## Core Concept Definitions
- **Node**: person or organization unit

## Extraction Rules
1. Extract all people, organizations, institutions
2. Assign a type to each node

### Source text:
"""

_EDGE_PROMPT = """## Role and Task
Please extract social relationships between nodes from the known node list.

## Core Concept Definitions
- **Edge**: social relationship between people/organizations

## Constraints
1. Only extract edges from the known node list
2. Do not create unlisted nodes
"""


class SocialNetwork(AutoGraph[PersonNode, SocialRelation]):
    """
    Applicable Documents: Biographies, news articles, literary works, organizational documents

    Function Introduction:
    Extract people, organizations, and their mutual relationships to build a social network graph.
    Suitable for biography analysis, character setting research, organizational structure analysis, etc.

    Example:
        >>> template = SocialNetwork(llm_client=llm, embedder=embedder)
        >>> template.feed_text("John works at ABC Company as a manager...")
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
        Initialize the social network graph template.

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
            node_schema=PersonNode,
            edge_schema=SocialRelation,
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
        Display the social network graph.

        Args:
            top_k_nodes_for_search: Number of nodes returned by semantic search, default is 3
            top_k_edges_for_search: Number of edges returned by semantic search, default is 3
            top_k_nodes_for_chat: Number of nodes used for Q&A, default is 3
            top_k_edges_for_chat: Number of edges used for Q&A, default is 3
        """

        def node_label_extractor(node: PersonNode) -> str:
            return f"{node.name} ({node.type})"

        def edge_label_extractor(edge: SocialRelation) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
