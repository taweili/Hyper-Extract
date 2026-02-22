"""Operational Procedure - Extract the specific sequential steps for declaration, approval, or operations specified in regulations.

Suitable for operation guidance, SOP process visualization, etc.
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class ProcedureStep(BaseModel):
    """Procedure step node"""
    stepId: str = Field(description="Step ID, e.g., Step 1, Step 2")
    name: str = Field(description="Step name")
    description: str = Field(description="Detailed step description")
    role: str = Field(description="Executor role", default="")
    inputRequired: str = Field(description="Required inputs/materials", default="")
    outputResult: str = Field(description="Output/result", default="")


class ProcedureTransition(BaseModel):
    """Procedure transition edge"""
    source: str = Field(description="Source step ID")
    target: str = Field(description="Target step ID")
    condition: str = Field(description="Transition condition", default="")
    details: str = Field(description="Detailed explanation", default="")


_PROMPT = """You are a professional process analysis expert. Please extract the specific sequential steps for declaration, approval, or operations specified in regulations from the text to build an operational procedure flowchart.

### Node Extraction Rules
1. Extract all process steps
2. Assign an ID to each step (e.g., Step 1, Step 2)
3. Add a name and detailed description to each step
4. Record the executor role (if available)
5. Record required inputs or materials (if available)
6. Record output or result (if available)

### Edge Extraction Rules
1. Only create transition edges from extracted steps
2. Record the sequential relationship between steps
3. Record transition conditions (if available)
4. Record detailed explanations (if available)

### Constraints
- Ensure the sequential order of process steps is accurate
- Maintain objectivity and accuracy, do not add information not in the text

### Source text:
"""

_NODE_PROMPT = """You are a professional process step recognition expert. Please extract all process steps as nodes from the text.

### Extraction Rules
1. Extract all process steps
2. Assign an ID to each step (e.g., Step 1, Step 2)
3. Add a name and detailed description to each step
4. Record the executor role (if available)
5. Record required inputs or materials (if available)
6. Record output or result (if available)

### Source text:
"""

_EDGE_PROMPT = """You are a professional process transition recognition expert. Please extract the sequential relationship between steps from the given step list.

### Constraints
1. Only extract edges from the known step list below
2. Do not create unlisted steps

"""


class OperationalProcedure(AutoGraph[ProcedureStep, ProcedureTransition]):
    """
    Applicable documents: Operation manuals, SOPs, compliance guidelines, approval processes

    Function introduction:
    Extract the specific sequential steps for declaration, approval, or operations specified in regulations. Suitable for operation guidance, SOP process visualization, etc.

    Example:
        >>> template = OperationalProcedure(llm_client=llm, embedder=embedder)
        >>> template.feed_text("Universe First Slacker Company Leave Approval Process...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize operational procedure template.
        
        Args:
            llm_client: LLM client for knowledge extraction
            embedder: Embedding model for semantic search
            extraction_mode: Extraction mode, either "one_stage" (extract nodes and edges simultaneously)
                or "two_stage" (extract nodes first, then edges), default: "two_stage"
            max_workers: Maximum number of worker threads, default: 10
            verbose: Whether to output detailed logs, default: False
            **kwargs: Other technical parameters, passed to base class
        """
        super().__init__(
            node_schema=ProcedureStep,
            edge_schema=ProcedureTransition,
            node_key_extractor=lambda x: x.stepId,
            edge_key_extractor=lambda x: f"{x.source}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
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
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        Display operational procedure flowchart.
        
        Args:
            top_k_for_search: Number of nodes/edges to return for semantic search, default: 3
            top_k_for_chat: Number of nodes/edges to use for chat, default: 3
        """
        def node_label_extractor(node: ProcedureStep) -> str:
            return f"{node.stepId}: {node.name}"
        
        def edge_label_extractor(edge: ProcedureTransition) -> str:
            if edge.condition:
                return edge.condition
            return "→"
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
