from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSpatialGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class PhysicalElementNode(BaseModel):
    """
    A specific physical component or zone within a construction site.
    """

    name: str = Field(
        description="Unique identifier or name of the element (e.g., 'Column-A1', 'Zone-B')."
    )
    element_type: str = Field(
        description="Type: 'Structural', 'MEP', 'Architectural', 'Temporary Structure', 'Safety Zone'."
    )
    location_coordinates: Optional[str] = Field(
        None,
        description="Spatial coordinates or relative grid location (e.g., 'X:10, Y:20, Z:5').",
    )
    material_properties: Optional[str] = Field(
        None, description="Key material info (e.g., 'C30 Concrete', 'Steel S355')."
    )


class SpatialRelation(BaseModel):
    """
    A spatial or topological connection between two physical elements.
    """

    source: str = Field(description="The reference element.")
    target: str = Field(description="The related element.")
    location_marker: str = Field(
        description="The physical location or zone where this relationship resides (e.g., 'Level 3', 'North Wing', 'Grid A-1')."
    )
    relation_type: str = Field(
        description="Type: 'Supporting', 'Adjacent', 'Enclosed By', 'Intersects', 'Aligned With'."
    )
    offset_distance: Optional[float] = Field(
        None, description="Physical distance between elements in meters."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

CONSTRUCTION_SPATIAL_CONSOLIDATED_PROMPT = (
    "You are a Senior BIM (Building Information Modeling) Engineer and Site Surveyor. Extract the spatial topology of the construction project.\n\n"
    "Rules:\n"
    "- Identify fixed physical elements and their properties as Nodes.\n"
    "- Map the structural and spatial relationships (Edges) between these elements.\n"
    "- Ensure coordinates and distances are captured if mentioned.\n"
    "- Focus on how objects are physically connected or positioned relative to each other."
)

CONSTRUCTION_SPATIAL_NODE_PROMPT = (
    "Identify all physical building components and site zones.\n\n"
    "Rules:\n"
    "- Extract distinct structural, mechanical, or architectural elements.\n"
    "- Capture any mentioned locations, levels, or material information.\n"
    "- DO NOT identify connections at this stage."
)

CONSTRUCTION_SPATIAL_EDGE_PROMPT = (
    "Map the spatial and structural relationships between the identified building elements.\n\n"
    "Rules:\n"
    "- Determine how Element A relates to Element B (e.g., A supports B, A is adjacent to B).\n"
    "- Extract physical offsets or distances if provided.\n"
    "- Only link elements from the provided list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class SiteTopologyGraph(AutoSpatialGraph[PhysicalElementNode, SpatialRelation]):
    """
    Template for building a spatial digital twin of a construction site.

    Useful for structural analysis, BIM-to-Graph conversion, and site logistics planning.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> graph = SiteTopologyGraph(llm_client=llm, embedder=embedder)
        >>> graph.feed_text("The foundation slab supports the four main corner columns.")
        >>> print(graph.nodes)  # Access structural elements
        >>> print(graph.edges)  # Access spatial relationships
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
        Initialize the Site Topology Graph template.

        Args:
            llm_client (BaseChatModel): The language model client used for topology extraction.
            embedder (Embeddings): The embedding model used for element deduplication.
            extraction_mode (str, optional): 'one_stage' for joint extraction,
                'two_stage' for separate passes. Defaults to "one_stage".
            chunk_size (int, optional): Maximum characters per text chunk. Defaults to 2048.
            chunk_overlap (int, optional): Overlap between chunks. Defaults to 256.
            max_workers (int, optional): Parallel processing workers. Defaults to 10.
            verbose (bool, optional): If True, enables progress logging. Defaults to False.
            **kwargs (Any): Additional parameters for the AutoSpatialGraph base class.
        """
        super().__init__(
            node_schema=PhysicalElementNode,
            edge_schema=SpatialRelation,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}--{x.relation_type.lower()}--{x.target.strip().lower()}"
            ),
            nodes_in_edge_extractor=lambda x: (
                x.source.strip().lower(),
                x.target.strip().lower(),
            ),
            location_in_edge_extractor=lambda x: x.location_marker.strip(),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CONSTRUCTION_SPATIAL_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=CONSTRUCTION_SPATIAL_NODE_PROMPT,
            prompt_for_edge_extraction=CONSTRUCTION_SPATIAL_EDGE_PROMPT,
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
        Visualize the graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of nodes to retrieve for search context. Default 3.
            top_k_edges_for_search (int): Number of edges to retrieve for search context. Default 3.
            top_k_nodes_for_chat (int): Number of nodes to retrieve for chat context. Default 3.
            top_k_edges_for_chat (int): Number of edges to retrieve for chat context. Default 3.
        """

        def node_label_extractor(node: PhysicalElementNode) -> str:
            return f"{node.name}"

        def edge_label_extractor(edge: SpatialRelation) -> str:
            return f"{edge.relation_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
