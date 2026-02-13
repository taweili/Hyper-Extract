from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class BiologicalHazard(BaseModel):
    """
    A biological hazard that must be controlled in food production.
    """

    name: str = Field(
        description="Hazard pathogen name (e.g., 'Salmonella', 'Listeria monocytogenes', 'E. coli O157:H7')."
    )
    hazard_type: str = Field(
        description="Type: 'Bacterial', 'Viral', 'Parasitic', 'Fungal'."
    )
    health_consequence: Optional[str] = Field(
        None, description="Potential health effect (e.g., 'Severe gastroenteritis', 'Sepsis')."
    )


class CriticalControlPoint(BaseModel):
    """
    A step or process in food production where a hazard can be controlled.
    """

    name: str = Field(
        description="CCP name (e.g., 'Pasteurization', 'Metal Detection', 'Cold Storage')."
    )
    process_stage: str = Field(
        description="Stage in production: 'Raw Material', 'Receiving', 'Processing', 'Cooking', 'Cooling', 'Packaging', 'Storage'."
    )
    description: Optional[str] = Field(
        None, description="Detailed description of the CCP."
    )


class ControlMeasure(BaseModel):
    """
    A control measure linking a hazard to a CCP.
    """

    source: str = Field(description="The biological hazard name.")
    target: str = Field(description="The CCP name.")
    critical_limit: str = Field(
        description="Critical limit defining the boundary between safe/unsafe (e.g., '>=72°C for >=15 seconds', 'pH < 4.6')."
    )
    monitoring_procedure: str = Field(
        description="How the CCP is monitored (e.g., 'Thermometer reading every batch', 'pH meter daily')."
    )
    monitoring_frequency: str = Field(
        description="How often monitoring occurs (e.g., 'Every 2 hours', 'Per batch', 'Daily')."
    )
    corrective_action: str = Field(
        description="Action if critical limit is not met (e.g., 'Discard product', 'Reprocess', 'Alert QA')."
    )
    verification: Optional[str] = Field(
        None, description="Verification method to confirm effectiveness (e.g., 'Culture tests monthly')."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a food safety specialist trained in HACCP principles. Extract hazards, critical control points, "
    "and their control measures from HACCP plans and food safety documentation.\n\n"
    "Rules:\n"
    "- Identify biological hazards relevant to the product and process.\n"
    "- Identify CCPs where hazards can be eliminated or controlled.\n"
    "- Extract critical limits, monitoring procedures, and corrective actions.\n"
    "- Ensure each CCP is linked to specific hazard(s) it controls."
)

_NODE_PROMPT = (
    "You are a food safety specialist. Extract all hazards and CCPs (Nodes) from the HACCP documentation.\n\n"
    "Extraction Rules:\n"
    "- Identify all biological hazards mentioned (pathogens, allergens if applicable).\n"
    "- Identify all CCPs (cooking, cooling, metal detection stages).\n"
    "- Classify each hazard by type (Bacterial, Viral, Fungal, Parasitic).\n"
    "- Classify each CCP by production stage.\n"
    "- DO NOT establish control relationships at this stage."
)

_EDGE_PROMPT = (
    "You are a food safety specialist. Given the list of hazards and CCPs, extract the control relationships (Edges).\n\n"
    "Extraction Rules:\n"
    "- Connect each hazard to the CCP(s) that control it.\n"
    "- Extract critical limits with precise thresholds and units.\n"
    "- Extract monitoring procedures and frequency from the HACCP document.\n"
    "- Extract corrective actions to be taken if limits are violated.\n"
    "- Include verification methods when documented.\n"
    "- Only create edges between hazards and CCPs that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class FoodSafetyHACCPGraph(AutoGraph[BiologicalHazard, ControlMeasure]):
    """
    Applicable to: HACCP Plans, Food Safety Plans (ISO 22000), SOP Manuals,
    FDA Guidance Documents, Food Company Quality Procedures, Supplier Audit Reports.

    Template for systematically extracting and structuring HACCP-based food safety 
    controls. Enables compliance verification, supplier auditing, and continuous 
    safety monitoring across food production operations.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> haccp = FoodSafetyHACCPGraph(llm_client=llm, embedder=embedder)
        >>> plan = "Critical Control Point: Pasteurization. Hazard: Salmonella. Critical limit: 72°C for 15s..."
        >>> haccp.feed_text(plan)
        >>> haccp.show()
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
        Initialize the Food Safety HACCP Graph template.

        Args:
            llm_client (BaseChatModel): The LLM for hazard and control extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoGraph.
        """
        super().__init__(
            node_schema=BiologicalHazard,
            edge_schema=ControlMeasure,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.target.strip()}): {x.critical_limit.strip()}"
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
        Visualize the food safety control graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of hazards/CCPs to retrieve. Default 3.
            top_k_edges_for_search (int): Number of control measures to retrieve. Default 3.
            top_k_nodes_for_chat (int): Nodes for chat context. Default 3.
            top_k_edges_for_chat (int): Edges for chat context. Default 3.
        """

        def node_label_extractor(node: BiologicalHazard) -> str:
            if isinstance(node, BiologicalHazard):
                return f"{node.name} ({node.hazard_type})"
            return str(node)

        def edge_label_extractor(edge: ControlMeasure) -> str:
            return f"{edge.critical_limit}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
