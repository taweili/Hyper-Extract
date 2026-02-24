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
        description="Boundary between safe/unsafe (e.g. '>72C')."
    )
    monitoring: str = Field(
        description="Procedure and frequency of monitoring."
    )
    details: Optional[str] = Field(
        None, description="Corrective actions and verification methods."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a food safety specialist. Extract hazards, CCPs, and controls.\n\n"
    "Rules:\n"
    "- Identify hazards and CCPs.\n"
    "- Link hazards to CCPs via control measures.\n"
    "- Extract **critical_limit** and **monitoring** details.\n"
    "- Capture corrective actions in **details**."
)

_NODE_PROMPT = (
    "You are a food safety specialist. Extract hazards and CCPs (Nodes).\n\n"
    "Rules:\n"
    "- Identify biological hazards and classify type.\n"
    "- Identify CCPs and production stage.\n"
)

_EDGE_PROMPT = (
    "You are a food safety specialist. Extract control measures (Edges).\n\n"
    "Rules:\n"
    "- Connect hazard to CCP.\n"
    "- **critical_limit**: Safety boundary.\n"
    "- **monitoring**: How and when to check.\n"
    "- **details**: Corrective actions and verification.\n"
    "- Only connect existing nodes."
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
        >>> llm = ChatOpenAI(model="gpt-5-mini")
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
