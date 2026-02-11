from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class ThreatActorNode(BaseModel):
    """
    An entity (individual, group, or nation-state) responsible for cyber threats.
    """

    actor_name: str = Field(
        description="Alias or group name (e.g., 'APT28', 'Fancy Bear', 'Lazarus Group')."
    )
    origin_country: Optional[str] = Field(
        None, description="Suspected geographic origin."
    )
    motivation: Optional[str] = Field(
        None,
        description="Primary driver: 'Espionage', 'Financial Gain', 'Sabotage', 'Hacktivism'.",
    )
    typical_targets: List[str] = Field(
        default_factory=list, description="Commonly targeted industries or regions."
    )


class IntelligenceNexus(BaseModel):
    """
    A hyperedge connecting an actor, specific infrastructure, and a campaign theme.
    """

    participants: List[str] = Field(
        description="Entities involved: Actor names, Tool names, Infrastructure (IPs/Domains), Target Organizations."
    )
    campaign_name: str = Field(
        description="Known name of the operation (e.g., 'SolarWinds Supply Chain Attack')."
    )
    shared_ttp: str = Field(
        description="The common tactic, technique, or procedure that links these disparate entities."
    )
    confidence_level: str = Field(
        "Medium", description="Analytical confidence: 'High', 'Medium', 'Low'."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

CYBER_NEXUS_CONSOLIDATED_PROMPT = (
    "You are a Strategic Threat Intelligence Analyst. Map the high-level correlations between actors, infrastructure, and infrastructure.\n\n"
    "Rules:\n"
    "- Identify threat actors and their aliases as Nodes.\n"
    "- Create Hyperedges (Nexuses) that link actors to specific tools and infrastructure under a named campaign.\n"
    "- Focus on multi-point connections that reveal a cohesive operation rather than simple binary links.\n"
    "- Highlight shared TTPs that unify the nexus."
)

CYBER_NEXUS_NODE_PROMPT = (
    "Identify threat actors, malware families, and malicious infrastructure entities.\n\n"
    "Rules:\n"
    "- Extract actor aliases and group names.\n"
    "- Identify motivations and target industries.\n"
    "- DO NOT identify campaigns or relations yet."
)

CYBER_NEXUS_EDGE_PROMPT = (
    "Identify the operational Campaigns or Nexuses that unify actors, tools, and targets.\n\n"
    "Rules:\n"
    "- Each hyperedge must describe a single campaign or operation.\n"
    "- Link the actor(s) to the specific infrastructure and tools used in that operation.\n"
    "- Only link entities from the provided list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class ThreatIntelligenceNexusHypergraph(
    AutoHypergraph[ThreatActorNode, IntelligenceNexus]
):
    """
    Template for strategic threat intelligence mapping.

    Ideal for connecting dots between infrastructure, actors, and malware in complex campaigns.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> nexus = ThreatIntelligenceNexusHypergraph(llm_client=llm, embedder=embedder)
        >>> nexus.feed_text("APT28 utilized X-Tunnel and C2 at 1.2.3.4 during Operation Fancy-Phish.")
        >>> print(nexus.nodes)  # Access threat actors
        >>> print(nexus.edges)  # Access campaign hyperedges
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
        """
        Initialize the Threat Intelligence Nexus Hypergraph template.

        Args:
            llm_client (BaseChatModel): The language model client used for nexus extraction.
            embedder (Embeddings): The embedding model used for actor deduplication.
            extraction_mode (str, optional): 'one_stage' for joint extraction,
                'two_stage' for separate passes. Defaults to "one_stage".
            chunk_size (int, optional): Maximum characters per text chunk. Defaults to 2048.
            chunk_overlap (int, optional): Overlap between chunks. Defaults to 256.
            max_workers (int, optional): Parallel processing workers. Defaults to 10.
            verbose (bool, optional): If True, enables progress logging. Defaults to False.
            **kwargs (Any): Additional parameters for the AutoHypergraph base class.
        """
        super().__init__(
            node_schema=ThreatActorNode,
            edge_schema=IntelligenceNexus,
            node_key_extractor=lambda x: x.actor_name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.campaign_name.strip().lower()}_linking_{sorted(x.participants)}"
            ),
            nodes_in_edge_extractor=lambda x: [
                p.strip().lower() for p in x.participants
            ],
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CYBER_NEXUS_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=CYBER_NEXUS_NODE_PROMPT,
            prompt_for_edge_extraction=CYBER_NEXUS_EDGE_PROMPT,
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
        """
        Visualize the graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of nodes to retrieve for search context. Default 3.
            top_k_edges_for_search (int): Number of edges to retrieve for search context. Default 3.
            top_k_nodes_for_chat (int): Number of nodes to retrieve for chat context. Default 3.
            top_k_edges_for_chat (int): Number of edges to retrieve for chat context. Default 3.
        """

        def node_label_extractor(node: ThreatActorNode) -> str:
            return f"{node.actor_name}"

        def edge_label_extractor(edge: IntelligenceNexus) -> str:
            return f"{edge.campaign_name}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
