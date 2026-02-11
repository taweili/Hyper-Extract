from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class AttackStageNode(BaseModel):
    """
    A specific phase or action in a cyber attack (aligned with MITRE ATT&CK or Lockheed Kill Chain).
    """

    stage_name: str = Field(
        description="Name of the attack stage (e.g., 'Initial Access', 'Lateral Movement')."
    )
    tactics_used: List[str] = Field(
        default_factory=list,
        description="Specific techniques or tactics employed (e.g., 'Phishing', 'Pass-the-Hash').",
    )
    adversary_tools: List[str] = Field(
        default_factory=list,
        description="Malware or tools used in this stage (e.g., 'Cobalt Strike', 'Mimikatz').",
    )
    timestamp: Optional[str] = Field(
        None, description="Time or sequence marker for the action."
    )


class KillChainLink(BaseModel):
    """
    A directional link representing the progression of an attack from one stage to another.
    """

    source: str = Field(description="The preceding attack stage.")
    target: str = Field(description="The succeeding attack stage.")
    causality: str = Field(
        "Progression",
        description="Type: 'Progression' (standard), 'Triggered' (automatic), 'Pivoted' (infrastructure shift).",
    )
    observables: List[str] = Field(
        default_factory=list,
        description="IOCs (Indicators of Compromise) linking the stages.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

CYBER_KILL_CHAIN_CONSOLIDATED_PROMPT = (
    "You are a Forensic Investigator and Incident Responder. Reconstruct the attack timeline and kill chain from incident reports.\n\n"
    "Rules:\n"
    "- Identify distinct attack stages as Nodes.\n"
    "- Map the chronological and logical progression (Edges) of the intrusion.\n"
    "- Capture specific tactics, tools (TTPs), and timestamps for each stage.\n"
    "- Focus on the 'how' and 'when' of the adversary's movement."
)

CYBER_KILL_CHAIN_NODE_PROMPT = (
    "Identify all suspicious activities and distinct phases of a cyber intrusion.\n\n"
    "Rules:\n"
    "- Extract action-oriented stages (e.g., 'Delivery of Payload', 'C2 Establishment').\n"
    "- Identify the tools and techniques associated with each discovery.\n"
    "- DO NOT link the stages yet."
)

CYBER_KILL_CHAIN_EDGE_PROMPT = (
    "Establish the sequence and progression between identified attack stages.\n\n"
    "Rules:\n"
    "- Define which stage led to or enabled the next.\n"
    "- Identify Indicators of Compromise (IPs, Hashes) that connect the stages.\n"
    "- Only link stages from the provided list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class IntrusionKillChainGraph(AutoGraph[AttackStageNode, KillChainLink]):
    """
    Template for reconstructing cyber attack lifecycles.

    Useful for incident response (IR), forensic reporting, and threat hunting.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> kill_chain = IntrusionKillChainGraph(llm_client=llm, embedder=embedder)
        >>> kill_chain.feed_text("The attacker gained initial access via a phishing email.")
        >>> print(kill_chain.nodes)  # Access attack stages
        >>> print(kill_chain.edges)  # Access progression links
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
        Initialize the Intrusion Kill Chain Graph template.

        Args:
            llm_client (BaseChatModel): The language model client used for kill chain extraction.
            embedder (Embeddings): The embedding model used for stage deduplication.
            extraction_mode (str, optional): 'one_stage' for joint extraction,
                'two_stage' for separate passes. Defaults to "one_stage".
            chunk_size (int, optional): Maximum characters per text chunk. Defaults to 2048.
            chunk_overlap (int, optional): Overlap between chunks. Defaults to 256.
            max_workers (int, optional): Parallel processing workers. Defaults to 10.
            verbose (bool, optional): If True, enables progress logging. Defaults to False.
            **kwargs (Any): Additional parameters for the AutoGraph base class.
        """
        super().__init__(
            node_schema=AttackStageNode,
            edge_schema=KillChainLink,
            node_key_extractor=lambda x: x.stage_name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}->{x.target.strip().lower()}"
            ),
            nodes_in_edge_extractor=lambda x: (
                x.source.strip().lower(),
                x.target.strip().lower(),
            ),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CYBER_KILL_CHAIN_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=CYBER_KILL_CHAIN_NODE_PROMPT,
            prompt_for_edge_extraction=CYBER_KILL_CHAIN_EDGE_PROMPT,
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

        def node_label_extractor(node: AttackStageNode) -> str:
            return f"{node.stage_name}"

        def edge_label_extractor(edge: KillChainLink) -> str:
            return f"{edge.causality}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
