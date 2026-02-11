from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class MovementEntity(BaseModel):
    """An art movement, style, artist, or influential work."""
    name: str = Field(description="Name of the movement (e.g., Impressionism) or Artist.")
    category: str = Field(
        description="Category: 'Movement', 'Style', 'Artist', 'Manifesto', 'Masterpiece'."
    )
    attributes: Optional[str] = Field(description="Key characteristics, materials, or timeframe.")

class ArtInfluenceEdge(BaseModel):
    """Influence, derivation, or membership relations in art history."""
    source: str = Field(description="The precursor or movement.")
    target: str = Field(description="The follower or specific work/artist.")
    relation: str = Field(
        description="Relation: 'Influenced', 'Founder of', 'Member of', 'Reaction against', 'Derived from'."
    )
    details: Optional[str] = Field(description="Specific stylistic techniques or historical events.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

MOVEMENT_GRAPH_PROMPT = (
    "You are an art historian specializing in the evolution of artistic styles. Extract a graph of art movements and their influences.\n\n"
    "Guidelines:\n"
    "- Identify distinct art movements and the artists associated with them.\n"
    "- Map how one movement influenced another (e.g., Post-Impressionism reacting to Impressionism).\n"
    "- Capture the core philosophies and visual characteristics defined in manifestos or works."
)

MOVEMENT_NODE_PROMPT = (
    "Extract art movements, styles, associated artists, and pivotal artworks. Describe their visual language and key theories."
)

MOVEMENT_EDGE_PROMPT = (
    "Define connections between movements and individuals. Use relations like 'Reaction against' or 'Influenced'. "
    "Note specific techniques passed between generations."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class ArtMovementGraph(AutoGraph[MovementEntity, ArtInfluenceEdge]):
    """
    Template for mapping art movements, stylistic influences, and artist school affiliations.
    
    Useful for educational applications and art historical analysis.
    
    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI()
        >>> embedder = OpenAIEmbeddings()
        >>> graph = ArtMovementGraph(llm_client=llm, embedder=embedder)
        >>> text = "Impressionism, led by Monet, was later challenged by the structured approach of Post-Impressionism."
        >>> graph.feed_text(text)
        >>> print(graph.nodes) # Movement and Artist details
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
        **kwargs: Any
    ):
        """
        Initialize the ArtMovementGraph template.

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
            node_schema=MovementEntity,
            edge_schema=ArtInfluenceEdge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.relation.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=MOVEMENT_GRAPH_PROMPT,
            prompt_for_node_extraction=MOVEMENT_NODE_PROMPT,
            prompt_for_edge_extraction=MOVEMENT_EDGE_PROMPT,
            **kwargs
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
        def node_label_extractor(node: MovementEntity) -> str:
            info = f" ({ node.category })" if getattr(node, "category", None) else ""
            return f"{ node.name }{info}"
    
        def edge_label_extractor(edge: ArtInfluenceEdge) -> str:
            return f"{ edge.source }"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
