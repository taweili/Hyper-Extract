from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definition
# ==============================================================================


class IndustrialEquipment(BaseModel):
    """
    Industrial equipment entity, including main equipment, auxiliary equipment, instruments, valves, pipelines, etc.
    """

    name: str = Field(description="Equipment or component name.")
    category: str = Field(
        description='Category: main equipment, auxiliary equipment, component, instrument, valve, pipeline, system, motor, pump, fan, container, etc.'
    )
    location: Optional[str] = Field(
        None,
        description="Installation location (e.g., production workshop floor 1, main building floor 2).",
    )
    status: Optional[str] = Field(
        None,
        description="Operating status: running, standby, maintenance, stopped.",
    )
    specification: Optional[str] = Field(
        None,
        description="Specifications or technical parameters.",
    )
    manufacturer: Optional[str] = Field(
        None,
        description="Manufacturer.",
    )


class EquipmentConnection(BaseModel):
    """
    Connection relationship between equipment.
    """

    source: str = Field(description="Upstream equipment or source equipment name.")
    target: str = Field(description="Downstream equipment or target equipment name.")
    connection_type: str = Field(
        description='Connection type: material transfer, energy transfer, control signal, process flow, electrical connection, instrument monitoring.'
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the connection (e.g., high-temperature material flow, circulating water loop, closed-loop control system).",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an industrial equipment management expert. Extract equipment entities and their interconnections from industrial equipment documents.\n\n"
    "Rules:\n"
    "- Identify all equipment, components, and systems, including main equipment, auxiliary equipment, instruments, valves, pumps, fans, motors, etc.\n"
    "- Classify equipment types (main/auxiliary/component/instrument/valve/pipeline/system).\n"
    "- Extract connection relationships between equipment, including material transfer, energy transfer, control signals, etc.\n"
    "- Record installation location and operating status.\n"
)

_NODE_PROMPT = (
    "You are an industrial equipment management expert. Extract all equipment entities (nodes) from documents.\n\n"
    "Extraction Rules:\n"
    "- Identify equipment names and component names.\n"
    "- Classify equipment categories (main equipment, auxiliary equipment, component, instrument, valve, pipeline, system, motor, pump, fan, container, etc.).\n"
    "- Record installation location and operating status.\n"
    "- Do not establish relationships between equipment.\n"
)

_EDGE_PROMPT = (
    "You are an industrial equipment management expert. Based on the equipment list, extract connection relationships between equipment (edges).\n\n"
    "Extraction Rules:\n"
    "- Identify material transfer relationships between equipment (upstream → downstream).\n"
    "- Identify energy transfer relationships (driven equipment → driven equipment).\n"
    "- Identify control signal relationships (control equipment → controlled equipment).\n"
    "- Identify process flow relationships (previous process → next process).\n"
    "- Identify electrical connections and instrument monitoring relationships.\n"
    "- Only establish relationships in the provided equipment list, do not create new equipment nodes.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class EquipmentTopologyGraph(AutoGraph[IndustrialEquipment, EquipmentConnection]):
    """
    Applicable Documents: Equipment system diagrams, Piping and Instrumentation Diagrams (P&ID), equipment lists, equipment records, system manuals, equipment chapters in maintenance procedures.

    This template extracts equipment topology relationships from industrial equipment documents.
    It identifies physical connections, material flows, energy transfer, and control signal
    relationships between equipment to construct an equipment system topology graph.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> topology = EquipmentTopologyGraph(llm_client=llm, embedder=embedder)
        >>> doc = "Line A consists of reactor B, cooling pump C and control cabinet D. Material from reactor B is transported through pipeline to cooling pump C for cooling, C is driven by motor E. Control cabinet D monitors B's temperature in real-time and controls E's speed."
        >>> topology.feed_text(doc)
        >>> topology.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize Equipment Topology Graph template.

        Args:
            llm_client (BaseChatModel): LLM for entity and relationship extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage". Default is "two_stage".
            chunk_size (int): Maximum characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Number of parallel processing worker threads.
            verbose (bool): Enable progress logging.
            **kwargs: Additional AutoGraph parameters.
        """
        super().__init__(
            node_schema=IndustrialEquipment,
            edge_schema=EquipmentConnection,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.connection_type})-->{x.target.strip()}"
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
        Visualize equipment topology graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of relationships to retrieve. Default 3.
            top_k_nodes_for_chat (int): Number of entities in chat context. Default 3.
            top_k_edges_for_chat (int): Number of relationships in chat context. Default 3.
        """

        def node_label_extractor(node: IndustrialEquipment) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: EquipmentConnection) -> str:
            return edge.connection_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
