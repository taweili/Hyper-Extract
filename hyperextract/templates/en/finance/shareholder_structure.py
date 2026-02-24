"""Shareholder Structure - Extracts ownership hierarchies from prospectuses.

Maps shareholder percentages, controlling paths, and parent-subsidiary relations
from S-1 filings and proxy statements for ultimate controller analysis.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class OwnershipEntity(BaseModel):
    """
    An entity in the ownership structure.
    """

    name: str = Field(
        description="Name of the entity (e.g., person, fund, holding company, trust)."
    )
    entity_type: str = Field(
        description="Type: 'Individual', 'Institutional Investor', 'Holding Company', 'Venture Capital', "
        "'Private Equity', 'Trust', 'Government Entity', 'Issuing Company'."
    )
    description: Optional[str] = Field(
        None,
        description="Additional details (e.g., 'Co-founder and CEO', 'Series B lead investor').",
    )


class OwnershipEdge(BaseModel):
    """
    An ownership or control relationship between entities.
    """

    source: str = Field(description="The owner/parent entity name.")
    target: str = Field(description="The owned/subsidiary entity name.")
    relationship_type: str = Field(
        description="Type: 'Direct Ownership', 'Indirect Ownership', 'Beneficial Ownership', "
        "'Voting Control', 'Board Seat', 'Parent-Subsidiary'."
    )
    ownership_percentage: Optional[str] = Field(
        None,
        description="Percentage ownership (e.g., '15.3%', '51%', 'Controlling interest').",
    )
    share_class: Optional[str] = Field(
        None,
        description="Class of shares (e.g., 'Class A', 'Class B (10x voting)', 'Preferred Series C').",
    )
    shares_held: Optional[str] = Field(
        None,
        description="Number of shares held (e.g., '45,000,000 shares').",
    )
    voting_power: Optional[str] = Field(
        None,
        description="Voting power percentage if different from ownership (e.g., '65% voting power').",
    )
    lock_up_period: Optional[str] = Field(
        None,
        description="Post-IPO lock-up period if applicable (e.g., '180 days').",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a corporate governance analyst. Extract the ownership structure including shareholders, "
    "holding companies, and their ownership relationships from this prospectus or proxy filing.\n\n"
    "Rules:\n"
    "- Identify all significant shareholders (5%+ beneficial owners).\n"
    "- Extract ownership percentages and share classes.\n"
    "- Map parent-subsidiary and holding company structures.\n"
    "- Note dual-class voting structures and voting power differentials.\n"
    "- Capture lock-up periods and post-IPO restrictions."
)

_NODE_PROMPT = (
    "You are a corporate governance analyst. Extract all ownership entities (Nodes).\n\n"
    "Extraction Rules:\n"
    "- Identify individuals, institutional investors, holding companies, and trusts.\n"
    "- Identify the issuing company itself.\n"
    "- Classify each entity by type.\n"
    "- DO NOT extract ownership relationships at this stage."
)

_EDGE_PROMPT = (
    "You are a corporate governance analyst. Given the entities, extract ownership "
    "and control relationships (Edges).\n\n"
    "Extraction Rules:\n"
    "- Connect owners to their holdings.\n"
    "- Extract ownership percentages and share classes.\n"
    "- Note voting power differentials.\n"
    "- Capture lock-up periods.\n"
    "- Only create edges between nodes that exist in the provided lists."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class ShareholderStructure(AutoGraph[OwnershipEntity, OwnershipEdge]):
    """
    Applicable to: S-1 Prospectuses, Proxy Statements (DEF 14A), Schedule 13D/G filings,
    Annual Reports (Beneficial Ownership sections), IPO Filings.

    Template for extracting and mapping corporate ownership structures. Enables
    ultimate controller analysis, voting power assessment, and post-IPO lock-up tracking.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> ownership = ShareholderStructure(llm_client=llm, embedder=embedder)
        >>> prospectus = "The following table sets forth beneficial ownership: CEO holds 15.3%..."
        >>> ownership.feed_text(prospectus)
        >>> ownership.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize the Shareholder Structure template.

        Args:
            llm_client (BaseChatModel): The LLM for ownership extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage".
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Parallel processing workers.
            verbose (bool): Enable progress logging.
            **kwargs: Additional arguments for AutoGraph.
        """
        super().__init__(
            node_schema=OwnershipEntity,
            edge_schema=OwnershipEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}--({x.relationship_type})-->{x.target.strip().lower()}"
            ),
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
        """
        Visualize the shareholder structure graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of relationships to retrieve. Default 3.
            top_k_nodes_for_chat (int): Entities for chat context. Default 3.
            top_k_edges_for_chat (int): Relationships for chat context. Default 3.
        """

        def node_label_extractor(node: OwnershipEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: OwnershipEdge) -> str:
            pct = f" {edge.ownership_percentage}" if edge.ownership_percentage else ""
            return f"{edge.relationship_type}{pct}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
