"""Financial Data Temporal Graph - Tracks financial metrics across reporting periods.

Extracts financial entities (companies, segments, accounts) and their quantitative
relationships over time from SEC filings, enabling multi-period trend analysis,
segment-level tracking, and cross-period financial comparison.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class FinancialDataEntity(BaseModel):
    """
    A financial entity appearing in SEC filings: a company, business segment,
    or financial metric / line item.
    """

    name: str = Field(
        description="Canonical name of the entity (e.g., 'Apple Inc.', 'Cloud Services', 'Total Revenue', 'Net Income')."
    )
    entity_type: str = Field(
        description="Type: 'Company', 'Segment', 'FinancialMetric', 'AccountItem', 'ExternalFactor'."
    )
    description: Optional[str] = Field(
        None,
        description="Brief context (e.g., 'Consumer electronics segment', 'GAAP revenue recognition').",
    )


class FinancialDataEdge(BaseModel):
    """
    A temporal financial relationship linking an entity to a metric or linking
    metrics to each other, always anchored to a specific reporting period.
    """

    source: str = Field(
        description="The reporting entity or contributing factor (e.g., 'Apple Inc.', 'Services Segment')."
    )
    target: str = Field(
        description="The financial metric or account item (e.g., 'Revenue', 'Operating Income')."
    )
    relationship: str = Field(
        description="Type: 'Reported', 'Contributed', 'Derived', 'YoY Change', 'Ratio', 'Impacted By'."
    )
    value: Optional[str] = Field(
        None,
        description="Reported amount or percentage (e.g., '$394.3 billion', '+7.8%', '45.6%').",
    )
    unit: Optional[str] = Field(
        None,
        description="Unit or currency if distinguishable (e.g., 'USD millions', 'percentage').",
    )
    fiscal_period: Optional[str] = Field(
        None,
        description="Fiscal period label (e.g., 'FY2024', 'Q3 2024', 'Year ended Dec 31, 2024').",
    )
    start_timestamp: Optional[str] = Field(
        None,
        description="Start date of the reporting period (e.g., '2024-01-01', 'January 1, 2024').",
    )
    end_timestamp: Optional[str] = Field(
        None,
        description="End date of the reporting period (e.g., '2024-12-31', 'December 31, 2024').",
    )
    description: Optional[str] = Field(
        None,
        description="Additional context such as comparison notes, restatement flags, or accounting treatment.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a senior financial analyst specializing in multi-period SEC filing analysis. "
    "Extract financial entities and their quantitative relationships over time from the text.\n\n"
    "Rules:\n"
    "- Identify companies, business segments, and financial metrics/account items as entities.\n"
    "- For each reported figure, create an edge linking the reporting entity to the metric "
    "with the exact value and fiscal period.\n"
    "- Capture year-over-year changes, derived ratios, and segment contributions as separate edges.\n"
    "- Preserve exact dollar amounts and units as stated in the source.\n"
    "- Assign fiscal_period labels consistently (e.g., 'FY2024', 'Q3 2024').\n"
    "- Extract comparative data across multiple periods when available.\n"
    "- DO NOT compute values not explicitly stated in the text."
)

_NODE_PROMPT = (
    "You are a senior financial analyst. Extract all financial entities (Nodes) from the text.\n\n"
    "Extraction Rules:\n"
    "- Identify the filing company and any subsidiaries or related entities.\n"
    "- Identify business segments or geographic regions mentioned.\n"
    "- Identify financial metrics and account items (Revenue, Net Income, EPS, Total Assets, etc.).\n"
    "- Identify external factors explicitly mentioned as influencing financials (e.g., 'FX headwinds', 'Tariff impact').\n"
    "- Classify each entity by type: Company, Segment, FinancialMetric, AccountItem, ExternalFactor.\n"
    "- DO NOT extract dates, time periods, or numeric values as entities."
)

_EDGE_PROMPT = (
    "You are a senior financial analyst. Given the entities, extract all financial data relationships (Edges) "
    "with their temporal context.\n\n"
    "Extraction Rules:\n"
    "- For each reported figure, connect the reporting entity/segment to the relevant financial metric.\n"
    "- Include the exact value, unit, and fiscal period for every edge.\n"
    "- Extract year-over-year changes as separate edges (e.g., source='Revenue', target='Revenue Growth', "
    "relationship='YoY Change', value='+7.8%').\n"
    "- Extract segment contributions (e.g., source='Services', target='Revenue', "
    "relationship='Contributed', value='$85.2B').\n"
    "- Extract derived ratios explicitly stated (e.g., source='Gross Profit', target='Gross Margin', "
    "relationship='Ratio', value='45.6%').\n"
    "- Assign start_timestamp and end_timestamp based on the fiscal period boundaries.\n"
    "- Only create edges between nodes that exist in the provided entity list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class FinancialDataTemporalGraph(
    AutoTemporalGraph[FinancialDataEntity, FinancialDataEdge]
):
    """
    Applicable to: SEC 10-K Annual Reports, 10-Q Quarterly Reports, 20-F Foreign Filings,
    Annual Reports with multi-period financial statements, Segment disclosures.

    Template for building a temporal knowledge graph of financial data from SEC filings.
    Unlike FilingFinancialSnapshot (a flat single-period extraction), this template
    preserves the **time dimension** — tracking how revenue, margins, segment contributions,
    and other metrics evolve across reporting periods. It models companies, segments,
    and financial metrics as nodes, and connects them through temporally-anchored edges
    carrying exact values and fiscal period labels.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> graph = FinancialDataTemporalGraph(llm_client=llm, embedder=embedder)
        >>> filing = "For FY2024, Apple reported revenue of $394.3B, up 7.8% from $365.8B in FY2023..."
        >>> graph.feed_text(filing)
        >>> graph.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: str = "2024-01-01",
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize the Financial Data Temporal Graph template.

        Args:
            llm_client (BaseChatModel): The LLM for financial data extraction.
            embedder (Embeddings): Embedding model for deduplication and search.
            observation_time (str): Reference date for resolving relative time expressions.
            extraction_mode (str): "one_stage" or "two_stage" (default: "two_stage").
            chunk_size (int): Max characters per text chunk.
            chunk_overlap (int): Overlap between consecutive chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoTemporalGraph.
        """
        super().__init__(
            node_schema=FinancialDataEntity,
            edge_schema=FinancialDataEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}|{x.relationship.lower()}|{x.target.strip().lower()}"
            ),
            time_in_edge_extractor=lambda x: x.fiscal_period or x.start_timestamp or "",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
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
        Visualize the financial data temporal graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of data edges to retrieve. Default 3.
            top_k_nodes_for_chat (int): Entities for chat context. Default 3.
            top_k_edges_for_chat (int): Data edges for chat context. Default 3.
        """

        def node_label_extractor(node: FinancialDataEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: FinancialDataEdge) -> str:
            parts = [edge.relationship]
            if edge.value:
                parts.append(edge.value)
            if edge.fiscal_period:
                parts.append(f"[{edge.fiscal_period}]")
            elif edge.start_timestamp:
                parts.append(f"[{edge.start_timestamp}]")
            return " ".join(parts)

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
