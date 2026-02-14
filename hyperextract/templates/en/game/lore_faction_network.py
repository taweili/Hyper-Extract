"""Lore Faction Network - Extracts faction relationships from game lore.

This template builds a political/social relationship graph showing how characters,
factions, and regions interact within the game world.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# Schema Definitions
# ==============================================================================

class LoreEntitySchema(BaseModel):
    """Schema for entities in the lore network (characters, factions, regions)."""

    entity_id: str = Field(..., description="Unique identifier for this entity")
    entity_type: str = Field(
        ...,
        description="Type of entity: 'Hero' (character), 'Faction' (organization), or 'Region' (location)",
    )
    entity_name: str = Field(..., description="Name of the entity")
    description: Optional[str] = Field(
        None, description="Brief description of the entity's background or characteristics"
    )


class LoreRelationshipSchema(BaseModel):
    """Schema for relationships in the lore network."""

    source_entity: str = Field(..., description="Name of the source entity")
    target_entity: str = Field(..., description="Name of the target entity")
    relationship_type: str = Field(
        ...,
        description="Type of relationship: 'Belongs_To' (allegiance), 'At_War_With' (conflict), "
        "'Betrayed' (betrayal), 'Founded' (founding), 'Ally_With' (alliance), etc.",
    )
    context: Optional[str] = Field(
        None, description="Background context or explanation for this relationship"
    )


# ==============================================================================
# Extraction Prompts - One-Stage and Two-Stage
# ==============================================================================

_PROMPT = """You are an expert game lore analyst specializing in world-building and faction relationships.
Your task is to extract entities (Nodes) and their political/social relationships (Edges) from game lore text.

Extract:
1. **Entities (Nodes)**: All characters (heroes), factions (organizations), and regions mentioned
   - For characters: name, type='Hero'
   - For factions: name, type='Faction'
   - For regions: name, type='Region'

2. **Relationships (Edges)**: Political, military, and social connections
   - Belongs_To: A character belongs to a faction or resides in a region
   - At_War_With: Two factions or entities are in conflict
   - Betrayed: A character/faction betrayed another
   - Founded: A character founded a faction
   - Ally_With: Formal alliance between factions
   - Other relationship types based on context

CRITICAL: Every edge must connect two entities that are present in the extracted nodes list.
Do not create edges between entities that are not explicitly identified as nodes.

Extract only information explicitly stated in the text.

### Source Text:
"""

_NODE_PROMPT = """You are an expert entity recognition specialist for game lore.
Your task is to extract all distinct entities from the text that will serve as nodes in a lore network.

Extract three types of entities:
1. **Heroes/Characters**: Individual persons with names (e.g., "Yasuo", "Ahri")
2. **Factions/Organizations**: Groups, orders, nations, guilds (e.g., "Ionia", "Noxus", "The Watchers")
3. **Regions/Locations**: Geographic areas and places (e.g., "Shadow Isles", "Piltover", "Demacia")

For each entity, provide:
- The entity name (as appears in text)
- The entity type (Hero/Faction/Region)
- A brief description if available

Focus on completeness. Extract every entity mentioned, no matter how briefly.

### Source Text:
"""

_EDGE_PROMPT = """You are an expert relationship extraction specialist for game lore networks.
Your task is to extract relationships (edges) between the provided entities.

Given the known entities list below, extract all relationships that connect them:
- Belongs_To: Character belongs to faction; faction controls region
- At_War_With: Entities in armed conflict
- Betrayed: One entity betrayed another
- Founded: Character founded a faction
- Ally_With: Formal alliance between factions
- Opposes: Opposition without necessarily warfare

CRITICAL RULES:
1. ONLY extract edges connecting entities from the known entity list provided below
2. DO NOT invent or hallucinate new entities not in the provided list
3. If an entity appears in text but isn't in the known list, DO NOT create edges involving it
4. Focus on explicit relationship statements in the text

Extract only explicitly stated relationships. Do not infer relationships not clearly described.

### Source Text:
"""


# ==============================================================================
# Template Class
# ==============================================================================

class LoreFactionNetwork(AutoGraph[LoreEntitySchema, LoreRelationshipSchema]):
    """Applicable to: Game background stories, Lore documents, Character bios, Setting guides

    Extracts a political and social relationship graph from game lore,
    showing how characters, factions, and regions interact within the game world.

    This template is particularly useful for:
    - Visualizing faction relationships and hierarchies
    - Understanding character allegiances and conflicts
    - Building world-building maps of political structures
    - Analyzing geopolitical dynamics in game settings

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.en.game import LoreFactionNetwork
        >>>
        >>> llm = ChatOpenAI(model="gpt-4", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>>
        >>> lore_graph = LoreFactionNetwork(
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     extraction_mode="two_stage"
        ... )
        >>>
        >>> lore_graph.feed_text('''
        ... Yasuo is a swordsman from the region of Ionia. He belongs to the traditionalist faction.
        ... Ionia is at war with Noxus for control of the eastern territories.
        ... Ahri is a fox spirit who betrayed Yasuo when she sided with Noxus.
        ... ''')
        >>>
        >>> # Nodes: Yasuo, Ionia, Noxus, Ahri
        >>> # Edges: Yasuo->Ionia (Belongs_To), Ionia->Noxus (At_War_With), Ahri->Yasuo (Betrayed)
        >>> lore_graph.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        """Initialize the Lore Faction Network template.

        Args:
            llm_client: Language model for extraction (e.g., ChatOpenAI).
            embedder: Embedding model for semantic indexing (e.g., OpenAIEmbeddings).
            extraction_mode: 'one_stage' (faster, simpler) or 'two_stage' (more accurate).
            chunk_size: Maximum characters per text chunk (default 2048).
            chunk_overlap: Overlapping characters between chunks (default 256).
            **kwargs: Additional arguments passed to AutoGraph parent class.
        """
        super().__init__(
            node_schema=LoreEntitySchema,
            edge_schema=LoreRelationshipSchema,
            node_key_extractor=lambda x: x.entity_name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source_entity.strip().lower()}|"
                f"{x.relationship_type.strip().lower()}|"
                f"{x.target_entity.strip().lower()}"
            ),
            nodes_in_edge_extractor=lambda x: (
                x.source_entity.strip().lower(),
                x.target_entity.strip().lower(),
            ),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 5,
        top_k_for_chat: int = 5,
    ) -> None:
        """Display the lore faction network as an interactive relationship graph.

        Args:
            top_k_for_search: Number of top entities to retrieve for search.
            top_k_for_chat: Number of top entities to show in chat context.
        """

        def node_label_extractor(node: LoreEntitySchema) -> str:
            """Extract display label showing entity type."""
            type_emoji = {
                "Hero": "👤",
                "Faction": "🏛️",
                "Region": "🗺️",
            }
            emoji = type_emoji.get(node.entity_type, "●")
            return f"{emoji} {node.entity_name}"

        def edge_label_extractor(edge: LoreRelationshipSchema) -> str:
            """Extract display label for relationships."""
            return edge.relationship_type.replace("_", " ")

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
