from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class LabOperation(BaseModel):
    """
    A specific step or action in a chemical or biological protocol (e.g., 'Centrifugation', 'Titration').
    """

    op_id: str = Field(description="Action name (e.g., 'Centrifuge', 'Heat', 'Add').")
    equipment: Optional[str] = Field(
        None, description="Device used (e.g., 'Microcentrifuge', 'Bunsen burner')."
    )
    reagents_added: List[str] = Field(
        default_factory=list,
        description="Chemicals introduced during this specific step.",
    )
    precautions: Optional[str] = Field(
        None, description="Safety or accuracy warnings (e.g., 'Keep on ice')."
    )


class ProtocolTransition(BaseModel):
    """
    The sequential transition between protocol steps, capturing duration and order.
    """

    transition_id: str = Field(description="Unique id for the step transition.")
    source_step: str = Field(description="The preceding operation.")
    target_step: str = Field(description="The succeeding operation.")
    duration: Optional[str] = Field(
        None,
        description="Time spent in or between steps (e.g., '15 mins', 'Overnight').",
    )
    timestamp: str = Field(
        description="The sequence order or relative time marker (e.g., 'T+0', 'Step 2')."
    )
    wait_condition: Optional[str] = Field(
        None, description="Condition to proceed (e.g., 'Until precipitate forms')."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

PROTOCOL_CONSOLIDATED_PROMPT = (
    "You are a laboratory technician specializing in protocol documentation. Extract sequential lab steps.\n\n"
    "Rules:\n"
    "- Represent each operation as a Node.\n"
    "- Represent the sequence and duration between operations as Temporal Edges.\n"
    "- Capture specific reagents/equipment associated with each step.\n"
    "- Map the timeline precisely (e.g., 'Step 1' -> 'Step 2')."
)

PROTOCOL_NODE_PROMPT = (
    "You are a laboratory technician. Your task is to identify individual protocol operations (Nodes).\n\n"
    "Extraction Rules:\n"
    "- Identify discrete actions (e.g., Centrifuge, Incubate, Titrate).\n"
    "- Note the equipment used and any reagents added during that specific step.\n"
    "- Capture safety precautions associated with the operation.\n"
    "- DO NOT establish the sequence or timing between steps at this stage."
)

PROTOCOL_EDGE_PROMPT = (
    "You are a laboratory technician. Given the list of laboratory operations, extract the sequential flow (Edges).\n\n"
    "Extraction Rules:\n"
    "- Connect the source step to the target step in chronological order.\n"
    "- Identify the duration of the transition and the specific timestamp or sequence number.\n"
    "- Record any wait conditions required before moving to the next operation.\n"
    "- Only reference operations that exist in the provided operations list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class LabProtocolTemporal(AutoTemporalGraph[LabOperation, ProtocolTransition]):
    """
    Temporal graph template for capturing step-by-step laboratory procedures and experimental workflows.
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
        super().__init__(
            node_schema=LabOperation,
            edge_schema=ProtocolTransition,
            node_key_extractor=lambda x: x.op_id.strip(),
            edge_key_extractor=lambda x: x.transition_id.strip(),
            nodes_in_edge_extractor=lambda x: (
                x.source_step.strip(),
                x.target_step.strip(),
            ),
            time_in_edge_extractor=lambda x: x.timestamp.strip(),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=PROTOCOL_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=PROTOCOL_NODE_PROMPT,
            prompt_for_edge_extraction=PROTOCOL_EDGE_PROMPT,
            **kwargs,
        )
