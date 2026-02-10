from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.graphs.temporal_graph import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class StrategicNode(BaseModel):
    """
    An organizational entity, business division, or strategic objective.
    """
    name: str = Field(description="Name of the strategic unit or goal (e.g., 'Azure', 'Carbon Neutrality').")
    scope: str = Field(description="Scope: 'Global', 'Regional', 'Product-specific', 'Corporate-wide'.")
    importance: Optional[str] = Field(None, description="Criticality: 'Core Business', 'Emerging Market', 'Legacy'.")

class StrategicPivot(BaseModel):
    """
    A temporal transition representing a change in strategic focus, investment, or divestiture.
    """
    source: str = Field(description="The original area of focus or acting entity.")
    target: str = Field(description="The new target, direction, or goal.")
    action: str = Field(description="Strategic action: 'Pivot to', 'Acquire', 'Divest', 'Merge', 'Sunset', 'Scale'.")
    timestamp: str = Field(description="When the shift occurred (e.g., 'Q4 2022', '2025-01-01').")
    rationale: Optional[str] = Field(None, description="The 'Why' behind the move (market pressure, CEO change, tech shift).")
    budget: Optional[str] = Field(None, description="Financial commitment mentioned alongside the pivot.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

STRATEGY_CONSOLIDATED_PROMPT = (
    "You are a management consultant and industry analyst. Extract the evolution of corporate strategy.\n\n"
    "Rules:\n"
    "- Focus on 'Pivots': movements from one business area to another.\n"
    "- Link specific actions to concrete timestamps.\n"
    "- Capture the underlying reasoning (rationale) for each strategic change."
)

STRATEGY_NODE_PROMPT = (
    "Extract business units, product lines, and high-level corporate goals. Identify their organizational importance."
)

STRATEGY_EDGE_PROMPT = (
    "Map strategic transitions over time. Ensure the 'timestamp' is resolved to specific periods. "
    "Identify what the company moved FROM (source) and what it moved TO (target)."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class StrategicChainGraph(AutoTemporalGraph[StrategicNode, StrategicPivot]):
    """
    Temporal template for tracking corporate strategy, longitudinal organizational change, and market shifts.
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
            node_schema=StrategicNode,
            edge_schema=StrategicPivot,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}-({x.action})->{x.target.strip()}",
            time_in_edge_extractor=lambda x: x.timestamp.strip(),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=STRATEGY_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=STRATEGY_NODE_PROMPT,
            prompt_for_edge_extraction=STRATEGY_EDGE_PROMPT,
            **kwargs
        )
