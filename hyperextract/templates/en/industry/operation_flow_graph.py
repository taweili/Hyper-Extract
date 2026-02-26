from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definition
# ==============================================================================


class OperationEntity(BaseModel):
    """
    Operation flow entity, including steps, states, equipment, etc.
    """

    name: str = Field(description="Entity specific name (e.g., turn on auxiliary power, start hydraulic system, check status).")
    category: str = Field(
        description='Category: step, state, equipment.'
    )
    description: Optional[str] = Field(
        None,
        description="Detailed operation description for this entity.",
    )
    expected_result: Optional[str] = Field(
        None,
        description="Expected result after executing this step.",
    )


class OperationTransition(BaseModel):
    """
    Transition relationship between operation steps.
    """

    source: str = Field(description="Current step name.")
    target: str = Field(description="Next step name.")
    relation_type: str = Field(
        description='Relation type: next step, trigger, leads to. Use "next step" for flow sequence.'
    )
    trigger_condition: Optional[str] = Field(
        None,
        description="Condition to trigger the next step.",
    )
    state_change: Optional[str] = Field(
        None,
        description="Description of state change.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an industrial operation flow analysis expert. Extract operation steps, equipment states, and expected results from operating procedure documents.\n\n"
    "Rules:\n"
    "- Identify each operation step and execution sequence.\n"
    "- Record detailed operation content for each step.\n"
    "- Extract equipment state changes and expected results.\n"
    "- Establish transition relationships between steps.\n"
)

_NODE_PROMPT = (
    "You are an industrial operation flow analysis expert. Extract all entities (nodes) from operating procedure documents.\n\n"
    "Extraction Rules:\n"
    "- Identify operation step names.\n"
    "- Identify equipment state names.\n"
    "- Identify related equipment names.\n"
    "- Record operation descriptions and expected results for each step.\n"
    "- Do not establish relationships between steps.\n"
)

_EDGE_PROMPT = (
    "You are an industrial operation flow analysis expert. Based on the entity list, extract transition relationships between operation steps (edges).\n\n"
    "Extraction Rules:\n"
    "- Identify execution sequence of steps (current step → next step).\n"
    "- Extract conditions to trigger the next step.\n"
    "- Record equipment state changes.\n"
    "- Only establish relationships within the provided entity list.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class OperationFlowGraph(AutoGraph[OperationEntity, OperationTransition]):
    """
    Applicable Documents: Operating procedures, start/stop operation tickets, equipment operation manuals, safety operation procedures.

    This template extracts operation steps, equipment states, and expected results from operating procedures.
    It identifies step sequences and state changes in operation flows, providing reference for operation training and safety control.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> operation = OperationFlowGraph(llm_client=llm, embedder=embedder)
        >>> doc = "Startup procedure: 1. Check if power is normal; 2. Turn on main switch of control cabinet; 3. Start motor; 4. Confirm operating status. After power is normal, turn on main switch, after main switch is closed, start motor."
        >>> operation.feed_text(doc)
        >>> operation.show()
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
        Initialize Operation Flow Graph template.

        Args:
            llm_client (BaseChatModel): LLM for entity and relationship extraction.
            embedder (Embeddings): Embedding model for deduplication.
            extraction_mode (str): "one_stage" or "two_stage". Default is "two_stage".
            chunk_size (int): Maximum characters per chunk.
            chunk_overlap (int): Overlap between chunks.
            max_workers (int): Number of parallel processing worker threads.
            verbose (bool): Enable progress logging.
            **kwargs: Additional AutoGraph parameters.
        """
        super().__init__(
            node_schema=OperationEntity,
            edge_schema=OperationTransition,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.relation_type})-->{x.target.strip()}"
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
        Visualize operation flow graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of relationships to retrieve. Default 3.
            top_k_nodes_for_chat (int): Number of entities in chat context. Default 3.
            top_k_edges_for_chat (int): Number of relationships in chat context. Default 3.
        """

        def node_label_extractor(node: OperationEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: OperationTransition) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
