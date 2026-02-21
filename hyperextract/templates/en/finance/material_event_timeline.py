"""Material Event Timeline - Chronologically extracts material events from 8-K filings.

Extracts executive changes, M&A announcements, restatements, and other material events
with temporal ordering for event-driven analysis and regulatory monitoring.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class MaterialEventEntity(BaseModel):
    """
    An entity involved in a material corporate event.
    """

    name: str = Field(
        description="Name of the entity (e.g., company name, executive name, regulatory body)."
    )
    entity_type: str = Field(
        description="Type: 'Company', 'Executive', 'Regulator', 'Counterparty', 'Subsidiary', 'Auditor'."
    )
    description: Optional[str] = Field(
        None, description="Role or context (e.g., 'CEO', 'Acquiring Company', 'SEC')."
    )


class MaterialEventEdge(BaseModel):
    """
    A material event linking entities with temporal context.
    """

    source: str = Field(description="The acting entity name.")
    target: str = Field(description="The affected entity name.")
    event_type: str = Field(
        description="Type: 'Executive Appointment', 'Executive Departure', 'Acquisition', 'Divestiture', "
        "'Restatement', 'Bankruptcy', 'Delisting', 'Material Agreement', 'Dividend Declaration', "
        "'Stock Split', 'Regulatory Action'."
    )
    start_timestamp: Optional[str] = Field(
        None,
        description="Date the event occurred or was announced (e.g., '2024-03-15', 'March 15, 2024').",
    )
    end_timestamp: Optional[str] = Field(
        None,
        description="End date if applicable (e.g., effective date, closing date).",
    )
    description: Optional[str] = Field(
        None,
        description="Details of the material event including financial terms, conditions, or regulatory context.",
    )
    sec_item: Optional[str] = Field(
        None,
        description="8-K Item number (e.g., 'Item 5.02', 'Item 1.01', 'Item 2.01').",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a regulatory filing analyst specializing in 8-K current reports and material event disclosures. "
    "Extract entities involved in material events and the temporal relationships between them.\n\n"
    "Rules:\n"
    "- Identify companies, executives, regulators, and counterparties involved.\n"
    "- Extract each material event with its specific date(s).\n"
    "- Classify events by their 8-K Item number when available.\n"
    "- Capture financial terms, conditions, and regulatory context.\n"
    "- Maintain chronological accuracy."
)

_NODE_PROMPT = (
    "You are a regulatory filing analyst. Extract all entities (Nodes) involved in material events.\n\n"
    "Extraction Rules:\n"
    "- Identify companies, executives, regulatory bodies, auditors, and counterparties.\n"
    "- Classify each entity by type.\n"
    "- Capture role descriptions.\n"
    "- DO NOT extract events or relationships at this stage."
)

_EDGE_PROMPT = (
    "You are a regulatory filing analyst. Given the entities, extract all material events (Edges) with dates.\n\n"
    "Extraction Rules:\n"
    "- Connect entities through material events.\n"
    "- Extract specific dates for each event.\n"
    "- Classify by event type and 8-K Item number.\n"
    "- Capture financial terms and conditions.\n"
    "- Only create edges between nodes that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class MaterialEventTimeline(AutoTemporalGraph[MaterialEventEntity, MaterialEventEdge]):
    """
    Applicable to: SEC 8-K Current Reports, Material Event Disclosures,
    Press Releases accompanying 8-K filings, Proxy Statements (DEF 14A).

    Template for chronologically extracting material corporate events from 8-K filings
    and related disclosures. Enables event-driven analysis, regulatory monitoring,
    and corporate governance tracking.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> timeline = MaterialEventTimeline(llm_client=llm, embedder=embedder)
        >>> filing = "Item 5.02: On March 15, 2024, the Board appointed John Smith as CEO..."
        >>> timeline.feed_text(filing)
        >>> timeline.show()
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
        Initialize the Material Event Timeline template.

        Args:
            llm_client (BaseChatModel): The LLM for event extraction.
            embedder (Embeddings): Embedding model for deduplication.
            observation_time (str): Reference time for resolving relative dates.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoTemporalGraph.
        """
        super().__init__(
            node_schema=MaterialEventEntity,
            edge_schema=MaterialEventEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}|{x.event_type.lower()}|{x.target.strip().lower()}"
            ),
            time_in_edge_extractor=lambda x: x.start_timestamp or "",
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
        Visualize the material event timeline using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of events to retrieve. Default 3.
            top_k_nodes_for_chat (int): Entities for chat context. Default 3.
            top_k_edges_for_chat (int): Events for chat context. Default 3.
        """

        def node_label_extractor(node: MaterialEventEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: MaterialEventEdge) -> str:
            date = f" [{edge.start_timestamp}]" if edge.start_timestamp else ""
            return f"{edge.event_type}{date}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
