from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class TaxonNode(BaseModel):
    """
    Represents a biological taxon in the Tree of Life.
    """
    name: str = Field(description="Scientific name (Latin) or standardized common name of the organism/group.")
    rank: str = Field(description="Taxonomic rank: 'Domain', 'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species'.")
    common_name: Optional[str] = Field(None, description="General name used in non-scientific contexts.")
    description: Optional[str] = Field(None, description="Brief biological characteristics, habitat, or distinguishing traits.")

class TaxonomyRelation(BaseModel):
    """
    A direct hierarchical relationship between two taxons.
    """
    source: str = Field(description="The parent taxon (e.g., 'Mammalia').")
    target: str = Field(description="The child taxon (e.g., 'Primates').")
    type: str = Field("parent_of", description="Relationship type: 'parent_of', 'subspecies_of', 'classified_under'.")
    evidence: Optional[str] = Field(None, description="Reference to phenotypic or genomic data justifying the classification.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

TAXONOMY_CONSOLIDATED_PROMPT = (
    "You are a professional taxonomist and systematic biologist. Extract the biological hierarchy (Taxonomy) from the text.\n\n"
    "Rules:\n"
    "- Identify all taxons (Kingdom to Species) and their specific ranks.\n"
    "- Construct a strict tree-like hierarchy using 'parent_of' relationships.\n"
    "- Capture both scientific names and common names where available."
)

TAXONOMY_NODE_PROMPT = (
    "You are a professional taxonomist. Your task is to identify and extract all biological taxonomic units (Nodes) from the text.\n\n"
    "Extraction Rules:\n"
    "- Identify the scientific name and assigned rank (e.g., Domain, Kingdom, Phylum, Class, Order, Family, Genus, Species) for each taxon.\n"
    "- Capture common names and brief descriptions if provided.\n"
    "- Focus exclusively on formal biological classifications.\n"
    "- DO NOT extract relationships between taxons at this stage."
)

TAXONOMY_EDGE_PROMPT = (
    "You are a professional taxonomist. Given the following list of identified taxons, extract the hierarchical relationships (Edges) described in the text.\n\n"
    "Extraction Rules:\n"
    "- Establish 'parent_of' links where a higher-rank taxon contains a lower-rank one.\n"
    "- Ensure the lineage accurately reflects the phylogenetic or systematic tree described.\n"
    "- Only connect nodes that exist in the provided taxon list.\n"
    "- Complement the relationship with any evidence or genomic context mentioned."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class TaxonomyGraph(AutoGraph[TaxonNode, TaxonomyRelation]):
    """
    High-fidelity template for biological classification and phylogenetic hierarchies.
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
            node_schema=TaxonNode,
            edge_schema=TaxonomyRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.type})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=TAXONOMY_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=TAXONOMY_NODE_PROMPT,
            prompt_for_edge_extraction=TAXONOMY_EDGE_PROMPT,
            **kwargs
        )
