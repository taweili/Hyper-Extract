from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class RiskFactor(BaseModel):
    """
    A specific risk factor identified in corporate disclosure documents.
    """

    name: str = Field(
        description="Name or category of the risk (e.g., 'Supply Chain Disruption', 'Currency Fluctuation')."
    )
    category: str = Field(
        description="Risk category: 'Market', 'Operational', 'Regulatory', 'Reputational', 'Geopolitical'."
    )
    description: Optional[str] = Field(
        None, description="Detailed explanation of what the risk entails."
    )


class FinancialImpact(BaseModel):
    """
    A financial or business metric that can be adversely affected by risks.
    """

    name: str = Field(
        description="Financial metric or business area (e.g., 'Operating Margin', 'Revenue', 'Stock Price')."
    )
    metric_type: str = Field(
        description="Type: 'Revenue', 'Profitability', 'Liquidity', 'Valuation', 'Reputation'."
    )


class RiskTransmissionEdge(BaseModel):
    """
    Represents the causal link from a risk factor to a financial impact.
    """

    source: str = Field(description="The risk factor name.")
    target: str = Field(description="The affected financial metric or business area.")
    impact_description: str = Field(
        description="How the risk could adversely affect the target (e.g., 'could reduce', 'may increase')."
    )
    likelihood: str = Field(
        description="Probability characterization: 'Possible', 'Probable', 'Uncertain', 'Remote'."
    )
    severity: str = Field(
        description="Severity level: 'Material', 'Significant', 'Severe', 'Catastrophic'."
    )
    mitigation: Optional[str] = Field(
        None, description="Any disclosed mitigation strategies or controls."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a financial risk analyst specializing in corporate risk disclosure. Extract risk factors and their "
    "transmission paths to financial impacts from SEC filings and prospectuses.\n\n"
    "Rules:\n"
    "- Identify explicit risk factors mentioned in Item 1A or similar risk disclosure sections.\n"
    "- For each risk, extract the explicit causal links to financial/operational impacts.\n"
    "- Use the exact severity and likelihood language from the source text.\n"
    "- Capture any disclosed mitigation strategies."
)

_NODE_PROMPT = (
    "You are a financial risk analyst. Extract all risk factors and financial metrics (Nodes) from the text.\n\n"
    "Extraction Rules:\n"
    "- Identify and categorize risk factors (Market, Operational, Regulatory, Reputational, Geopolitical).\n"
    "- Identify financial or operational metrics that could be affected (Revenue, Margin, Valuation).\n"
    "- Use exact names and descriptions from the source text.\n"
    "- DO NOT establish the causal relationships between risks and impacts at this stage."
)

_EDGE_PROMPT = (
    "You are a financial risk analyst. Given the list of risk factors and financial metrics, extract the causal "
    "transmission paths (Edges).\n\n"
    "Extraction Rules:\n"
    "- Connect each risk factor to the specific financial metrics it could adversely affect.\n"
    "- Extract the exact impact description using language like 'could have a material adverse effect on'.\n"
    "- Classify the likelihood and severity using disclosed characterizations.\n"
    "- Document any mitigation strategies mentioned in conjunction with the risk.\n"
    "- Only create edges between nodes that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class RiskAssessmentGraph(AutoGraph[RiskFactor, RiskTransmissionEdge]):
    """
    Applicable to: SEC 10-K/10-Q Item 1A (Risk Factors), Prospectus Risk Sections (S-1), 
    Debt Rating Reports, Risk Disclosure Filings.

    Template for systematically extracting and mapping corporate risk factors to their 
    financial impacts. Enables structured risk monitoring and comparative analysis across 
    multiple filings.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> risk_graph = RiskAssessmentGraph(llm_client=llm, embedder=embedder)
        >>> filing_text = "Item 1A. Risk Factors: Currency fluctuations could materially impact our margins..."
        >>> risk_graph.feed_text(filing_text)
        >>> risk_graph.show()
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
        Initialize the Risk Assessment Graph template.

        Args:
            llm_client (BaseChatModel): The LLM for risk and impact extraction.
            embedder (Embeddings): Embedding model for entity deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoGraph.
        """
        super().__init__(
            node_schema=RiskFactor,
            edge_schema=RiskTransmissionEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.likelihood}/{x.severity})-->{x.target.strip()}"
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
        Visualize the risk transmission graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of risk nodes to retrieve. Default 3.
            top_k_edges_for_search (int): Number of transmission paths to retrieve. Default 3.
            top_k_nodes_for_chat (int): Nodes for chat context. Default 3.
            top_k_edges_for_chat (int): Edges for chat context. Default 3.
        """

        def node_label_extractor(node: RiskFactor) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: RiskTransmissionEdge) -> str:
            return f"[{edge.likelihood}/{edge.severity}]"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
