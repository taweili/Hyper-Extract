from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class LogicNode(BaseModel):
    """A node representing a claim, evidence, or premise in an argument."""

    statement: str = Field(description="The central claim, fact, or observation.")
    node_type: str = Field(
        description="Type of node: Claim (main point), Evidence (supporting data), Premise (underlying assumption)."
    )
    source_attribution: Optional[str] = Field(
        description="Where or who this logic point originates from."
    )


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

_PROMPT = (
    "You are a logical analyst. Extract the reasoning structure from the text into a directed graph.\n\n"
    "Guidelines:\n"
    "- Identify the main claims (conclusions) and the evidence or premises that lead to them.\n"
    "- Explicitly map how one statement supports or contradicts another.\n"
    "- Do not just extract facts; extract the 'argument' and 'reasoning' flow."
)

_NODE_PROMPT = (
    "Extract the individual building blocks of the argument. Identify core claims, supporting evidence, "
    "and underlying premises. For each, determine its type and note any source attribution mentioned."
)

_EDGE_PROMPT = (
    "Map the logical flow between the extracted claims and evidence. Focus on how statements "
    "Support, Contradict, or Lead to one another. Ensure every edge represents a step in the reasoning chain."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class LogicGraph(AutoGraph[LogicNode, LogicRelation]):
    """
    A template for analyzing reasoning, arguments, and causal chains.

    This template is designed to map out the logical structure of analytical reports,
    scientific papers, or debate transcripts. It captures claims, evidence, and
    the logical links (Support/Contradict) between them.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # Initialize the template
        >>> lg = LogicGraph(llm_client=llm, embedder=embedder)
        >>> # Extract logic from text
        >>> text = "The climate is warming because carbon levels are rising."
        >>> lg.feed_text(text)
        >>> print(lg.edges)  # Output shows: Carbon levels rising --(Supports)--> Climate is warming
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
        Initialize the LogicGraph template.

        Args:
            llm_client: The language model client used for extraction.
            embedder: The embedding model used for logic point deduplication and indexing.
            extraction_mode: The strategy for extraction:
                - "one_stage": Extract nodes and edges simultaneously (faster).
                - "two_stage": Extract nodes first, then edges (higher accuracy).
            chunk_size: Maximum number of characters per text chunk.
            chunk_overlap: Number of characters to overlap between chunks.
            max_workers: Maximum number of parallel workers for processing.
            verbose: If True, prints detailed progress logs.
            **kwargs: Additional arguments passed to the AutoGraph constructor.
        """
        super().__init__(
            node_schema=LogicNode,
            edge_schema=LogicRelation,
            node_key_extractor=lambda x: x.statement.strip(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.inference.lower()})-->{x.target.strip()}"
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
        Visualize the graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of nodes to retrieve for search context. Default 3.
            top_k_edges_for_search (int): Number of edges to retrieve for search context. Default 3.
            top_k_nodes_for_chat (int): Number of nodes to retrieve for chat context. Default 3.
            top_k_edges_for_chat (int): Number of edges to retrieve for chat context. Default 3.
        """

        def node_label_extractor(node: LogicNode) -> str:
            return f"{node.statement}"

        def edge_label_extractor(edge: LogicRelation) -> str:
            return f"{edge.inference}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
