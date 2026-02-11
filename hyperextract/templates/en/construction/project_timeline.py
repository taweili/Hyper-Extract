from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class MilestoneTaskNode(BaseModel):
    """
    A specific task, milestone, or phase in a construction project schedule.
    """

    task_name: str = Field(
        description="Operational name of the task (e.g., 'Foundation Pouring')."
    )
    phase: str = Field(
        description="Project phase: 'Pre-con', 'Substructure', 'Superstructure', 'Fit-out', 'Commissioning'."
    )
    duration_estimate: Optional[str] = Field(
        None, description="Estimated time required (e.g., '14 days', '2 months')."
    )
    responsible_party: Optional[str] = Field(
        None, description="Subcontractor or team lead in charge."
    )


class TemporalDependency(BaseModel):
    """
    A time-based link indicating task sequencing.
    """

    source: str = Field(description="The predecessor task.")
    target: str = Field(description="The successor task.")
    timestamp: str = Field(
        description="Temporal marker or sequence ID (e.g., 'Phase 1', 'Step 2', or a specific date/time)."
    )
    dependency_type: str = Field(
        "Finish-to-Start",
        description="Type: 'Finish-to-Start (FS)', 'Start-to-Start (SS)', 'Finish-to-Finish (FF)', 'Start-to-Finish (SF)'.",
    )
    lag_time: Optional[str] = Field(
        None,
        description="Wait time between tasks (e.g., '3 days for concrete curing').",
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

CONSTRUCTION_TEMPORAL_CONSOLIDATED_PROMPT = (
    "You are a Senior Project Planner and Scheduler (P6/MS Project expert). Extract the construction project timeline.\n\n"
    "Rules:\n"
    "- Identify granular tasks and major milestones as Nodes.\n"
    "- Establish clear temporal dependencies (Edges) using industry-standard logic (FS, SS, etc.).\n"
    "- Capture durations and curing/lag times where mentioned.\n"
    "- Focus on the critical path and sequencing logic."
)

CONSTRUCTION_TEMPORAL_NODE_PROMPT = (
    "Identify all tasks, scheduled activities, and project milestones.\n\n"
    "Rules:\n"
    "- Extract action-oriented task names.\n"
    "- Group tasks into project phases and identify responsible parties.\n"
    "- DO NOT identify sequences or dependencies yet."
)

CONSTRUCTION_TEMPORAL_EDGE_PROMPT = (
    "Link construction tasks based on their logical sequence in time.\n\n"
    "Rules:\n"
    "- Define the predecessor and successor for each link.\n"
    "- Classify the link type (FS is default if not specified).\n"
    "- Identify any required lag times (e.g., waiting for inspection or drying).\n"
    "- Only link tasks from the provided list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class ProjectSchedulingTimeline(
    AutoTemporalGraph[MilestoneTaskNode, TemporalDependency]
):
    """
    Template for extracting project schedules and Critical Path Method (CPM) networks.

    Ideal for schedule risk analysis, delay tracking, and progress monitoring.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> timeline = ProjectSchedulingTimeline(llm_client=llm, embedder=embedder)
        >>> timeline.feed_text("Excavation must finish before the foundation slab can be poured.")
        >>> print(timeline.nodes)  # Access tasks and milestones
        >>> print(timeline.edges)  # Access temporal dependencies
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
        Initialize the Project Scheduling Timeline template.

        Args:
            llm_client (BaseChatModel): The language model client used for schedule extraction.
            embedder (Embeddings): The embedding model used for task and dependency deduplication.
            extraction_mode (str, optional): 'one_stage' for joint extraction,
                'two_stage' for separate passes. Defaults to "one_stage".
            chunk_size (int, optional): Maximum characters per text chunk. Defaults to 2048.
            chunk_overlap (int, optional): Overlap between chunks. Defaults to 256.
            max_workers (int, optional): Parallel processing workers. Defaults to 10.
            verbose (bool, optional): If True, enables progress logging. Defaults to False.
            **kwargs (Any): Additional parameters for the AutoTemporalGraph base class.
        """
        super().__init__(
            node_schema=MilestoneTaskNode,
            edge_schema=TemporalDependency,
            node_key_extractor=lambda x: x.task_name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}--[{x.dependency_type}]-->{x.target.strip().lower()}"
            ),
            nodes_in_edge_extractor=lambda x: (
                x.source.strip().lower(),
                x.target.strip().lower(),
            ),
            time_in_edge_extractor=lambda x: x.timestamp.strip(),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CONSTRUCTION_TEMPORAL_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=CONSTRUCTION_TEMPORAL_NODE_PROMPT,
            prompt_for_edge_extraction=CONSTRUCTION_TEMPORAL_EDGE_PROMPT,
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

        def node_label_extractor(node: MilestoneTaskNode) -> str:
            info = f" ({node.phase})" if getattr(node, "phase", None) else ""
            return f"{node.task_name}{info}"

        def edge_label_extractor(edge: TemporalDependency) -> str:
            return f"{edge.dependency_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
