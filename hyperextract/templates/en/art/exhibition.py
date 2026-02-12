from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class ExhibitionEntity(BaseModel):
    """An element of an art exhibition (Curator, Theme, Work, Venue, Sponsor)."""

    name: str = Field(description="Name of the exhibition, artist, or curator.")
    type: str = Field(
        description="Type: 'Exhibition', 'Theme', 'Artwork', 'Curator', 'Venue', 'Partner'."
    )
    details: Optional[str] = Field(
        description="Exhibition dates, conceptual notes, or location."
    )


class ExhibitionRelation(BaseModel):
    """Connectivity within an exhibition's planning and execution."""

    source: str = Field(description="The organizing or controlling entity.")
    target: str = Field(description="The related work or participant.")
    relation_type: str = Field(
        description="Type: 'Curated by', 'Featured in', 'Hosted at', 'Sponsored by', 'Thematically linked to'."
    )
    context: Optional[str] = Field(
        description="Specific room, loan conditions, or thematic sub-group."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

EXHIBITION_GRAPH_PROMPT = (
    "You are a museum curator and exhibition designer. Map the structure of an art exhibition.\n\n"
    "Guidelines:\n"
    "- Identify the exhibition title, its central themes, and the participating artists/works.\n"
    "- Connect works to their thematic sections and the curators responsible.\n"
    "- Capture logistics like venues and sponsors."
)

EXHIBITION_NODE_PROMPT = "Extract exhibition components: titles, venues, themes, specific artworks, and key personnel (curators, designers)."

EXHIBITION_EDGE_PROMPT = "Link items within the exhibition. Show which artworks belong to which theme and identify the hosting venue and sponsors."

# ==============================================================================
# 3. Template Class
# ==============================================================================


class ExhibitionGraph(AutoGraph[ExhibitionEntity, ExhibitionRelation]):
    """
    Template for curatorial planning and exhibition analysis.

    Tracks the relationships between artworks, themes, curators, and venues.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI()
        >>> embedder = OpenAIEmbeddings()
        >>> graph = ExhibitionGraph(llm_client=llm, embedder=embedder)
        >>> text = "The 'Surrealist Dreams' exhibition was curated by Alice Smith at the Tate Modern."
        >>> graph.feed_text(text)
        >>> print(graph.edges) # Exhibition connections
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
        Initialize the ExhibitionGraph template.

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
            node_schema=ExhibitionEntity,
            edge_schema=ExhibitionRelation,
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
            prompt=EXHIBITION_GRAPH_PROMPT,
            prompt_for_node_extraction=EXHIBITION_NODE_PROMPT,
            prompt_for_edge_extraction=EXHIBITION_EDGE_PROMPT,
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

        def node_label_extractor(node: ExhibitionEntity) -> str:
            info = f" ({node.type})" if getattr(node, "type", None) else ""
            return f"{node.name}{info}"

        def edge_label_extractor(edge: ExhibitionRelation) -> str:
            return f"{edge.relation_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
