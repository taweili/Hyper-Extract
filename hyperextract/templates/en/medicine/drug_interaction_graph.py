from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class MedicalSubstance(BaseModel):
    """A drug, active ingredient, or dietary supplement."""
    name: str = Field(description="The generic name or major brand name of the substance (e.g., 'Aspirin', 'Warfarin').")
    category: str = Field(description="Therapeutic category (e.g., 'NSAID', 'Anticoagulant').")
    description: Optional[str] = Field(description="Primary function or indication of the substance.")

class DrugInteraction(BaseModel):
    """Properties of the interaction between two substances."""
    source: str = Field(description="First drug/substance name.")
    target: str = Field(description="Second drug/substance name.")
    interaction_type: str = Field(description="Nature of interaction (e.g., Contraindicated, Use with caution, Synergistic, Antagonistic).")
    severity: str = Field(description="Severity levels (e.g., Major, Moderate, Minor).")
    mechanism: str = Field(description="Pharmacological mechanism (e.g., 'Competition for CYP enzymes leading to increased blood levels').")
    recommendation: str = Field(description="Clinical action/advice (e.g., 'Strictly avoid combination', 'Monitor PT/INR').")

# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = (
    "You are a professional clinical pharmacologist. Your task is to extract drug-drug interactions from medical literature, labels, or guidelines.\n\n"
    "Extraction Rules:\n"
    "1. **Normalization**: Prefer generic names (INN). If only brand names are present, record them as is.\n"
    "2. **Rigorous Mapping**: Accurately capture the interaction type, severity, and the underlying medical mechanism.\n"
    "3. **Clinical Guidance**: Always include the clinical recommendation or precautionary advice mentioned in the text.\n"
    "- Ensure every interaction connects nodes that are identified in the medical substance list."
)

_NODE_PROMPT = (
    "Extract all medical substances, chemical names, or supplements mentioned in the text. Clearly identify their category and primary pharmacological effect."
)

_EDGE_PROMPT = (
    "Identify explicit interactions between the extracted substances. Specify the type, severity, and detailed mechanism for each interaction based on the text."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class DrugInteractionGraph(AutoGraph[MedicalSubstance, DrugInteraction]):
    """
    Applicable to: [Drug Labels/Inserts, Pharmacopoeias, Clinical Practice Guidelines, Medical Journals]

    Knowledge pattern for constructing drug contraindication and synergy networks.

    Using a two-stage extraction process, this template parses rigorous medical literature 
    to create structured interaction graphs for clinical decision support.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # Initialize template
        >>> drug_map = DrugInteractionGraph(llm_client=llm, embedder=embedder)
        >>> # Feed text from a drug label
        >>> text = "Combining Warfarin with Aspirin significantly increases bleeding risk (Major). Avoid concurrent use."
        >>> drug_map.feed_text(text)
        >>> drug_map.show()
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
        **kwargs: Any
    ):
        """
        Initialize DrugInteractionGraph template.

        Args:
            llm_client: Language model client.
            embedder: Embeddings model for deduplication.
            extraction_mode: "one_stage" for quick drafts, "two_stage" for rigorous medical extraction.
            chunk_size: Max characters per processing chunk.
            chunk_overlap: Overlap between chunks.
            max_workers: Parallel workers.
            verbose: Enable detailed logging.
            **kwargs: Extra arguments for AutoGraph.
        """
        super().__init__(
            node_schema=MedicalSubstance,
            edge_schema=DrugInteraction,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: f"{x.source}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
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
        Visualize the drug interaction graph.

        Args:
            top_k_for_search: Nodes/edges for search.
            top_k_for_chat: Nodes/edges for chat.
        """
        def node_label_extractor(node: MedicalSubstance) -> str:
            return node.name.capitalize()

        def edge_label_extractor(edge: DrugInteraction) -> str:
            return f"{edge.interaction_type} ({edge.severity})"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
