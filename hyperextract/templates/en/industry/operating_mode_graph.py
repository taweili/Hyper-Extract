from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definition
# ==============================================================================


class ModeEntity(BaseModel):
    """
    Mode entity, including modes and conditions.
    """

    name: str = Field(description="Entity name (e.g., automatic operation mode, manual debug mode, standby mode, emergency stop mode, press start button, press stop button, fault occurs).")
    category: str = Field(
        description='Category: mode, condition. Modes include automatic, manual debug, standby, etc.; conditions include start button, stop button, fault signal, etc.'
    )
    description: Optional[str] = Field(
        None,
        description="Description of this entity.",
    )
    load_range: Optional[str] = Field(
        None,
        description="Load range (e.g., 0-50%, 50-80%, 80-100%), only valid for mode category.",
    )


class ModeTransition(BaseModel):
    """
    Transition relationship between modes, or trigger relationship between conditions and modes.
    """

    source: str = Field(description="Source entity name (mode or condition).")
    target: str = Field(description="Target entity name (mode or condition).")
    relation_type: str = Field(
        description='Relation type: switches to, triggers. Use "switches to" for mode-to-mode switching, "triggers" for condition triggering mode.'
    )
    transition_condition: Optional[str] = Field(
        None,
        description="Switching condition (e.g., press start button, press stop button, fault occurs).",
    )
    transition_procedure: Optional[str] = Field(
        None,
        description="Switching procedure.",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an industrial equipment mode analysis expert. Extract mode and condition entities and their relationships from operating procedure documents.\n\n"
    "Rules:\n"
    "- Identify various operation modes, such as automatic, manual debug, standby, emergency stop, etc.\n"
    "- Identify various trigger conditions, such as press start button, press stop button, fault occurs, etc.\n"
    "- Identify applicable conditions and load ranges for each mode.\n"
    "- Extract switching relationships between modes (switches to).\n"
    "- Extract trigger relationships from conditions to modes (triggers).\n"
)

_NODE_PROMPT = (
    "You are an industrial equipment mode analysis expert. Extract all entities (nodes) from operating procedure documents.\n\n"
    "Extraction Rules:\n"
    "- Identify mode names (e.g., automatic operation mode, manual debug mode, standby mode, emergency stop mode).\n"
    "- Identify condition names (e.g., press start button, press stop button, fault occurs, return to normal).\n"
    "- Assign category for each entity (mode/condition).\n"
    "- Record load range for each mode.\n"
    "- Do not establish relationships between entities.\n"
)

_EDGE_PROMPT = (
    "You are an industrial equipment mode analysis expert. Based on the entity list, extract relationships between modes and conditions (edges).\n\n"
    "Extraction Rules:\n"
    "- Identify switching relationships between modes (source mode switches to target mode).\n"
    "- Identify trigger relationships from conditions to modes (condition triggers target mode).\n"
    "- Use relation type as \"switches to\" or \"triggers\".\n"
    "- Only establish relationships within the provided entity list.\n"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class OperatingModeGraph(AutoGraph[ModeEntity, ModeTransition]):
    """
    Applicable Documents: Operating procedures, equipment operation manuals, mode switching manuals.

    This template extracts mode types and switching conditions from operating procedures.
    It identifies switching conditions and procedures between different modes.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> mode = OperatingModeGraph(llm_client=llm, embedder=embedder)
        >>> doc = "Equipment has two operation modes: automatic mode and manual mode. Press start button to switch from standby to automatic mode..."
        >>> mode.feed_text(doc)
        >>> mode.show()
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
        Initialize Operating Mode Graph template.

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
            node_schema=ModeEntity,
            edge_schema=ModeTransition,
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
        Visualize operating mode graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of entities to retrieve. Default 3.
            top_k_edges_for_search (int): Number of relationships to retrieve. Default 3.
            top_k_nodes_for_chat (int): Number of entities in chat context. Default 3.
            top_k_edges_for_chat (int): Number of relationships in chat context. Default 3.
        """

        def node_label_extractor(node: ModeEntity) -> str:
            load = f" [{node.load_range}]" if node.load_range else ""
            return f"{node.name} ({node.category}){load}"

        def edge_label_extractor(edge: ModeTransition) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
