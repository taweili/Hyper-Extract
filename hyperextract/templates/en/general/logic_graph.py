from typing import List, Optional
from pydantic import BaseModel, Field
from hyperextract.graphs import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class LogicNode(BaseModel):
    """A node representing a claim, evidence, or premise in an argument."""
    statement: str = Field(description="The central claim, fact, or observation.")
    node_type: str = Field(
        description="Type of node: Claim (main point), Evidence (supporting data), Premise (underlying assumption)."
    )
    source_attribution: Optional[str] = Field(description="Where or who this logic point originates from.")

class LogicRelation(BaseModel):
    """The logical connection between two statements."""
    source: str = Field(description="The source statement.")
    target: str = Field(description="The target statement.")
    inference: str = Field(
        description="The logical link: Supports, Contradicts, Proves, Leads to, Explains."
    )

# ==============================================================================
# 2. Prompts
# ==============================================================================

LOGIC_GRAPH_PROMPT = (
    "You are a logical analyst. Extract the reasoning structure from the text into a directed graph.\n\n"
    "Guidelines:\n"
    "- Identify the main claims (conclusions) and the evidence or premises that lead to them.\n"
    "- Explicitly map how one statement supports or contradicts another.\n"
    "- Do not just extract facts; extract the 'argument' and 'reasoning' flow."
)

LOGIC_GRAPH_NODE_PROMPT = (
    "Extract the individual building blocks of the argument. Identify core claims, supporting evidence, "
    "and underlying premises. For each, determine its type and note any source attribution mentioned."
)

LOGIC_GRAPH_EDGE_PROMPT = (
    "Map the logical flow between the extracted claims and evidence. Focus on how statements "
    "Support, Contradict, or Lead to one another. Ensure every edge represents a step in the reasoning chain."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class LogicGraph(AutoGraph[LogicNode, LogicRelation]):
    """
    A template for analyzing reasoning, arguments, and causal chains.
    Ideal for analytical reports, debate transcripts, and scientific reasoning.
    """
    def __init__(self, **kwargs):
        super().__init__(
            node_schema=LogicNode,
            edge_schema=LogicRelation,
            node_key_extractor=lambda x: x.statement.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.inference.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            prompt=LOGIC_GRAPH_PROMPT,
            prompt_for_node_extraction=LOGIC_GRAPH_NODE_PROMPT,
            prompt_for_edge_extraction=LOGIC_GRAPH_EDGE_PROMPT,
            **kwargs
        )
