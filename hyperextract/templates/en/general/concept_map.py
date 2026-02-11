from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class Concept(BaseModel):
    """A conceptual node representing a term, idea, or theory."""
    term: str = Field(description="The technical term or concept name.")
    definition: str = Field(description="A formal definition or explanation of the concept.")
    examples: Optional[List[str]] = Field(default_factory=list, description="Examples that illustrate this concept.")
    attributes: Optional[List[str]] = Field(default_factory=list, description="Key properties or attributes of the concept.")

class ConceptRelation(BaseModel):
    """A semantic relationship between two concepts."""
    source: str = Field(description="The source concept.")
    target: str = Field(description="The target concept.")
    relation_type: str = Field(
        description="Type of relationship (e.g., is-a, part-of, related-to, used-for, instance-of)."
    )

# ==============================================================================
# 2. Prompts
# ==============================================================================

CONCEPT_MAP_PROMPT = (
    "You are an expert in semantic modeling. Extract a concept map from the text, focusing on "
    "definitions, terminologies, and their hierarchical or associative relationships.\n\n"
    "Guidelines:\n"
    "- Identify core terms and provide their precise definitions based on the text.\n"
    "- Use standard semantic relations like 'is-a' (inheritance) or 'part-of' (composition).\n"
    "- Capture illustrative examples if mentioned."
)

CONCEPT_MAP_NODE_PROMPT = (
    "Extract all foundational concepts and technical terms from the text. "
    "For each concept, provide its term, a precise definition, a list of key attributes, "
    "and any specific examples mentioned in the source."
)

CONCEPT_MAP_EDGE_PROMPT = (
    "Establish semantic relationships between the provided concepts. "
    "Focus on hierarchical taxonomies (is-a, part-of) and functional associations (used-for, instance-of). "
    "Ensure edges logically connect the defined concepts."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class ConceptMap(AutoGraph[Concept, ConceptRelation]):
    """
    A template for building concept maps and taxonomies.
    
    Ideal for structured learning, technical documentation, and glossary extraction.
    It focuses on definitions, semantic categories, and hierarchical relationships.
    
    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # Initialize the template
        >>> cm = ConceptMap(llm_client=llm, embedder=embedder)
        >>> # Extract taxonomy from text
        >>> text = "Machine Learning is a subset of Artificial Intelligence that uses data to learn."
        >>> cm.feed_text(text)
        >>> print(cm.edges)  # Output shows: Machine Learning --(is a)--> Artificial Intelligence
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
        Initialize the ConceptMap template.

        Args:
            llm_client: The language model client used for extraction.
            embedder: The embedding model used for concept deduplication and indexing.
            extraction_mode: The strategy for extraction:
                - "one_stage": Extract nodes and edges simultaneously (faster).
                - "two_stage": Extract nodes first, then edges (higher accuracy).
            chunk_size: Maximum number of characters per text chunk.
            chunk_overlap: Number of characters to overlap between chunks.
            max_workers: Maximum number of parallel workers for processing.
            verbose: If True, prints detailed progress logs.
            **kwargs: Additional arguments passed to the AutoGraph constructor.
        """
        super().__init__(
            node_schema=Concept,
            edge_schema=ConceptRelation,
            node_key_extractor=lambda x: x.term.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.relation_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CONCEPT_MAP_PROMPT,
            prompt_for_node_extraction=CONCEPT_MAP_NODE_PROMPT,
            prompt_for_edge_extraction=CONCEPT_MAP_EDGE_PROMPT,
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
        def node_label_extractor(node: Concept) -> str:
            return f"{ node.term }"
    
        def edge_label_extractor(edge: ConceptRelation) -> str:
            return f"{ edge.source }"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
