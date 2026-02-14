from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class MedicalEvent(BaseModel):
    """A single medical event within a clinical pathway."""
    event_name: str = Field(description="Event name or diagnostic summary (e.g., 'Admission Diagnosis', 'ECG Exam', 'Splenectomy').")
    event_type: str = Field(description="Type of event (e.g., Chief Complaint, Physical Exam, Lab Test, Diagnosis, Medication, Surgery, Discharge).")
    finding: Optional[str] = Field(description="Specific finding, result, or treatment detail (e.g., 'Hb 90g/L', 'Surgery successful').")

class ClinicalProgression(BaseModel):
    """The progression of medical events over time."""
    source: str = Field(description="Preceding medical event.")
    target: str = Field(description="Subsequent medical event.")
    time: str = Field(description="Relative or absolute time of the event. You MUST resolve fuzzy expressions (e.g., 'a few hours later') into absolute timestamps (e.g., '2024-01-01 10:00') or standard offsets (e.g., '6h post-op') based on the base date/context.")
    status_change: str = Field(description="Change in patient condition or treatment response (e.g., 'Improvement', 'Deterioration', 'Stable').")

# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are an expert clinical documentation analyst. Your task is to extract the diagnostic and therapeutic progression from medical records or clinical pathway documents.\n\n"
    "Analysis Guidelines:\n"
    "1. **Medical Fact Extraction**: Record every significant medical activity (tests, medications, surgeries) and its core results.\n"
    "2. **Temporal Logic Chain**: Establish links in strict chronological order. Use time markers in the text (e.g., '30 mins before surgery', 'next morning') to connect events.\n"
    "3. **Dynamic Tracking**: Focus on describing the evolution of the patient's status (status_change) following clinical interventions.\n"
)

_NODE_PROMPT = (
    "Extract all key clinical nodes from the record, including chief complaints, vital signs, lab results, diagnoses, clinical procedures, and surgeries."
)

_EDGE_PROMPT = (
    "Establish temporal connections between clinical nodes. Resolve chronological cues into specific times or offsets and summarize the dynamic changes in patient condition."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class ClinicalTreatmentTimeline(AutoTemporalGraph[MedicalEvent, ClinicalProgression]):
    """
    Applicable to: [Electronic Medical Records (EMR), Discharge Summaries, Case Reports, Nursing Notes]

    Knowledge pattern for reconstructing a patient's clinical lifecycle as a temporal pathway.

    Leveraging AutoTemporalGraph, this template focuses on the 'Diagnosis-Intervention-Feedback' logic 
    to facilitate retrospective case analysis.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # Initialize template
        >>> pathway = ClinicalTreatmentTimeline(llm_client=llm, embedder=embedder)
        >>> # Feed medical record text
        >>> text = "Patient admitted on Jan 10. Appendectomy performed on Jan 11. Recovered well and discharged on Jan 15."
        >>> pathway.feed_text(text)
        >>> pathway.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: Optional[str] = None,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any
    ):
        """
        Initialize ClinicalTreatmentTimeline template.

        Args:
            llm_client: Language model client.
            embedder: Embeddings model for indexing.
            observation_time: Admission date or reference date.
            extraction_mode: Defaults to 'two_stage' for complex medical history parsing.
            chunk_size: Processing chunk size.
            chunk_overlap: Chunk overlap.
            max_workers: Parallel workers.
            verbose: Enable detailed logging.
            **kwargs: Extra arguments for AutoTemporalGraph.
        """
        super().__init__(
            node_schema=MedicalEvent,
            edge_schema=ClinicalProgression,
            node_key_extractor=lambda x: x.event_name.strip(),
            edge_key_extractor=lambda x: f"{x.source}>>{x.target}",
            time_in_edge_extractor=lambda x: x.time,
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """
        Visualize the clinical treatment timeline.

        Args:
            top_k_for_search: Search context depth.
            top_k_for_chat: Chat context depth.
        """
        def node_label_extractor(node: MedicalEvent) -> str:
            return f"[{node.event_type}] {node.event_name}"

        def edge_label_extractor(edge: ClinicalProgression) -> str:
            return f"({edge.time}) {edge.status_change}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
