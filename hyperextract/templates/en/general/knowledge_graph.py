"""General Knowledge Graph - Extract entities and relationships from any text.

Suitable for unstructured documents like arbitrary text, web scraped content, etc., to extract general entities and their relationships.
"""

from typing import Any, Optional, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class GeneralEntity(BaseModel):
    """General entity node"""

    name: str = Field(
        description="Entity name, e.g., person name, organization name, product name"
    )
    category: str = Field(
        description="Entity type: Person, Organization, Location, Product, Concept, Other"
    )
    description: str = Field(description="Brief description", default="")


class GeneralRelation(BaseModel):
    """General relationship edge"""

    source: str = Field(description="Source entity")
    target: str = Field(description="Target entity")
    relationType: str = Field(
        description="Relationship type: BelongsTo, LocatedIn, CollaboratesWith, CompetesWith, InventedBy, CreatedBy, RelatedTo, etc."
    )
    details: str = Field(description="Detailed description", default="")


_PROMPT = """## Role and Task
You are a professional knowledge graph extraction expert. Please extract all entities (nodes) and their relationships (edges) from the text.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a general entity, including types such as Person, Organization, Location, Product, Concept, etc., used to represent basic entities in a knowledge graph.
- **Edge**: In this template, "Edge" refers to a binary relationship between entities, including relationship types such as BelongsTo, LocatedIn, CollaboratesWith, CompetesWith, InventedBy, CreatedBy, and RelatedTo.

## Extraction Rules
### Node Extraction Rules
1. Extract all entities: Person, Organization, Location, Product, Concept, etc.
2. Assign a type to each entity: Person, Organization, Location, Product, Concept, Other
3. Keep entity names consistent with the original text
4. Add a brief description for each entity

### Edge Extraction Rules
1. Only create edges from extracted entities
2. Relationship types include: BelongsTo, LocatedIn, CollaboratesWith, CompetesWith, InventedBy, CreatedBy, RelatedTo, etc.

### Constraints
- Each edge must connect extracted nodes
- Do not create entities or relationships not mentioned in the text
- Maintain objectivity and accuracy, do not add information not in the text

### Source text:
"""

_NODE_PROMPT = """## Role and Task
You are a professional entity recognition expert. Please extract all key entities as nodes from the text.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a general entity, including types such as Person, Organization, Location, Product, Concept, etc., used to represent basic entities in a knowledge graph.

## Extraction Rules
1. Extract all entities: Person, Organization, Location, Product, Concept, etc.
2. Assign a type to each entity: Person, Organization, Location, Product, Concept, Other
3. Keep entity names consistent with the original text
4. Add a brief description for each entity

### Source text:
"""

_EDGE_PROMPT = """## Role and Task
You are a professional relationship extraction expert. Please extract relationships between entities from the given entity list.

## Core Concept Definitions
- **Node**: In this template, "Node" refers to a general entity, as participants in relationships.
- **Edge**: In this template, "Edge" refers to a binary relationship between entities, including relationship types such as BelongsTo, LocatedIn, CollaboratesWith, CompetesWith, InventedBy, CreatedBy, and RelatedTo.

## Extraction Rules
### Constraints
1. Only extract edges from the known entity list below
2. Do not create unlisted entities
3. Relationship types include: BelongsTo, LocatedIn, CollaboratesWith, CompetesWith, InventedBy, CreatedBy, RelatedTo, etc.

"""


class KnowledgeGraph(AutoGraph[GeneralEntity, GeneralRelation]):
    """
    Applicable documents: Arbitrary text, web scraped content, blog articles, news reports

    Function introduction:
    Extract general entities and their relationships from any text to build a knowledge graph. Supports multiple entity types including Person, Organization, Location, Product, Concept, etc.

    Example:
        >>> template = KnowledgeGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Galaxy Interstellar announces successful maiden flight of Shenzhou-50...")
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
        Initialize general knowledge graph template.

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
            node_schema=GeneralEntity,
            edge_schema=GeneralRelation,
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
        Display knowledge graph.

        Args:
            top_k_nodes_for_search: Number of nodes to return for semantic search, default: 3
            top_k_edges_for_search: Number of edges to return for semantic search, default: 3
            top_k_nodes_for_chat: Number of nodes to use for chat, default: 3
            top_k_edges_for_chat: Number of edges to use for chat, default: 3
        """

        def node_label_extractor(node: GeneralEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: GeneralRelation) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
