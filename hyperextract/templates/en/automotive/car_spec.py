from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class CarComponent(BaseModel):
    """A vehicle component or specification category (Engine, Battery, ADAS, Transmission)."""
    name: str = Field(description="Name of the car model or specific component.")
    category: str = Field(
        description="Category: 'Model', 'Powertrain', 'Chassis', 'Safety System', 'Infotainment'."
    )
    specification: Optional[str] = Field(description="Detailed specs (e.g., Horsepower, Capacity, Version).")

class CarSystemRelation(BaseModel):
    """The hierarchy or technical relationship between car systems."""
    source: str = Field(description="Parent system or vehicle model.")
    target: str = Field(description="Sub-component or feature.")
    relation_type: str = Field(
        description="Type: 'Equipped with', 'Powered by', 'Integrated with', 'Compatible with'."
    )
    performance_note: Optional[str] = Field(description="Benchmark data or integration details.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

CAR_SPEC_GRAPH_PROMPT = (
    "You are an automotive engineer and technical reviewer. Extract a technical specification graph for a vehicle.\n\n"
    "Guidelines:\n"
    "- Identify the vehicle model and its primary systems (Engine, Motor, Battery, ADAS).\n"
    "- Map the hierarchy of components (e.g., Battery contains Cells, Engine uses Turbocharger).\n"
    "- Capture quantifiable specs like 0-60 mph, Range, Peak Power, and Torque."
)

CAR_SPEC_NODE_PROMPT = (
    "Extract car models and technical components. Focus on names and their measurable specifications (e.g., 500hp, 80kWh)."
)

CAR_SPEC_EDGE_PROMPT = (
    "Define technical dependencies. Show which components belong to which car system. Use relations like 'Powered by' or 'Equipped with'."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class CarSpecGraph(AutoGraph[CarComponent, CarSystemRelation]):
    """
    Template for extracting vehicle technical data and specification hierarchies.
    
    Ideal for competitive analysis, e-commerce car data, and technical documentation.
    
    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI()
        >>> embedder = OpenAIEmbeddings()
        >>> graph = CarSpecGraph(llm_client=llm, embedder=embedder)
        >>> text = "The Tesla Model 3 Performance features a dual-motor AWD system delivering 510 hp."
        >>> graph.feed_text(text)
        >>> print(graph.nodes) # Vehicle and component specs
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
        Initialize the CarSpecGraph template.

        Args:
            llm_client: The language model client for extraction.
            embedder: The embedding model for deduplication.
            extraction_mode: "one_stage" or "two_stage".
            chunk_size: Max characters per chunk.
            chunk_overlap: Overlap between chunks.
            max_workers: Parallel processing workers.
            verbose: Enable progress logging.
            **kwargs: Extra arguments for AutoGraph.
        """
        super().__init__(
            node_schema=CarComponent,
            edge_schema=CarSystemRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.relation_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CAR_SPEC_GRAPH_PROMPT,
            prompt_for_node_extraction=CAR_SPEC_NODE_PROMPT,
            prompt_for_edge_extraction=CAR_SPEC_EDGE_PROMPT,
            **kwargs
        )
