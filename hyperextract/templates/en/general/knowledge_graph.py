from typing import List, Optional
from pydantic import BaseModel, Field
from hyperextract.graphs import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class Entity(BaseModel):
    """A general entity representing a person, organization, location, or object."""
    name: str = Field(description="The primary name of the entity.")
    category: str = Field(
        description="Category of the entity (e.g., Person, Organization, Location, Event, Object)."
    )
    description: Optional[str] = Field(
        description="A concise summary of the entity and its role in the text."
    )

class Relation(BaseModel):
    """A factual relationship between two entities."""
    source: str = Field(description="The name of the source entity.")
    target: str = Field(description="The name of the target entity.")
    relation: str = Field(description="The type of relationship (e.g., Works for, Located in, Born in, Acquired).")
    details: Optional[str] = Field(description="Additional context or details about this relationship.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

KNOWLEDGE_GRAPH_PROMPT = (
    "You are an expert knowledge extraction system. Your task is to extract a factual knowledge graph "
    "from the provided text. Focus on identifying key entities (People, Organizations, Locations, and relevant Objects) "
    "and the explicit relationships between them.\n\n"
    "Guidelines:\n"
    "- Extract distinct entitles and their factual properties.\n"
    "- Map relationships that describe how entities interact or are connected.\n"
    "- Use clear, concise language for descriptions and relations."
)

KNOWLEDGE_GRAPH_NODE_PROMPT = (
    "Extract all key entities from the text. Focus on identifying People, Organizations, Locations, and important Objects. "
    "Provide a name, a category, and a concise description for each entity."
)

KNOWLEDGE_GRAPH_EDGE_PROMPT = (
    "Identify factual relationships between the following listed entities based on the text. "
    "Focus on interactions like 'works for', 'located in', 'acquired', or 'partnered with'. "
    "Do not hallucinate entities not in the provided list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class KnowledgeGraph(AutoGraph[Entity, Relation]):
    """
    A foundational knowledge graph template for factual extraction.
    Best for news, biographies, and descriptive encyclopedic content.
    """
    def __init__(self, **kwargs):
        super().__init__(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--[{x.relation.lower()}]-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            prompt=KNOWLEDGE_GRAPH_PROMPT,
            prompt_for_node_extraction=KNOWLEDGE_GRAPH_NODE_PROMPT,
            prompt_for_edge_extraction=KNOWLEDGE_GRAPH_EDGE_PROMPT,
            **kwargs
        )
