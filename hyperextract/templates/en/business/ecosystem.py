from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.hypergraphs.base import AutoHypergraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class IndustryParticipant(BaseModel):
    """
    An entity (Company, Regulatory Body, NGO) within an industrial ecosystem.
    """
    name: str = Field(description="Name of the actor (e.g., 'TSMC', 'European Commission').")
    rank: Optional[str] = Field(None, description="Market position: 'Tier 1 Supplier', 'Market Leader', 'Challenger'.")
    technological_focus: Optional[str] = Field(None, description="Primary tech or domain (e.g., '5G', 'Lithography').")

class CollectiveAlliance(BaseModel):
    """
    A hyperedge representing a consortium, alliance, market cartel, or joint standard-setting body.
    """
    alliance_id: str = Field(description="Name or identifier of the alliance (e.g., 'CHIPS Alliance').")
    participants: List[str] = Field(description="Names of all entities collaborating or competing in this group.")
    shared_goal: str = Field(description="The objective: 'Standardization', 'Anti-monopoly Review', 'Joint R&D'.")
    governance: Optional[str] = Field(None, description="Rules of participation or leading entity.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

ECOSYSTEM_CONSOLIDATED_PROMPT = (
    "You are a market strategist and antitrust expert. Extract market ecosystem dynamics.\n\n"
    "Rules:\n"
    "- Use Hyperedges to link multiple entities (3+) participating in a joint venture or alliance.\n"
    "- Capture non-binary group relations like cartels, industrial clusters, and regulatory coalitions.\n"
    "- Define the shared goal of these groups clearly."
)

ECOSYSTEM_NODE_PROMPT = (
    "You are a market analyst. Your task is to identify all participants (Nodes) within an industrial ecosystem.\n\n"
    "Extraction Rules:\n"
    "- Identify companies, NGOs, and regulatory bodies mentioned.\n"
    "- Capture their market rank and primary technological focus area.\n"
    "- Focus on naming actors that collaborate or compete as a group.\n"
    "- DO NOT identify alliances, joint ventures, or consortia at this stage."
)

ECOSYSTEM_EDGE_PROMPT = (
    "You are a market analyst. Given the industrial participants, extract the collective relationships (Hyperedges).\n\n"
    "Extraction Rules:\n"
    "- Group multiple participants (3+) into alliances, standard bodies, or joint ventures.\n"
    "- Define the shared goal (e.g., 'R&D', 'Anti-monopoly Review') for the entire group.\n"
    "- Record any mentioned governance structures or leading participants.\n"
    "- Ensure every group member is selected from the provided participants list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class MarketEcosystemHyper(AutoHypergraph[IndustryParticipant, CollectiveAlliance]):
    """
    Hypergraph template for industrial clusters, ecosystem coalitions, and complex market alliances.
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
            node_schema=IndustryParticipant,
            edge_schema=CollectiveAlliance,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: x.alliance_id.strip(),
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=ECOSYSTEM_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=ECOSYSTEM_NODE_PROMPT,
            prompt_for_edge_extraction=ECOSYSTEM_EDGE_PROMPT,
            **kwargs
        )
