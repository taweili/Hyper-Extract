from typing import List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class ConceptNode(BaseModel):
    """
    A fundamental academic concept that might belong to multiple disciplines.
    """
    name: str = Field(description="Standard name of the concept.")
    primary_field: str = Field(description="The primary discipline this concept originates from.")

class InterdisciplinaryEdge(BaseModel):
    """
    A hyperedge representing a connection between multiple concepts across different fields.
    """
    participants: List[str] = Field(
        description="List of nodes (concept names) participating in this interdisciplinary nexus."
    )
    unifying_theme: str = Field(
        description="The overarching theme or problem that connects these concepts (e.g., 'Complexity Theory', 'Universal Design')."
    )
    connectivity_insight: str = Field(
        description="The scientific or pedagogical value of connecting these specific dots."
    )

# ==============================================================================
# 2. Prompts
# ==============================================================================

NEXUS_CONSOLIDATED_PROMPT = (
    "You are a Polymath and Interdisciplinary Researcher. Identify deep connections between concepts across different academic fields.\n\n"
    "Extraction Rules:\n"
    "- Identify core concepts as Nodes.\n"
    "- Create Hyperedges that group multiple concepts under a unifying interdisciplinary theme.\n"
    "- Focus on finding surprising but scientifically valid bridges (e.g., connecting Biology and Economics through Game Theory)."
)

NEXUS_NODE_PROMPT = (
    "Identify fundamental academic concepts that carry cross-disciplinary potential.\n\n"
    "Rules:\n"
    "- Extract nouns/concepts that are central to their respective fields.\n"
    "- Identify the field of origin."
)

NEXUS_EDGE_PROMPT = (
    "Identify the 'Nexuses' or Hyperedges that unify a group of concepts.\n\n"
    "Rules:\n"
    "- A hyperedge must involve more than two nodes whenever possible.\n"
    "- Describe the unifying theme and the insight gained by this connection."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class InterdisciplinaryNexusHypergraph(AutoHypergraph[ConceptNode, InterdisciplinaryEdge]):
    """
    Educational template for mapping non-binary, multi-point academic connections.
    Ideal for research synthesis, curriculum cross-linking, and holistic knowledge management.

    Example Usage:
        >>> nexus = InterdisciplinaryNexusHypergraph(llm, embedder)
        >>> nexus.feed_text("The concept of Entropy applies to Heat (Physics) and Information (Information Theory).")
        >>> nexus.extract()
        >>> # Result will contain a Hyperedge connecting 'Heat' and 'Information' via 'Entropy'.
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
        Initialize the Interdisciplinary Nexus Template.

        Args:
            llm_client (BaseChatModel): The LLM used for extraction.
            embedder (Embeddings): The embedding model for deduplication.
            extraction_mode (str): 'one_stage' or 'two_stage'.
            chunk_size (int): Size of chunks.
            chunk_overlap (int): Overlap.
            max_workers (int): Workers.
            verbose (bool): Logs.
            **kwargs: Args for AutoHypergraph.
        """
        super().__init__(
            node_schema=ConceptNode,
            edge_schema=InterdisciplinaryEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.unifying_theme.strip().lower()}_linking_{sorted(x.participants)}"
            ),
            nodes_in_edge_extractor=lambda x: [p.strip().lower() for p in x.participants],
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=NEXUS_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=NEXUS_NODE_PROMPT,
            prompt_for_edge_extraction=NEXUS_EDGE_PROMPT,
            **kwargs,
        )
