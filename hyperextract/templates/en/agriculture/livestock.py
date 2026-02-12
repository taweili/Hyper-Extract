from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class AnimalNode(BaseModel):
    """An entity in livestock management (e.g., individual animal, breed, group, health condition)."""

    name: str = Field(description="Name or ID of the animal/group.")
    category: str = Field(
        description="Category: 'Individual', 'Breed', 'Strain', 'Health Status', 'Nutrient/Feed', 'Facility'."
    )
    traits: Optional[str] = Field(
        description="Key physical traits, genetic markers, or health metrics."
    )


class BreedingRelation(BaseModel):
    """Relationships in breeding and health management."""

    source: str = Field(description="The source livestock entity.")
    target: str = Field(description="The target livestock entity.")
    relation_type: str = Field(
        description="Type: 'parent of', 'bred with', 'member of', 'diagnosed with', 'fed with'."
    )
    details: Optional[str] = Field(
        description="Inherited traits, dosage, or specific health observations."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

LIVESTOCK_GRAPH_PROMPT = (
    "You are a livestock specialist and geneticist. Extract a breeding and health management graph.\n\n"
    "Guidelines:\n"
    "- Identify individual animals and their breeds.\n"
    "- Map pedigree relationships (parent-offspring) and breeding pairs.\n"
    "- Link animals to their health status, vaccinations, and nutrition records."
)

LIVESTOCK_NODE_PROMPT = (
    "Extract livestock entities: identify specific animals (by ID or name), breeds, health conditions, "
    "vaccines, and specific feed types. Provide relevant traits or metrics for each."
)

LIVESTOCK_EDGE_PROMPT = (
    "Link livestock entities logically. Map family trees (parental links), breeding history, "
    "and medical/nutritional events. Ensure relation types like 'bred with' or 'fed with' are used accurately."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class LivestockGraph(AutoGraph[AnimalNode, BreedingRelation]):
    """
    Template for managing livestock pedigrees, health records, and breeding programs.

    Useful for farm management software, veterinary records, and genetic tracking.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> graph = LivestockGraph(llm_client=llm, embedder=embedder)
        >>> text = "Cow #402 (Angus) was crossbred with Bull #09 to improve meat quality."
        >>> graph.feed_text(text)
        >>> print(graph.edges) # Extracted breeding relationship
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize the LivestockGraph template.

        Args:
            llm_client: The language model client for extraction.
            embedder: The embedding model for deduplication.
            extraction_mode: "one_stage" or "two_stage".
            chunk_size: Max characters per chunk.
            chunk_overlap: Overlap between chunks.
            max_workers: Parallel processing workers.
            verbose: Enable progress logging.
            **kwargs: Extra arguments for AutoGraph.
        """
        super().__init__(
            node_schema=AnimalNode,
            edge_schema=BreedingRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.relation_type.lower()})-->{x.target.strip()}"
            ),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=LIVESTOCK_GRAPH_PROMPT,
            prompt_for_node_extraction=LIVESTOCK_NODE_PROMPT,
            prompt_for_edge_extraction=LIVESTOCK_EDGE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ) -> None:
        """
        Visualize the graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of nodes to retrieve for search context. Default 3.
            top_k_edges_for_search (int): Number of edges to retrieve for search context. Default 3.
            top_k_nodes_for_chat (int): Number of nodes to retrieve for chat context. Default 3.
            top_k_edges_for_chat (int): Number of edges to retrieve for chat context. Default 3.
        """

        def node_label_extractor(node: AnimalNode) -> str:
            info = f" ({node.category})" if getattr(node, "category", None) else ""
            return f"{node.name}{info}"

        def edge_label_extractor(edge: BreedingRelation) -> str:
            return f"{edge.relation_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
