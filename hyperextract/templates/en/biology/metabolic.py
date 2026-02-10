from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.hypergraphs.base import AutoHypergraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class MetaboliteNode(BaseModel):
    """
    Any physical substance (substrate or product) involved in a metabolic reaction.
    """
    name: str = Field(description="Chemical or common name of the molecule (e.g., 'Pyruvate').")
    formula: Optional[str] = Field(None, description="Chemical formula/notation.")
    charge: Optional[int] = Field(None, description="Net electrical charge of the metabolite.")
    compartment: Optional[str] = Field(description="Cellular location: 'Cytosol', 'Mitochondria', 'Extracellular'.")

class MetabolicReactionHyperedge(BaseModel):
    """
    A multi-reagent biochemical reaction where multiple substrates yield multiple products.
    """
    reaction_id: str = Field(description="Unique identifier or EC number (e.g., 'EC 1.1.1.1').")
    substrates: List[str] = Field(description="List of substrate metabolite names.")
    products: List[str] = Field(description="List of product metabolite names.")
    enzymes: List[str] = Field(default_factory=list, description="List of catalysts (enzymes) involved.")
    stoichiometry: Optional[str] = Field(None, description="Balancing coefficients if mentioned in text.")
    reversibility: bool = Field(True, description="Whether the reaction is reversible.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

METABOLIC_CONSOLIDATED_PROMPT = (
    "You are a biochemist specializing in metabolic engineering. Extract complex N-ary reactions.\n\n"
    "Rules:\n"
    "- Group all participants (substrates, products, and enzymes) into a single Hyperedge.\n"
    "- Distinguish between reactants (substrates) and results (products).\n"
    "- Capture the catalytic enzymes as part of the hyperedge participants."
)

METABOLIC_NODE_PROMPT = (
    "You are a biochemist. Your task is to identify all metabolites and catalytic enzymes (Nodes) involved in metabolic processes.\n\n"
    "Extraction Rules:\n"
    "- Identify chemical components (substrates/products) and the enzymes that facilitate their transformation.\n"
    "- Capture formulas, charges, and cellular compartments if described.\n"
    "- Ensure names are standardized (e.g., 'Glucose-6-phosphate').\n"
    "- DO NOT construct reaction equations or complexes at this stage."
)

METABOLIC_EDGE_PROMPT = (
    "You are a biochemist. Given the following list of metabolites and enzymes, extract complex metabolic reactions (Hyperedges).\n\n"
    "Extraction Rules:\n"
    "- Group all participants (substrates, products, and enzymes) into single reaction events.\n"
    "- Clearly distinguish between substrates (inputs) and products (outputs) within the reaction metadata.\n"
    "- Only include participants that exist in the provided entity list.\n"
    "- Record stoichiometry and reversibility where specific data is available."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class MetabolicHypergraph(AutoHypergraph[MetaboliteNode, MetabolicReactionHyperedge]):
    """
    Complex hypergraph template for metabolic pathways involving multi-substrate/multi-product reactions.
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
            node_schema=MetaboliteNode,
            edge_schema=MetabolicReactionHyperedge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: x.reaction_id.strip(),
            nodes_in_edge_extractor=lambda x: tuple(set(x.substrates + x.products + x.enzymes)),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=METABOLIC_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=METABOLIC_NODE_PROMPT,
            prompt_for_edge_extraction=METABOLIC_EDGE_PROMPT,
            **kwargs
        )
