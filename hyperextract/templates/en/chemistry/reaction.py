from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.hypergraphs.base import AutoHypergraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class ChemicalEntity(BaseModel):
    """
    A chemical substance (Reagent, Product, Catalyst, Solvent).
    """
    name: str = Field(description="IUPAC name or common name (e.g., 'Sulfuric Acid').")
    formula: Optional[str] = Field(None, description="Chemical formula (e.g., 'H2SO4').")
    cas_number: Optional[str] = Field(None, description="CAS Registry Number.")
    phase: str = Field("Unknown", description="Physical state: 'Gas', 'Liquid', 'Solid', 'Aqueous'.")

class ReactionEvent(BaseModel):
    """
    A chemical reaction involving multiple reagents, specific conditions, and resulting products.
    """
    reaction_id: str = Field(description="Name or short description of the reaction (e.g., 'Haber Process').")
    reactants: List[str] = Field(description="List of starting chemical entity names.")
    products: List[str] = Field(description="List of resulting chemical entity names.")
    catalysts: List[str] = Field(default_factory=list, description="Names of substances facilitating the reaction.")
    solvents: List[str] = Field(default_factory=list, description="The medium in which the reaction occurs.")
    temperature: Optional[str] = Field(None, description="Operating temperature (e.g., '250°C').")
    pressure: Optional[str] = Field(None, description="Operating pressure (e.g., '200 atm').")
    yield_info: Optional[str] = Field(None, description="Percentage/amount of product obtained.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

REACTION_CONSOLIDATED_PROMPT = (
    "You are an expert organic and inorganic chemist. Extract multi-component reaction events.\n\n"
    "Rules:\n"
    "- Represent each reaction as a Hyperedge connecting all reactants, products, and catalysts.\n"
    "- Capture detailed conditions like temperature, pressure, and specific solvents.\n"
    "- Identify the role of each chemical entity correctly in the reaction context."
)

REACTION_NODE_PROMPT = (
    "You are an organic chemist. Your task is to identify and extract all chemical entities (Nodes) mentioned in the text.\n\n"
    "Extraction Rules:\n"
    "- Identify reagents, products, catalysts, and solvents.\n"
    "- Capture IUPAC names, chemical formulas, and CAS numbers where available.\n"
    "- Note the physical phase (Gas, Liquid, Solid) of each entity.\n"
    "- DO NOT construct reaction sequences or grouping participants at this stage."
)

REACTION_EDGE_PROMPT = (
    "You are an organic chemist. Given the list of chemical entities, extract multi-component reaction events (Hyperedges).\n\n"
    "Extraction Rules:\n"
    "- Group all participants (reactants, products, catalysts, solvents) into a single reaction hyperedge.\n"
    "- Clearly specify the roles (Reactant vs. Product) for each involved entity in the metadata.\n"
    "- Only include entities that are present in the provided entity list.\n"
    "- Capture specific conditions like temperature, pressure, and yield info for the reaction event."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class ChemicalReactionHyper(AutoHypergraph[ChemicalEntity, ReactionEvent]):
    """
    Hypergraph template for complex chemical synthesis, industrial processes, and reaction pathways.
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
            node_schema=ChemicalEntity,
            edge_schema=ReactionEvent,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: x.reaction_id.strip(),
            nodes_in_edge_extractor=lambda x: tuple(set(x.reactants + x.products + x.catalysts + x.solvents)),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=REACTION_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=REACTION_NODE_PROMPT,
            prompt_for_edge_extraction=REACTION_EDGE_PROMPT,
            **kwargs
        )
