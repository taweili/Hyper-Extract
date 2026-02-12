from typing import Optional, Any, Callable
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types.graph import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class AgriPestEntity(BaseModel):
    """An entity in the pest control domain (Pest, Disease, Crop, Symptom, Treatment)."""

    name: str = Field(description="Name of the pest, crop, disease, or chemical agent.")
    category: str = Field(
        description="Category: 'Pest', 'Disease', 'Host Crop', 'Symptom', 'Prevention Method', 'Chemical Treatment'."
    )
    description: Optional[str] = Field(
        None, description="Detailed description, biological traits, or characteristics."
    )


class AgriPestRelation(BaseModel):
    """The relationship between agricultural entities (e.g., 'infests', 'causes', 'treated_by')."""

    source: str = Field(description="The source entity name.")
    target: str = Field(description="The target entity name.")
    relation_type: str = Field(
        description="Type: 'infests', 'parasitizes', 'damages', 'causes symptom', 'prevented by', 'sensitive to'."
    )
    detail: Optional[str] = Field(
        None, description="Specific conditions, dosage, or damage severity."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = """
You are an expert agronomist and pest management specialist. 
Your task is to extract a comprehensive knowledge graph of crop pests, diseases, and their control methods.

Guidelines:
1. Identify biological threats: Pests, insects, fungi, bacteria, or viruses.
2. Link threats to their host crops and the specific symptoms they cause (e.g., leaf spot, stem rot).
3. Map out integrated pest management (IPM) strategies, including biological, physical, and chemical control methods.
4. Extract specific chemical agents, dosages, and application timings mentioned in the text.
"""

# ==============================================================================
# 3. Template Class
# ==============================================================================


class AgriPestControl(AutoGraph[AgriPestEntity, AgriPestRelation]):
    """
    Knowledge graph template for agricultural pest and disease management.
    
    Transforms technical manuals and guidelines into structured control strategies.
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
        """Initialize the AgriPestControl template."""
        super().__init__(
            node_schema=AgriPestEntity,
            edge_schema=AgriPestRelation,
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
            prompt=_PROMPT,
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
        """Visualize the pest control knowledge graph."""

        def node_label_extractor(node: AgriPestEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: AgriPestRelation) -> str:
            return f"{edge.relation_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
