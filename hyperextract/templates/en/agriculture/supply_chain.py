from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class SupplyEntity(BaseModel):
    """An actor or asset in the agri-supply chain (e.g., Farm, Warehouse, Processor, Logistics, Retailer)."""
    name: str = Field(description="Name of the organization, facility, or batch ID.")
    category: str = Field(
        description="Category: 'Producer/Farm', 'Processor', 'Distributor', 'Logistics Provider', 'Retailer', 'Batch/Product'."
    )
    location_or_cert: Optional[str] = Field(description="Geographic location or quality certification (e.g., Organic, ISO).")

class SupplyFlow(BaseModel):
    """The flow of products or information between supply chain actors."""
    source: str = Field(description="The starting entity (sender/producer).")
    target: str = Field(description="The receiving entity (buyer/processor).")
    flow_type: str = Field(
        description="Type: 'Ships to', 'Processes', 'Sells to', 'Tests', 'Certifies'."
    )
    specification: Optional[str] = Field(description="Quantity, transportation mode, or quality check result.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

AGRI_SUPPLY_CHAIN_PROMPT = (
    "You are a supply chain analyst specializing in agriculture. Extract a traceability and logistics graph.\n\n"
    "Guidelines:\n"
    "- Identify all actors involved from the farm to the fork (Producer, Processor, Distributor).\n"
    "- Map the flow of specific batches or products through various stages.\n"
    "- Capture quality checks, certifications, and transportation modes mentioned in the text."
)

AGRI_SUPPLY_CHAIN_NODE_PROMPT = (
    "Extract supply chain entities: identify specific farms, factories, logistics hubs, and retailers. "
    "Note their roles, locations, and any quality certifications mentioned."
)

AGRI_SUPPLY_CHAIN_EDGE_PROMPT = (
    "Establish the movement of goods and information. Connect producers to processors, and processors to retailers. "
    "Use specific relation types like 'Ships to' or 'Processes', and include details like transport methods or quantities."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class AgriSupplyChain(AutoGraph[SupplyEntity, SupplyFlow]):
    """
    Template for agricultural traceability, logistics mapping, and supply chain transparency.
    
    Ideal for food safety tracking, logistics optimization, and trade analysis.
    
    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> graph = AgriSupplyChain(llm_client=llm, embedder=embedder)
        >>> text = "Batch #A102 was shipped from GreenFarm (Organic) to CentralProcessor via cold-chain truck."
        >>> graph.feed_text(text)
        >>> print(graph.edges) # Extracted logistics flow
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
        Initialize the AgriSupplyChain template.

        Args:
            llm_client: The language model client for extraction.
            embedder: The embedding model for deduplication.
            extraction_mode: "one_stage" or "two_stage".
            chunk_size: Max characters per chunk.
            chunk_overlap: Overlap between chunks.
            max_workers: Parallel processing workers.
            verbose: Enable progress logging.
            **kwargs: Extra arguments for AutoGraph.
        """
        super().__init__(
            node_schema=SupplyEntity,
            edge_schema=SupplyFlow,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.flow_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=AGRI_SUPPLY_CHAIN_PROMPT,
            prompt_for_node_extraction=AGRI_SUPPLY_CHAIN_NODE_PROMPT,
            prompt_for_edge_extraction=AGRI_SUPPLY_CHAIN_EDGE_PROMPT,
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
        def node_label_extractor(node: SupplyEntity) -> str:
            info = f" ({ node.category })" if getattr(node, "category", None) else ""
            return f"{ node.name }{info}"
    
        def edge_label_extractor(edge: SupplyFlow) -> str:
            info = f" ({ edge.specification })" if getattr(edge, "specification", None) else ""
            return f"{ edge.source }{info}"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
