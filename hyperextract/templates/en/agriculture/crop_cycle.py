from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class AgriEntity(BaseModel):
    """An entity in the agricultural domain (e.g., Crop, Soil, Pest, Pest Control, Equipment)."""

    name: str = Field(description="The name of the agricultural entity.")
    category: str = Field(
        description="Category: 'Crop', 'Growth Stage', 'Soil/Climate Condition', 'Task/Activity', 'Stress/Pest', 'Input/Fertilizer'."
    )
    description: Optional[str] = Field(
        description="Specific characteristics or state of the entity."
    )


class AgriRelation(BaseModel):
    """A relationship between agricultural entities (e.g., 'requires', 'affected by', 'follows')."""

    source: str = Field(description="The source entity name.")
    target: str = Field(description="The target entity name.")
    relation_type: str = Field(
        description="Type: 'is at stage', 'impacts', 'requires task', 'applied to', 'leads to next stage'."
    )
    specification: Optional[str] = Field(
        description="Dosage, timing, or specific impact details."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an expert agronomist. Extract a crop growth and management graph from the text.\n\n"
    "Guidelines:\n"
    "- Identify the crop and its specific growth stages (e.g., Sowing, Flowering).\n"
    "- Map soil conditions, weather requirements, and necessary farming activities (irrigation, fertilization) to specific stages.\n"
    "- Note any threats like pests or diseases and their impact on the crop."
)

_NODE_PROMPT = (
    "You are an expert agronomist. Your task is to identify and extract all key agricultural entities (Nodes) from the text.\n\n"
    "Extraction Rules:\n"
    "- Identify crop types, specific growth stages, environmental factors (e.g., pH, temperature), and farming tasks.\n"
    "- Capture biological stresses such as specific pests, fungi, or diseases.\n"
    "- Classify each node into the appropriate category: 'Crop', 'Growth Stage', 'Task/Activity', etc.\n"
    "- DO NOT identify sequences or dependencies between these entities at this stage."
)

_EDGE_PROMPT = (
    "You are an expert agronomist. Given the list of agricultural entities, map the logical links and cycles (Edges).\n\n"
    "Extraction Rules:\n"
    "- Establish sequential links between growth stages.\n"
    "- Link farming tasks to the specific growth stages where they must be performed.\n"
    "- Map how environmental conditions and pests impact the crop or its stages.\n"
    "- Use specific relation types such as 'is at stage', 'requires task', 'inhibits', or 'applied to'.\n"
    "- Only connect entities that exist in the provided agricultural entity list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class CropCycleGraph(AutoGraph[AgriEntity, AgriRelation]):
    """
    Template for mapping crop growth stages, environmental requirements, and farming activities.

    Ideal for precision agriculture, crop management guides, and seasonal planning.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> graph = CropCycleGraph(llm_client=llm, embedder=embedder)
        >>> text = "Corn requires high nitrogen during the vegetative stage."
        >>> graph.feed_text(text)
        >>> print(graph.nodes) # Extracted Corn, Nitrogen, Vegetative Stage
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
        Initialize the CropCycleGraph template.

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
            node_schema=AgriEntity,
            edge_schema=AgriRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.relation_type.lower()})-->{x.target.strip()}"
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
        Visualize the graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of nodes to retrieve for search context. Default 3.
            top_k_edges_for_search (int): Number of edges to retrieve for search context. Default 3.
            top_k_nodes_for_chat (int): Number of nodes to retrieve for chat context. Default 3.
            top_k_edges_for_chat (int): Number of edges to retrieve for chat context. Default 3.
        """

        def node_label_extractor(node: AgriEntity) -> str:
            info = f" ({node.category})" if getattr(node, "category", None) else ""
            return f"{node.name}{info}"

        def edge_label_extractor(edge: AgriRelation) -> str:
            return f"{edge.relation_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
