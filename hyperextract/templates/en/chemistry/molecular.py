from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSpatialGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class AtomNode(BaseModel):
    """
    An individual atom in a chemical structure.
    """
    name: str = Field(description="Atom identifier (e.g., 'C1', 'O2') or element symbol.")
    element: str = Field(description="The chemical element (e.g., 'Carbon', 'H').")
    hybridization: Optional[str] = Field(None, description="Electronic state: 'sp3', 'sp2', 'sp'.")
    formal_charge: int = Field(0, description="The electrical charge assigned to the atom.")

class ChemicalBond(BaseModel):
    """
    A chemical bond between two atoms, including spatial/positional metadata.
    """
    source: str = Field(description="The originating atom (e.g., 'C1').")
    target: str = Field(description="The connected atom (e.g., 'C2').")
    bond_type: str = Field(description="Type: 'Single', 'Double', 'Triple', 'Aromatic', 'Hydrogen'.")
    spatial_position: str = Field(description="The physical or logical position in the molecule (e.g., 'C4 position', 'Axial', 'Equatorial').")
    bond_length: Optional[float] = Field(None, description="Distance between atoms in Angstroms.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

MOLECULAR_CONSOLIDATED_PROMPT = (
    "You are a computational chemist and crystallographer. Extract the 3D molecular topology.\n\n"
    "Rules:\n"
    "- Identify every atom as a node.\n"
    "- Define bonds including their specific spatial orientation (e.g., 'Alpha', 'Beta', 'Cis', 'Trans').\n"
    "- Capture the formal charge and hybridization of each atom."
)

MOLECULAR_NODE_PROMPT = (
    "You are a computational chemist. Your task is to identify and extract all individual atoms (Nodes) from the molecular structure.\n\n"
    "Extraction Rules:\n"
    "- Identify the unique atom identifier (e.g., C1) and its chemical element symbol.\n"
    "- Capture the electronic hybridization state (sp, sp2, sp3) and formal charge for each atom.\n"
    "- Focus on maintaining the exact nomenclature present in the source text.\n"
    "- DO NOT identify bonds or spatial connectivity at this stage."
)

MOLECULAR_EDGE_PROMPT = (
    "You are a computational chemist. Given the list of atoms, map the chemical bonds and spatial connectivity (Edges).\n\n"
    "Extraction Rules:\n"
    "- Define the bond type (Single, Double, Aromatic, etc.) between a source and target atom.\n"
    "- Precisely identify the spatial position or stereochemical orientation (e.g., Axial, Equatorial, Cis, Trans).\n"
    "- Only create bonds between atoms that are present in the provided atom list.\n"
    "- Capture bond lengths if numerical data is provided."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class MolecularStructureGraph(AutoSpatialGraph[AtomNode, ChemicalBond]):
    """
    Spatial graph template for high-resolution molecular modeling and structural biology.
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
            node_schema=AtomNode,
            edge_schema=ChemicalBond,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.bond_type})-->{x.target.strip()}",
            location_in_edge_extractor=lambda x: x.spatial_position.strip(),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=MOLECULAR_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=MOLECULAR_NODE_PROMPT,
            prompt_for_edge_extraction=MOLECULAR_EDGE_PROMPT,
            **kwargs
        )
