from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class StakeholderNode(BaseModel):
    """
    A legal or natural person holding equity or control in a business.
    """
    name: str = Field(description="Full registry name of the company or individual's full name.")
    type: str = Field(description="Type: 'Natural Person', 'Public Company', 'Private Company', 'State-Owned Enterprise', 'Venture Capital'.")
    jurisdiction: Optional[str] = Field(None, description="Country or region of incorporation/residence.")
    is_ubo: bool = Field(False, description="Whether this entity is identified as an Ultimate Beneficial Owner.")

class OwnershipRelation(BaseModel):
    """
    A stakeholding or control link between two entities.
    """
    source: str = Field(description="The shareholder or parent entity.")
    target: str = Field(description="The company being owned or controlled (subsidiary).")
    stake_percentage: Optional[float] = Field(None, description="Percentage of ownership (0.0 to 100.0).")
    control_type: str = Field("Equity", description="Nature of link: 'Equity Acquisition', 'Voting Rights', 'Nominee Shareholding', 'Direct Control'.")
    as_of_date: Optional[str] = Field(None, description="The date or fiscal period when this ownership was recorded.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

EQUITY_CONSOLIDATED_PROMPT = (
    "You are a corporate paralegal and financial analyst. Extract complex ownership structures.\n\n"
    "Rules:\n"
    "- Prioritize identifying the percentage of shares held by each entity.\n"
    "- Distinguish between direct shareholders and Ultimate Beneficial Owners (UBO).\n"
    "- Map the hierarchy from the parent organization down to the smallest subsidiary."
)

EQUITY_NODE_PROMPT = (
    "You are a corporate paralegal and financial analyst. Your task is to identify all stakeholders (Nodes) within a corporate structure.\n\n"
    "Extraction Rules:\n"
    "- Identify companies, investment funds, government bodies, and individual persons.\n"
    "- Classify each as 'Natural Person', 'Public Company', 'Private Company', etc.\n"
    "- Flag entities identified as Ultimate Beneficial Owners (UBO) where explicit.\n"
    "- DO NOT extract ownership percentages or control links at this stage."
)

EQUITY_EDGE_PROMPT = (
    "You are a corporate paralegal and financial analyst. Given the list of stakeholders, map the ownership and control relationships (Edges).\n\n"
    "Extraction Rules:\n"
    "- Extract the exact percentage of equity held between a shareholder (source) and a company (target).\n"
    "- Specify the nature of control (e.g., Voting Rights, Direct Control, Nominee Shareholding).\n"
    "- Create edges only between entities found in the provided stakeholder list.\n"
    "- Capture the 'as of' date or historical period for the ownership record."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class EquityStructureGraph(AutoGraph[StakeholderNode, OwnershipRelation]):
    """
    Precision template for corporate registries, M&A analysis, and KYC/UBO tracking.
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
            node_schema=StakeholderNode,
            edge_schema=OwnershipRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}->{x.target.strip()}_at_{x.stake_percentage}%",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=EQUITY_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=EQUITY_NODE_PROMPT,
            prompt_for_edge_extraction=EQUITY_EDGE_PROMPT,
            **kwargs
        )
