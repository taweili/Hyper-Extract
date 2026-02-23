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
    relationType: str = Field(description="Relationship type: Family, Friend, Colleague, TeacherStudent, SupervisorSubordinate, Collaboration, Competition, Affiliation, Other")
    details: str = Field(description="Detailed relationship explanation", default="")


_PROMPT = """## Role and Task
You are a professional social relationship analysis expert. Please extract people, organizations, and their mutual relationships from the text to build a social network graph.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a person or organization unit, including types such as Person, Organization, Institution, etc., used to represent entities in a social network.
- **Edge**: In this template, "Edge" refers to a social relationship between people/organizations, including binary relationships such as Family, Friend, Colleague, TeacherStudent, SupervisorSubordinate, Collaboration, Competition, and Affiliation.

## Extraction Rules
### Node Extraction Rules
1. Extract all people, organizations, institutions, etc.
2. Assign a type to each node: Person, Organization, Institution, Other
3. Add a brief description for each node
4. Annotate role or identity for each node

### Edge Extraction Rules
1. Only create edges from extracted nodes
2. Relationship types include:
   - Family: Family relationships (parents, children, spouse, siblings, etc.)
   - Friend: Friend relationships
   - Colleague: Work partner relationships
   - TeacherStudent: Educational relationships
   - SupervisorSubordinate: Management relationships
   - Collaboration: Collaborative relationships
   - Competition: Competitive relationships
   - Affiliation: Organizational affiliation relationships
   - Other: Other relationships
3. Each edge must connect extracted nodes

### Constraints
- Do not create nodes or relationships not mentioned in the text
- Maintain objectivity and accuracy, do not add information not in the text

### Source text:
"""

_NODE_PROMPT = """## Role and Task
You are a professional person and organization recognition expert. Please extract all people and organizations as nodes from the text.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a person or organization unit, including types such as Person, Organization, Institution, etc., used to represent entities in a social network.

## Extraction Rules
1. Extract all people, organizations, institutions, etc.
2. Assign a type to each node: Person, Organization, Institution, Other
3. Add a brief description for each node
4. Annotate role or identity for each node

### Source text:
"""

_EDGE_PROMPT = """## Role and Task
You are a professional social relationship extraction expert. Please extract mutual relationships between nodes from the given node list.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a person or organization unit, as participants in social relationships.
- **Edge**: In this template, "Edge" refers to a social relationship between people/organizations, including binary relationships such as Family, Friend, Colleague, TeacherStudent, SupervisorSubordinate, Collaboration, Competition, and Affiliation.

## Extraction Rules
### Relationship Type Explanation
- Family: Family relationships (parents, children, spouse, siblings, etc.)
- Friend: Friend relationships
- Colleague: Work partner relationships
- TeacherStudent: Educational relationships
- SupervisorSubordinate: Management relationships
- Collaboration: Collaborative relationships
- Competition: Competitive relationships
- Affiliation: Organizational affiliation relationships
- Other: Other relationships

### Constraints
1. Only extract edges from the known node list below
2. Do not create unlisted nodes

"""


class SocialNetwork(AutoGraph[PersonNode, SocialRelation]):
    """
    Applicable documents: Biographies, memoirs, novels, character setting documents

    Function introduction:
    Focus on extracting interpersonal relationships, interactions, and organizational affiliations. Suitable for biography analysis, character setting research, etc.

    Example:
        >>> template = SocialNetwork(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Zu Chongzhi studied under He Chengtian and debated with Dai Faxing...")
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
        Initialize social network graph template.
        
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
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        Display social network graph.
        
        Args:
            top_k_for_search: Number of nodes/edges to return for semantic search, default: 3
            top_k_for_chat: Number of nodes/edges to use for chat, default: 3
        """
        def node_label_extractor(node: PersonNode) -> str:
            if node.role:
                return f"{node.name} ({node.role})"
            return f"{node.name} ({node.type})"
        
        def edge_label_extractor(edge: SocialRelation) -> str:
            return edge.relationType
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
