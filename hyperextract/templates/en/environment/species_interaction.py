from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types.graph import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class Species(BaseModel):
    """An organism entity in the ecosystem."""

    name: str = Field(description="Scientific or common name of the species.")
    category: str = Field(
        description="Taxonomic classification: 'Mammal', 'Bird', 'Insect', 'Plant', 'Microorganism', etc."
    )
    protection_level: Optional[str] = Field(
        None, description="Conservation status: 'Endangered', 'Vulnerable', 'Least Concern', etc."
    )


class Interaction(BaseModel):
    """The biological interaction between two species."""

    source: str = Field(description="The initiating species (predator, competitor, etc.).")
    target: str = Field(description="The receiving species (prey, competitor, host, etc.).")
    interaction_type: str = Field(
        description="Type of interaction: 'predation', 'parasitism', 'mutualism', 'commensalism', 'competition', 'symbiosis'."
    )
    detail: Optional[str] = Field(
        None, description="Specific details about the interaction (e.g., frequency, seasonal pattern, ecological impact)."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = """
You are an expert ecologist and biodiversity specialist.
Your task is to extract the ecological interaction network from scientific texts, field reports, or nature documentaries.

Guidelines:
1. Identify all organisms mentioned in the text and classify them by category (species, type).
2. Extract the biological relationships between organisms (predation, parasitism, competition, mutualism, etc.).
3. For each interaction, capture the interaction type and any specific ecological details (timing, frequency, conditions).
4. Preserve the directionality of interactions (e.g., "Lion hunts Zebra" is different from "Zebra avoids Lion").
5. Include conservation status information if mentioned.

Output Format:
- Each species should be a distinct entity with name, category, and conservation status if available.
- Each interaction should clearly state the source (initiating organism), target (receiving organism), and interaction type.
"""

_NODE_PROMPT = """
You are an expert ecologist and biodiversity specialist.
Your task is to extract ONLY species/organisms from the text during the first extraction stage.
Do not identify interactions yet - focus solely on finding all distinct organisms mentioned.

Guidelines:
1. List all species, organisms, or populations mentioned in the text.
2. For each organism, capture: name, category (e.g., predator, prey, plant, decomposer), and conservation status if available.
3. Ensure no duplicates: if "Lion" and "African Lion" refer to the same species, consolidate to the most specific name.
4. Ignore vague references; extract only explicitly mentioned organisms.

Output Format:
- Each organism should be a distinct node with clear name, category, and status.
"""

_EDGE_PROMPT = """
You are an expert ecologist analyzing species interactions.
Your task is to extract ONLY the biological relationships between given species during the second extraction stage.
You will be provided with a list of already-extracted species (nodes). Your job is to identify interactions between them.

Guidelines:
1. Given the list of confirmed species, find all pairwise interactions mentioned in the text.
2. For each interaction, capture: source species, target species, interaction type (predation, mutualism, competition, etc.), and details.
3. Preserve directionality: "A eats B" is predation (A→B), different from "B avoids A".
4. Only extract interactions that connect the given species; ignore mentions of species not in the provided list.
5. Include ecological context (seasonal, frequency, conditions) as details.

Output Format:
- Each interaction is an edge: Source → Target with relation type and details.
"""

# ==============================================================================
# 3. Template Class
# =============================================================================="


class SpeciesInteractionNetwork(AutoGraph[Species, Interaction]):
    """
    Knowledge graph template for ecological species interactions.

    Transforms scientific texts and field studies into structured interaction networks,
    enabling analysis of ecosystem biodiversity and food webs.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4")
        >>> embedder = OpenAIEmbeddings()
        >>> 
        >>> network = SpeciesInteractionNetwork(llm_client=llm, embedder=embedder)
        >>> text = "Lions hunt zebras in the African savanna. Parasitic wasps are eaten by birds."
        >>> network.feed_text(text)
        >>> network.show()  # Visualize the species interaction network
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
        **kwargs: Any,
    ):
        """Initialize the SpeciesInteractionNetwork template.

        Args:
            llm_client (BaseChatModel): Language model client for species and interaction extraction.
            embedder (Embeddings): Embedding model for vector indexing of species nodes and interaction edges.
            extraction_mode (str, optional): Extraction strategy. Defaults to "one_stage".
                - "one_stage": Extract species and interactions simultaneously (faster).
                - "two_stage": Extract species first, then interactions (higher accuracy).
            chunk_size (int, optional): Maximum characters per text chunk. Defaults to 2048.
            chunk_overlap (int, optional): Overlapping characters between chunks for context preservation. Defaults to 256.
            max_workers (int, optional): Maximum concurrent extraction workers. Defaults to 10.
            verbose (bool, optional): If True, prints detailed extraction progress logs. Defaults to False.
            **kwargs: Additional arguments passed to the AutoGraph base class.
        """
        super().__init__(
            node_schema=Species,
            edge_schema=Interaction,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.interaction_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ) -> None:
        """Visualize the species interaction network for ecological analysis.

        Displays the extracted species (nodes) and their interactions (edges) using OntoSight visualization.
        Internally defines frontend visualization labels for species (name + category + protection status)
        and interactions (interaction type).

        Args:
            top_k_nodes_for_search (int, optional): Number of species nodes to retrieve for search-triggered context. Defaults to 3.
            top_k_edges_for_search (int, optional): Number of interaction edges to retrieve for search-triggered context. Defaults to 3.
            top_k_nodes_for_chat (int, optional): Number of species nodes to retrieve for chat-triggered context. Defaults to 3.
            top_k_edges_for_chat (int, optional): Number of interaction edges to retrieve for chat-triggered context. Defaults to 3.
        """

        def node_label_extractor(node: Species) -> str:
            status = f" [{node.protection_level}]" if node.protection_level else ""
            return f"{node.name} ({node.category}){status}"

        def edge_label_extractor(edge: Interaction) -> str:
            return f"{edge.interaction_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
