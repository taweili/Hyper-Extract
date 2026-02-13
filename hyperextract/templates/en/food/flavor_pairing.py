from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class FlavorComponent(BaseModel):
    """
    A food ingredient or flavor compound involved in pairing relationships.
    """

    name: str = Field(description="Name of food/ingredient/compound (e.g., 'Strawberry', 'Furaneol', 'Vanilla').")
    component_type: str = Field(
        description="Type: 'Ingredient', 'Chemical Compound', 'Flavor Note', 'Aroma'."
    )
    description: Optional[str] = Field(
        None, description="Additional details (e.g., chemical formula, source, sensory profile)."
    )


class FlavorRelationship(BaseModel):
    """
    A pairing or flavor relationship between two components.
    """

    source: str = Field(description="First component.")
    target: str = Field(description="Second component.")
    relationship_type: str = Field(
        description="Type: 'Contains', 'Pairs_Well', 'Conflicts', 'Complements', 'Shared_Flavor'."
    )
    pairing_mechanism: str = Field(
        description="Why they pair or connect (e.g., 'Shared sulfur compounds', 'Complementary sweetness', 'Similar volatile compounds')."
    )
    pairing_quality: Optional[str] = Field(
        None, description="Quality assessment (e.g., 'Strong', 'Moderate', 'Subtle', 'Surprising')."
    )
    culinary_context: Optional[str] = Field(
        None,
        description="In what culinary context they pair well (e.g., 'Sweet desserts', 'Savory broths', 'Asian cuisine').",
    )
    supporting_evidence: Optional[str] = Field(
        None,
        description="Scientific evidence or reference (e.g., 'Clinical taste panel study', 'Food Chemistry Journal').",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a food chemist and flavor scientist. Extract flavor components and their pairing "
    "relationships from food science literature and sensory evaluation reports.\n\n"
    "Rules:\n"
    "- Identify food ingredients, volatile compounds, and flavor molecules mentioned.\n"
    "- Extract flavor pairing relationships and the chemistry/science behind them.\n"
    "- Distinguish between complementary, conflicting, and surprising pairings.\n"
    "- Document the evidence basis (taste panel, chemical analysis, etc.)."
)

_NODE_PROMPT = (
    "You are a food chemist. Extract all flavor components and compounds (Nodes) from the text.\n\n"
    "Extraction Rules:\n"
    "- Identify food ingredients (Strawberry, Tomato) and flavor compounds (Furaneol, Vanillin).\n"
    "- Classify each as Ingredient, Chemical Compound, or Flavor Note.\n"
    "- Include sensory or chemical descriptors where provided.\n"
    "- DO NOT establish pairings or relationships at this stage."
)

_EDGE_PROMPT = (
    "You are a food chemist. Given the list of flavor components, extract their pairing and "
    "relationship connections (Edges).\n\n"
    "Extraction Rules:\n"
    "- Connect components that share flavor molecules or pair well culinarily.\n"
    "- Extract the scientific mechanism (shared compounds, complementary tastes).\n"
    "- Assess pairing quality and context (when/why they work together).\n"
    "- Include supporting evidence from research or sensory studies.\n"
    "- Only connect components that exist in the provided list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class FlavorPairingGraph(AutoGraph[FlavorComponent, FlavorRelationship]):
    """
    Applicable to: Food Chemistry Research Papers (journals like Food Chemistry, LWT),
    Sensory Evaluation Reports, Recipe Development Studies, Flavor Science Books,
    Culinary Science Databases, Molecular Gastronomy Guides.

    Template for extracting and mapping flavor and culinary science knowledge. Enables 
    understanding of ingredients' chemical similarities, predicting novel flavor combinations, 
    and supporting data-driven recipe development.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> flavors = FlavorPairingGraph(llm_client=llm, embedder=embedder)
        >>> paper = "Strawberries and tomatoes both contain furaneol, leading to surprising pairing potential..."
        >>> flavors.feed_text(paper)

        >>> flavors.show()
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
        Initialize the Flavor Pairing Graph template.

        Args:
            llm_client (BaseChatModel): The LLM for component and relationship extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoGraph.
        """
        super().__init__(
            node_schema=FlavorComponent,
            edge_schema=FlavorRelationship,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.relationship_type})-->{x.target.strip()}"
            ),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
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
    ) -> None:
        """
        Visualize the flavor pairing graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of components to retrieve. Default 3.
            top_k_edges_for_search (int): Number of relationships to retrieve. Default 3.
            top_k_nodes_for_chat (int): Components for chat context. Default 3.
            top_k_edges_for_chat (int): Relationships for chat context. Default 3.
        """

        def node_label_extractor(node: FlavorComponent) -> str:
            return f"{node.name} ({node.component_type})"

        def edge_label_extractor(edge: FlavorRelationship) -> str:
            quality = f" ({edge.pairing_quality})" if edge.pairing_quality else ""
            return f"{edge.relationship_type}{quality}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
