from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class ManufacturingEntity(BaseModel):
    """An entity in the automotive supply chain or production line (Supplier, Factory, Assembly Step)."""
    name: str = Field(description="Name of the company, factory, or production process.")
    category: str = Field(
        description="Category: 'Supplier', 'Factory', 'Process', 'Material', 'Quality Check'."
    )
    specification: Optional[str] = Field(description="Production capacity, certifications, or lead times.")

class SupplyChainRelation(BaseModel):
    """Connectivity between players and steps in automotive manufacturing."""
    source: str = Field(description="The upstream supplier or process.")
    target: str = Field(description="The downstream factory or product.")
    relation_type: str = Field(
        description="Type: 'Supplies to', 'Assembled at', 'Processed by', 'Certified for'."
    )
    logistics_details: Optional[str] = Field(description="Incoterms, transit times, or volume commitments.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

MFG_GRAPH_PROMPT = (
    "You are a supply chain analyst for a major auto manufacturer. Extract the manufacturing and supply chain graph.\n\n"
    "Guidelines:\n"
    "- Identify the tiers of suppliers (Tier 1, Tier 2) and the components they provide.\n"
    "- Map the assembly sequence from raw materials to the final vehicle roll-out.\n"
    "- Capture geographic locations of factories and specific logistics constraints."
)

MFG_NODE_PROMPT = (
    "Extract suppliers, manufacturing plants, and critical production steps. Note their roles in the vehicle production cycle."
)

MFG_EDGE_PROMPT = (
    "Define the material and process flow. Connect suppliers to assembly plants and plants to the final car delivery."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class AutomotiveMfgGraph(AutoGraph[ManufacturingEntity, SupplyChainRelation]):
    """
    Template for automotive production lines, supply chain logistics, and supplier management.
    
    Helps visualize dependencies in the global automotive manufacturing ecosystem.
    
    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI()
        >>> embedder = OpenAIEmbeddings()
        >>> graph = AutomotiveMfgGraph(llm_client=llm, embedder=embedder)
        >>> text = "CATL supplies battery cells to the Tesla Gigafactory in Berlin for Model Y assembly."
        >>> graph.feed_text(text)
        >>> print(graph.edges) # Supply chain flow
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
        Initialize the AutomotiveMfgGraph template.

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
            node_schema=ManufacturingEntity,
            edge_schema=SupplyChainRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.relation_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=MFG_GRAPH_PROMPT,
            prompt_for_node_extraction=MFG_NODE_PROMPT,
            prompt_for_edge_extraction=MFG_EDGE_PROMPT,
            **kwargs
        )
