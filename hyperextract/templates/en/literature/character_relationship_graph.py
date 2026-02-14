from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class Character(BaseModel):
    """A character entity in a literary work."""
    name: str = Field(description="The full or most common name of the character.")
    aliases: List[str] = Field(default_factory=list, description="Other names, titles, or nicknames used for the character.")
    traits: List[str] = Field(default_factory=list, description="Core personality traits, skills, or physical attributes.")
    description: Optional[str] = Field(description="A brief description of the character's role and significance in the story.")

class Relationship(BaseModel):
    """Social or emotional interaction between characters."""
    source: str = Field(description="The name of the character initiating or participating in the relationship.")
    target: str = Field(description="The name of the second character in the relationship.")
    relation_type: str = Field(description="The nature of the relationship (e.g., Kinship, Romance, Rivalry, Mentorship).")
    sentiment: str = Field(description="The emotional tone (e.g., Positive, Negative, Ambivalent, Intense).")
    evidence: str = Field(description="Brief textual evidence or plot point supporting this relationship.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a sophisticated literary critic and character analysis expert. "
    "Your task is to extract character entities and their relationship networks from the literary text.\n\n"
    "Extraction Guidelines:\n"
    "1. **Character Identification**: Identify all significant characters. Record their names, aliases, and core character traits.\n"
    "2. **Relationship Analysis**: Analyze dialogues, actions, and narrative descriptions to extract deep connections. "
    "Focus not only on kinship but also on emotional bonds, ideological conflicts, and shifting allegiances.\n"
    "3. **Evidence-Based**: Provide short textual evidence for each relationship.\n"
    "- Ensure every edge connects two nodes that are explicitly listed in the character nodes."
)

_NODE_PROMPT = (
    "As a literary expert, extract all key characters. For each character, provide their name, any known aliases, core personality tags, and a brief description of their role/status."
)

_EDGE_PROMPT = (
    "Based on the extracted characters, identify the social and emotional relationships between them. "
    "Specify the relationship type, emotional sentiment, and provide a brief justification based on the text."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class CharacterRelationshipGraph(AutoGraph[Character, Relationship]):
    """
    Applicable to: [Novels, Screenplays, Biographies, Dramas]

    Knowledge pattern for extracting character networks and social structures in literature.

    This template captures dynamic interactions, emotional tones, and structured connections, 
    supporting two-stage extraction for higher precision in complex narrative webs.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # Initialize template
        >>> characters = CharacterRelationshipGraph(llm_client=llm, embedder=embedder)
        >>> # Feed text
        >>> text = "Elizabeth Bennet's initial prejudice against Mr. Darcy was challenged by his noble actions."
        >>> characters.feed_text(text)
        >>> characters.show()
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
        """
        Initialize CharacterRelationshipGraph template.

        Args:
            llm_client: The language model client.
            embedder: Embeddings model for deduplication and indexing.
            extraction_mode: "one_stage" (fast) or "two_stage" (accurate).
            chunk_size: Max characters per processing chunk.
            chunk_overlap: Overlap between chunks.
            max_workers: Number of parallel extraction workers.
            verbose: Enable detailed logging.
            **kwargs: Extra arguments for AutoGraph.
        """
        super().__init__(
            node_schema=Character,
            edge_schema=Relationship,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """
        Visualize the character relationship graph.

        Args:
            top_k_for_search: Number of nodes/edges to retrieve for search context.
            top_k_for_chat: Number of nodes/edges to retrieve for chat context.
        """
        def node_label_extractor(node: Character) -> str:
            return node.name

        def edge_label_extractor(edge: Relationship) -> str:
            return f"{edge.relation_type} ({edge.sentiment})"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
