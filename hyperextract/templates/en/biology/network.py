from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.graphs.base import AutoGraph

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

NETWORK_CONSOLIDATED_PROMPT = (
    "You are a bioinformatics expert specializing in molecular signaling and regulatory networks. "
    "Extract interactions from the text to build a biological network graph.\n\n"
    "Rules:\n"
    "- Distinguish between different molecular types (Protein vs Gene).\n"
    "- Identify directed interactions (e.g., Enzyme A phosphorylates Protein B).\n"
    "- Capture the specific biochemical mechanism for each edge."
)

NETWORK_NODE_PROMPT = (
    "Identify all genes, proteins, and molecules mentioned. Normalize names to standard symbols where possible. "
    "Ignore generic terms like 'the protein' or 'this molecule' unless they refer to a specific named entity."
)

NETWORK_EDGE_PROMPT = (
    "Extract functional and physical interactions between the identified bio-entities. "
    "Define the direction and nature of the interaction (Activation, Inhibition, etc.)."
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
            prompt=NETWORK_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=NETWORK_NODE_PROMPT,
            prompt_for_edge_extraction=NETWORK_EDGE_PROMPT,
            **kwargs
        )
