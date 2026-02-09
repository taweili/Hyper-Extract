from typing import List, Optional
from pydantic import BaseModel, Field
from hyperextract.graphs import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class Concept(BaseModel):
    """A conceptual node representing a term, idea, or theory."""
    term: str = Field(description="The technical term or concept name.")
    definition: str = Field(description="A formal definition or explanation of the concept.")
    examples: Optional[List[str]] = Field(default_factory=list, description="Examples that illustrate this concept.")
    attributes: Optional[List[str]] = Field(default_factory=list, description="Key properties or attributes of the concept.")

class ConceptRelation(BaseModel):
    """A semantic relationship between two concepts."""
    source: str = Field(description="The source concept.")
    target: str = Field(description="The target concept.")
    relation_type: str = Field(
        description="Type of relationship (e.g., is-a, part-of, related-to, used-for, instance-of)."
    )

# ==============================================================================
# 2. Prompts
# ==============================================================================

CONCEPT_MAP_PROMPT = (
    "You are an expert in semantic modeling. Extract a concept map from the text, focusing on "
    "definitions, terminologies, and their hierarchical or associative relationships.\n\n"
    "Guidelines:\n"
    "- Identify core terms and provide their precise definitions based on the text.\n"
    "- Use standard semantic relations like 'is-a' (inheritance) or 'part-of' (composition).\n"
    "- Capture illustrative examples if mentioned."
)

CONCEPT_MAP_NODE_PROMPT = (
    "Extract all foundational concepts and technical terms from the text. "
    "For each concept, provide its term, a precise definition, a list of key attributes, "
    "and any specific examples mentioned in the source."
)

CONCEPT_MAP_EDGE_PROMPT = (
    "Establish semantic relationships between the provided concepts. "
    "Focus on hierarchical taxonomies (is-a, part-of) and functional associations (used-for, instance-of). "
    "Ensure edges logically connect the defined concepts."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class ConceptMap(AutoGraph[Concept, ConceptRelation]):
    """
    A template for building conceptual graphs and taxonomies.
    Ideal for technical documentation, educational materials, and glossaries.
    """
    def __init__(self, **kwargs):
        super().__init__(
            node_schema=Concept,
            edge_schema=ConceptRelation,
            node_key_extractor=lambda x: x.term.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.relation_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            prompt=CONCEPT_MAP_PROMPT,
            prompt_for_node_extraction=CONCEPT_MAP_NODE_PROMPT,
            prompt_for_edge_extraction=CONCEPT_MAP_EDGE_PROMPT,
            **kwargs
        )
