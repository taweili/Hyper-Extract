from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class BioEntityNode(BaseModel):
    """
    A fundamental biological unit representing a gene, protein, or small molecule.
    """
    name: str = Field(description="Standardized symbol or name (e.g., 'BRCA1', 'cAMP').")
    category: str = Field(description="Entity type: 'Gene', 'Protein', 'RNA', 'Metabolite', 'Enzyme', 'Transcription Factor'.")
    synonyms: Optional[str] = Field(None, description="Alternative names or database IDs (e.g., UniProt, Entrez).")
    biological_function: Optional[str] = Field(None, description="Dominant molecular function or cellular localization.")

class BioInteractionEdge(BaseModel):
    """
    A direct physical or functional interaction between two biological entities.
    """
    source: str = Field(description="The upstream or acting entity.")
    target: str = Field(description="The downstream or acted-upon entity.")
    interaction_type: str = Field(description="Type: 'Phosphorylates', 'Inhibits', 'Activates', 'Binds', 'Regulates', 'Cleaves'.")
    mechanism: Optional[str] = Field(None, description="Specific biochemical mechanism (e.g., 'Allosteric inhibition').")
    strength: Optional[str] = Field(None, description="Confidence score or binding affinity if available.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a bioinformatics expert specializing in molecular signaling and regulatory networks. "
    "Extract interactions from the text to build a biological network graph.\n\n"
    "Rules:\n"
    "- Distinguish between different molecular types (Protein vs Gene).\n"
    "- Identify directed interactions (e.g., Enzyme A phosphorylates Protein B).\n"
    "- Capture the specific biochemical mechanism for each edge."
)

_NODE_PROMPT = (
    "You are a bioinformatics expert. Your task is to identify all molecular entities (Nodes) mentioned in the text.\n\n"
    "Extraction Rules:\n"
    "- Identify genes, proteins, RNAs, and metabolites. Use standard nomenclature (e.g., HGNC symbols).\n"
    "- Capture synonyms and biological functions where available.\n"
    "- Exclude generic biological terms unless they are acting as specific placeholders for known molecules.\n"
    "- DO NOT extract interactions or state changes at this stage."
)

_EDGE_PROMPT = (
    "You are a bioinformatics expert. Given the following list of molecular entities, extract their physical and functional interactions (Edges).\n\n"
    "Extraction Rules:\n"
    "- Identify the type of interaction (Phosphorylation, Inhibition, Activation, Binding, etc.).\n"
    "- Specify the directionality (source acts on target).\n"
    "- Only create edges between entities present in the provided list.\n"
    "- Include the biochemical mechanism and interaction strength if mentioned."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class BiologicalNetwork(AutoGraph[BioEntityNode, BioInteractionEdge]):
    """
    Template for modeling molecular signaling, metabolic pathways (binary), and regulatory networks.
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
        super().__init__(
            node_schema=BioEntityNode,
            edge_schema=BioInteractionEdge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.interaction_type.lower()})-->{x.target.strip()}",
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
        def node_label_extractor(node: BioEntityNode) -> str:
            info = f" ({ node.category })" if getattr(node, "category", None) else ""
            return f"{ node.name }{info}"
    
        def edge_label_extractor(edge: BioInteractionEdge) -> str:
            return f"{ edge.interaction_type }"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
