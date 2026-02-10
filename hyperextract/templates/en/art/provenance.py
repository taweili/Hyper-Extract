from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.graphs import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class ArtEntity(BaseModel):
    """An entity in the art world (e.g., Artwork, Artist, Museum, Collector, Auction House)."""
    name: str = Field(description="Name of the artwork, person, or organization.")
    category: str = Field(
        description="Category: 'Artwork', 'Artist', 'Collector', 'Institution', 'Location'."
    )
    description: Optional[str] = Field(description="Medium, creation date, or historical status.")

class ProvenanceEdge(BaseModel):
    """The transfer of ownership or location of an artwork."""
    source: str = Field(description="Previous owner or starting location.")
    target: str = Field(description="New owner or destination.")
    transfer_type: str = Field(
        description="Type: 'Acquired by', 'Sold to', 'Donated to', 'Lent to', 'Commissioned by'."
    )
    specification: Optional[str] = Field(description="Date of transfer, sale price, or auction details.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

PROVENANCE_GRAPH_PROMPT = (
    "You are a fine arts historian and provenance researcher. Extract an artwork's ownership history graph.\n\n"
    "Guidelines:\n"
    "- Identify the core artwork and all its historical owners (Collectors, Museums, Kings).\n"
    "- Map the chronological sequence of transfers (Sales, Inheritances, Looting, Donations).\n"
    "- Capture specific dates and monetary values if mentioned."
)

PROVENANCE_NODE_PROMPT = (
    "Extract art entities: identify the artwork itself, the artists, collectors, museums, and auction houses. "
    "Note the medium of the artwork and roles of the people/institutions."
)

PROVENANCE_EDGE_PROMPT = (
    "Establish the chain of title. Connect previous owners to current owners using transfer types like 'Sold to' or 'Donated to'. "
    "Include time periods and transaction details in the specification."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class ProvenanceGraph(AutoGraph[ArtEntity, ProvenanceEdge]):
    """
    Template for tracking the ownership history (provenance) of artworks and artifacts.
    
    Essential for art authentication, museum archives, and historical research.
    
    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> graph = ProvenanceGraph(llm_client=llm, embedder=embedder)
        >>> text = "The painting was acquired by the Louvre in 1815 from the Borghese collection."
        >>> graph.feed_text(text)
        >>> print(graph.edges) # Extracted ownership transfer
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
        Initialize the ProvenanceGraph template.

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
            node_schema=ArtEntity,
            edge_schema=ProvenanceEdge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.transfer_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=PROVENANCE_GRAPH_PROMPT,
            prompt_for_node_extraction=PROVENANCE_NODE_PROMPT,
            prompt_for_edge_extraction=PROVENANCE_EDGE_PROMPT,
            **kwargs
        )
