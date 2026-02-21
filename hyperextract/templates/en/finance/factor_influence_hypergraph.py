"""Factor Influence Hypergraph - Models multi-factor relationships in equity analysis.

Models complex relationships between macro factors, industry trends, and company
metrics as hyperedges connecting multiple factors simultaneously.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class InvestmentFactor(BaseModel):
    """
    A factor in multi-factor investment analysis.
    """

    name: str = Field(
        description="Name of the factor (e.g., 'GDP Growth', 'Semiconductor Cycle', 'Cloud Revenue')."
    )
    factor_level: str = Field(
        description="Level: 'Macro', 'Industry', 'Company', 'Technical'."
    )
    current_reading: Optional[str] = Field(
        None,
        description="Current value or state (e.g., '3.2% YoY', 'Upcycle Phase', 'Accelerating').",
    )
    description: Optional[str] = Field(
        None, description="Explanation of this factor's significance."
    )


class FactorInteraction(BaseModel):
    """
    A multi-factor interaction where several factors jointly influence an outcome.
    """

    interaction_name: str = Field(
        description="Descriptive name (e.g., 'AI Capex Multiplier Effect', 'Rate-Sensitive Rotation')."
    )
    participating_factors: List[str] = Field(
        description="Names of all factors involved in this interaction."
    )
    interaction_type: str = Field(
        description="Type: 'Reinforcing', 'Offsetting', 'Conditional', 'Cascading', 'Threshold'."
    )
    outcome: str = Field(
        description="The combined outcome or effect (e.g., 'Accelerated revenue growth for cloud names')."
    )
    mechanism: Optional[str] = Field(
        None,
        description="How the factors interact to produce the outcome.",
    )
    confidence: Optional[str] = Field(
        None,
        description="Analyst's confidence in this interaction: 'High', 'Medium', 'Low'.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a quantamental research analyst. Extract investment factors and their multi-factor "
    "interactions from this research report.\n\n"
    "Rules:\n"
    "- Identify macro, industry, and company-level factors.\n"
    "- Extract complex interactions where multiple factors jointly produce an outcome.\n"
    "- A hyperedge connects ALL participating factors, not just pairs.\n"
    "- Capture the mechanism and outcome of each interaction."
)

_NODE_PROMPT = (
    "You are a quantamental research analyst. Extract all investment factors (Nodes).\n\n"
    "Extraction Rules:\n"
    "- Identify macro indicators, industry metrics, and company KPIs.\n"
    "- Capture current values or readings.\n"
    "- Classify each factor by level.\n"
    "- DO NOT extract interactions at this stage."
)

_EDGE_PROMPT = (
    "You are a quantamental research analyst. Given the factors, extract multi-factor "
    "interactions (Hyperedges) where multiple factors jointly influence outcomes.\n\n"
    "Extraction Rules:\n"
    "- Each hyperedge should connect 2 or more factors.\n"
    "- Describe the interaction mechanism and outcome.\n"
    "- Classify the interaction type.\n"
    "- Only reference factors that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class FactorInfluenceHypergraph(AutoHypergraph[InvestmentFactor, FactorInteraction]):
    """
    Applicable to: Multi-Factor Research Reports, Quantamental Analysis,
    Macro Strategy Notes, Cross-Asset Research, Factor Attribution Studies.

    Template for modeling complex multi-factor relationships in equity analysis.
    Uses hyperedges to capture interactions where multiple factors jointly influence
    an outcome, going beyond simple pairwise relationships.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> factors = FactorInfluenceHypergraph(llm_client=llm, embedder=embedder)
        >>> report = "Rising rates combined with strong GDP and AI capex create a rotation into quality growth..."
        >>> factors.feed_text(report)
        >>> factors.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize the Factor Influence Hypergraph template.

        Args:
            llm_client (BaseChatModel): The LLM for factor extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoHypergraph.
        """
        super().__init__(
            node_schema=InvestmentFactor,
            edge_schema=FactorInteraction,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: x.interaction_name.strip().lower(),
            nodes_in_edge_extractor=lambda x: tuple(
                f.strip().lower() for f in x.participating_factors
            ),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
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
        Visualize the factor influence hypergraph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of factors to retrieve. Default 3.
            top_k_edges_for_search (int): Number of interactions to retrieve. Default 3.
            top_k_nodes_for_chat (int): Factors for chat context. Default 3.
            top_k_edges_for_chat (int): Interactions for chat context. Default 3.
        """

        def node_label_extractor(node: InvestmentFactor) -> str:
            reading = f": {node.current_reading}" if node.current_reading else ""
            return f"{node.name} [{node.factor_level}]{reading}"

        def edge_label_extractor(edge: FactorInteraction) -> str:
            return f"[{edge.interaction_type}] {edge.interaction_name}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
