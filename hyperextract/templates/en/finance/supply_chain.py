from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class SupplyEntity(BaseModel):
    """
    A participant in the supply chain (company, supplier, customer, distributor).
    """

    name: str = Field(description="Entity name (company or supplier).")
    entity_type: str = Field(
        description="Type: 'Customer', 'Supplier', 'Strategic Partner', 'Distributor', 'Our Company'."
    )
    jurisdiction: Optional[str] = Field(
        None, description="Geographic location or headquarters region."
    )
    notes: Optional[str] = Field(
        None, description="Additional details (e.g., 'Certified Organic', 'ISO Compliant')."
    )


class SupplyTransaction(BaseModel):
    """
    A supply chain relationship between entities.
    """

    source: str = Field(description="The supplier or upstream entity.")
    target: str = Field(description="The buyer or downstream entity.")
    transaction_type: str = Field(
        description="Type: 'Supply', 'Purchase', 'Distribution', 'Strategic Partnership'."
    )
    product_service: str = Field(
        description="What is being supplied or transacted (e.g., 'Lithium Chips', 'Logistics Services')."
    )
    dependency: str = Field(
        description="Dependency level: 'Critical', 'High', 'Moderate', 'Low'."
    )
    volume_percentage: Optional[str] = Field(
        None, description="Percentage of total supply/revenue if disclosed (e.g., '80%')."
    )
    geographic_origin: Optional[str] = Field(
        None, description="Source region or geopolitical consideration."
    )
    risks: Optional[str] = Field(
        None,
        description="Any disclosed risks or vulnerabilities (e.g., 'Single-source supplier', 'Tariff exposure').",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a supply chain analyst. Extract supply chain entities and their relationships "
    "from corporate filings and supply chain audits.\n\n"
    "Rules:\n"
    "- Identify key suppliers, customers, and strategic partners mentioned.\n"
    "- Extract transaction types and product/service descriptions.\n"
    "- Assess dependency levels based on disclosed volume or importance.\n"
    "- Document any geopolitical or regulatory risks."
)

_NODE_PROMPT = (
    "You are a supply chain analyst. Extract all supply chain participants (Nodes) from the text.\n\n"
    "Extraction Rules:\n"
    "- Identify companies, suppliers, customers, and distribution partners.\n"
    "- Classify each entity's role in the supply chain.\n"
    "- Note jurisdiction and any certifications or compliance notes.\n"
    "- DO NOT establish transaction relationships at this stage."
)

_EDGE_PROMPT = (
    "You are a supply chain analyst. Given the list of supply chain entities, extract the "
    "transaction relationships (Edges).\n\n"
    "Extraction Rules:\n"
    "- Connect supplier to buyer with the specific product/service being transacted.\n"
    "- Assess dependency level based on disclosed volume percentages or importance keywords.\n"
    "- Extract geographic origin and any disclosed risks (tariffs, single-source).\n"
    "- Only connect entities that exist in the provided list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class SupplyChainGraph(AutoGraph[SupplyEntity, SupplyTransaction]):
    """
    Applicable to: Business Overview sections in 10-K filings, Supplier Audit Reports,
    Supply Chain Resilience Disclosures (10-K Item 1A), ESG Reports, Vendor Management Documents.

    Template for mapping corporate supply chain dependencies and partnerships. Enables 
    identification of critical suppliers, geopolitical exposure, and supply chain resilience risks.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> supply_chain = SupplyChainGraph(llm_client=llm, embedder=embedder)
        >>> filing = "Supplier XYZ provides 70% of our components. We also depend on..."
        >>> supply_chain.feed_text(filing)
        >>> supply_chain.show()
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
        Initialize the Supply Chain Graph template.

        Args:
            llm_client (BaseChatModel): The LLM for entity and relationship extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoGraph.
        """
        super().__init__(
            node_schema=SupplyEntity,
            edge_schema=SupplyTransaction,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.product_service})-->{x.target.strip()}"
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
        Visualize the supply chain graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of relationships to retrieve. Default 3.
            top_k_nodes_for_chat (int): Entities for chat context. Default 3.
            top_k_edges_for_chat (int): Relationships for chat context. Default 3.
        """

        def node_label_extractor(node: SupplyEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: SupplyTransaction) -> str:
            vol = f" {edge.volume_percentage}" if edge.volume_percentage else ""
            return f"{edge.product_service}{vol} [{edge.dependency}]"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
