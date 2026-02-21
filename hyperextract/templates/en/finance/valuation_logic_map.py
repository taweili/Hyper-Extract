"""Valuation Logic Map - Maps causal chains driving stock performance.

Extracts the logical chain from business drivers to valuation conclusions as
presented in equity research reports (e.g., New Market -> Growth -> Multiple Expansion).
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class ValuationDriver(BaseModel):
    """
    A factor in the analyst's valuation logic chain.
    """

    name: str = Field(
        description="Name of the valuation driver (e.g., 'Market Share Gains', 'Multiple Expansion', 'DCF Assumption')."
    )
    driver_type: str = Field(
        description="Type: 'Fundamental', 'Valuation Metric', 'Growth Driver', 'Comparable', 'Discount Rate', 'Terminal Value'."
    )
    value: Optional[str] = Field(
        None,
        description="Quantified value or metric (e.g., '25x forward P/E', 'WACC 9.5%', '$15B TAM').",
    )
    description: Optional[str] = Field(
        None,
        description="Analyst's explanation of this driver's role in the valuation.",
    )


class ValuationEdge(BaseModel):
    """
    A causal link in the analyst's valuation logic.
    """

    source: str = Field(description="The cause or input driver name.")
    target: str = Field(description="The effect or output driver name.")
    logic: str = Field(
        description="The analyst's reasoning connecting source to target "
        "(e.g., 'higher cloud adoption drives recurring revenue growth')."
    )
    direction: str = Field(
        description="Impact direction: 'Positive', 'Negative', 'Neutral'."
    )
    confidence: Optional[str] = Field(
        None,
        description="Analyst's conviction level: 'High', 'Medium', 'Low'.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an equity research analyst. Extract the valuation logic chain from this research report: "
    "the causal reasoning from business fundamentals through to valuation conclusions.\n\n"
    "Rules:\n"
    "- Identify fundamental drivers, growth catalysts, and valuation metrics.\n"
    "- Extract the causal chain from business drivers to target price.\n"
    "- Capture the analyst's specific reasoning at each link.\n"
    "- Note impact direction and conviction level."
)

_NODE_PROMPT = (
    "You are an equity research analyst. Extract all valuation drivers and metrics (Nodes).\n\n"
    "Extraction Rules:\n"
    "- Identify fundamental drivers (revenue growth, market share, TAM).\n"
    "- Identify valuation metrics (P/E, EV/EBITDA, DCF, comparable multiples).\n"
    "- Capture quantified values when stated.\n"
    "- DO NOT establish causal links at this stage."
)

_EDGE_PROMPT = (
    "You are an equity research analyst. Given the valuation drivers, extract the logical "
    "reasoning chain (Edges) that connects them.\n\n"
    "Extraction Rules:\n"
    "- Connect business drivers to financial outcomes to valuation conclusions.\n"
    "- Capture the specific reasoning at each link.\n"
    "- Note whether each link is positive, negative, or neutral.\n"
    "- Only create edges between nodes that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class ValuationLogicMap(AutoGraph[ValuationDriver, ValuationEdge]):
    """
    Applicable to: Equity Research Reports, Initiation Reports, Valuation Analysis,
    Sum-of-Parts Analyses, DCF Model Summaries.

    Template for mapping the causal chains in an analyst's valuation logic. Connects
    business fundamentals to growth drivers to valuation metrics to target price,
    enabling investment strategy mapping and thesis comparison.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> valuation = ValuationLogicMap(llm_client=llm, embedder=embedder)
        >>> report = "Cloud adoption drives recurring revenue, justifying a 30x forward P/E..."
        >>> valuation.feed_text(report)
        >>> valuation.show()
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
        Initialize the Valuation Logic Map template.

        Args:
            llm_client (BaseChatModel): The LLM for valuation logic extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoGraph.
        """
        super().__init__(
            node_schema=ValuationDriver,
            edge_schema=ValuationEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}--({x.direction})-->{x.target.strip().lower()}"
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
        Visualize the valuation logic map using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of drivers to retrieve. Default 3.
            top_k_edges_for_search (int): Number of logic links to retrieve. Default 3.
            top_k_nodes_for_chat (int): Drivers for chat context. Default 3.
            top_k_edges_for_chat (int): Logic links for chat context. Default 3.
        """

        def node_label_extractor(node: ValuationDriver) -> str:
            val = f": {node.value}" if node.value else ""
            return f"{node.name}{val}"

        def edge_label_extractor(edge: ValuationEdge) -> str:
            return f"[{edge.direction}] {edge.logic[:60]}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
