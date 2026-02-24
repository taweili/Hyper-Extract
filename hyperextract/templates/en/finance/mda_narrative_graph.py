"""MD&A Narrative Graph - Extracts causal relationships from Management Discussion & Analysis.

Maps causal chains from business drivers to financial outcomes as described in MD&A sections
of SEC filings (e.g., "Supply chain disruption -> Revenue decline -> Margin compression").
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class MDAFactor(BaseModel):
    """
    A business driver, financial outcome, or operational factor mentioned in MD&A.
    """

    name: str = Field(
        description="Name of the factor (e.g., 'Supply Chain Disruption', 'Revenue Growth', 'Margin Compression')."
    )
    factor_type: str = Field(
        description="Type: 'Business Driver', 'Financial Outcome', 'Operational Factor', 'Strategic Initiative', 'External Factor'."
    )
    description: Optional[str] = Field(
        None,
        description="Management's explanation or context for this factor.",
    )


class MDANarrativeEdge(BaseModel):
    """
    A causal or explanatory relationship between two MD&A factors.
    """

    source: str = Field(description="The cause or driver factor name.")
    target: str = Field(description="The effect or outcome factor name.")
    relationship_type: str = Field(
        description="Type: 'Caused', 'Contributed To', 'Offset By', 'Resulted In', 'Led To', 'Mitigated By'."
    )
    magnitude: Optional[str] = Field(
        None,
        description="Quantified impact if mentioned (e.g., 'increased by $2.3B', '300 basis points').",
    )
    management_attribution: Optional[str] = Field(
        None,
        description="Management's own causal explanation verbatim or paraphrased.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a financial analyst specializing in MD&A (Management Discussion & Analysis) sections of SEC filings. "
    "Extract business drivers, financial outcomes, and the causal relationships management describes between them.\n\n"
    "Rules:\n"
    "- Identify factors management discusses: revenue drivers, cost pressures, strategic changes, external forces.\n"
    "- Extract causal chains as management presents them (e.g., 'increased demand led to revenue growth').\n"
    "- Capture quantified impacts when stated.\n"
    "- Preserve management's attribution language."
)

_NODE_PROMPT = (
    "You are a financial analyst. Extract all business drivers, financial outcomes, and operational factors (Nodes) "
    "from the MD&A text.\n\n"
    "Extraction Rules:\n"
    "- Identify revenue drivers, cost factors, strategic initiatives, and external forces.\n"
    "- Identify financial outcomes (revenue changes, margin shifts, cash flow impacts).\n"
    "- Classify each factor by type.\n"
    "- DO NOT establish causal relationships at this stage."
)

_EDGE_PROMPT = (
    "You are a financial analyst. Given the list of MD&A factors, extract the causal and explanatory "
    "relationships (Edges) that management describes.\n\n"
    "Extraction Rules:\n"
    "- Connect causes to effects as management presents them.\n"
    "- Classify the relationship type (Caused, Contributed To, Offset By, etc.).\n"
    "- Extract quantified magnitude when available.\n"
    "- Capture management's own causal explanation.\n"
    "- Only create edges between nodes that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class MDANarrativeGraph(AutoGraph[MDAFactor, MDANarrativeEdge]):
    """
    Applicable to: SEC 10-K/10-Q Item 7 (Management Discussion & Analysis),
    Annual Report MD&A sections, Interim Management Reports.

    Template for extracting causal relationships from Management Discussion & Analysis
    sections. Maps how management explains business performance drivers and their
    financial impacts, enabling narrative analytics and driver attribution.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> mda = MDANarrativeGraph(llm_client=llm, embedder=embedder)
        >>> text = "Revenue increased 12% driven by strong demand in our cloud segment..."
        >>> mda.feed_text(text)
        >>> mda.show()
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
        Initialize the MD&A Narrative Graph template.

        Args:
            llm_client (BaseChatModel): The LLM for causal relationship extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoGraph.
        """
        super().__init__(
            node_schema=MDAFactor,
            edge_schema=MDANarrativeEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}--({x.relationship_type})-->{x.target.strip().lower()}"
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
        Visualize the MD&A narrative graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of factors to retrieve. Default 3.
            top_k_edges_for_search (int): Number of causal links to retrieve. Default 3.
            top_k_nodes_for_chat (int): Factors for chat context. Default 3.
            top_k_edges_for_chat (int): Causal links for chat context. Default 3.
        """

        def node_label_extractor(node: MDAFactor) -> str:
            return f"{node.name} ({node.factor_type})"

        def edge_label_extractor(edge: MDANarrativeEdge) -> str:
            mag = f" [{edge.magnitude}]" if edge.magnitude else ""
            return f"{edge.relationship_type}{mag}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
