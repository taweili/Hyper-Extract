from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class MaintenanceItem(BaseModel):
    """A maintenance task or vehicle part (Oil Change, Brake Pad, Timing Belt)."""
    item_name: str = Field(description="Name of the part or maintenance service.")
    category: str = Field(description="Category: 'Fluid', 'Wearable Part', 'Inspection', 'Software'.")
    interval: Optional[str] = Field(description="Suggested mileage or time interval (e.g., 5,000 miles).")

class MaintenanceSequence(BaseModel):
    """The dependency or sequence of maintenance actions."""
    source: str = Field(description="Prerequisite component or initial state.")
    target: str = Field(description="Maintenance task or replacement part.")
    action: str = Field(description="Action: 'Replace', 'Inspect', 'Flush', 'Calibrate'.")
    precaution: Optional[str] = Field(description="Safety warnings or required tools.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

MAINTENANCE_GRAPH_PROMPT = (
    "You are a master mechanic and service consultant. Extract a vehicle maintenance and repair graph.\n\n"
    "Guidelines:\n"
    "- Identify specific maintenance items and parts mentioned in the manual or log.\n"
    "- Map the conditions that trigger maintenance (e.g., Mileage, Warning Light, Visual Inspection).\n"
    "- Link parts to their respective systems and required actions."
)

MAINTENANCE_NODE_PROMPT = (
    "Extract maintenance tasks, parts, and fluid types. Include recommended intervals if specified."
)

MAINTENANCE_EDGE_PROMPT = (
    "Connect triggers to actions. Show which parts need replacement or inspection. Note specific precautions for each task."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class CarMaintenanceGraph(AutoGraph[MaintenanceItem, MaintenanceSequence]):
    """
    Template for vehicle service manuals, repair guides, and ownership logs.
    
    Helps organize maintenance schedules and part compatibility information.
    
    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI()
        >>> embedder = OpenAIEmbeddings()
        >>> graph = CarMaintenanceGraph(llm_client=llm, embedder=embedder)
        >>> text = "Change engine oil and filter every 10,000 km using synthetic 0W-20."
        >>> graph.feed_text(text)
        >>> print(graph.nodes) # Maintenance items
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
        Initialize the CarMaintenanceGraph template.

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
            node_schema=MaintenanceItem,
            edge_schema=MaintenanceSequence,
            node_key_extractor=lambda x: x.item_name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.action.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=MAINTENANCE_GRAPH_PROMPT,
            prompt_for_node_extraction=MAINTENANCE_NODE_PROMPT,
            prompt_for_edge_extraction=MAINTENANCE_EDGE_PROMPT,
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
        def node_label_extractor(node: MaintenanceItem) -> str:
            info = f" ({ node.category })" if getattr(node, "category", None) else ""
            return f"{ node.item_name }{info}"
    
        def edge_label_extractor(edge: MaintenanceSequence) -> str:
            return f"{ edge.action }"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
