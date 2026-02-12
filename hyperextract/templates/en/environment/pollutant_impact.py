from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types.graph import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class EnvironmentalEntity(BaseModel):
    """An entity in the environmental pollution domain."""

    name: str = Field(description="Name of the pollutant, contaminated site, or impacted entity.")
    entity_type: str = Field(
        description="Type: 'Pollutant' (chemical, particle, etc.), 'Source' (factory, vehicle), 'Target' (water, air, soil, organism)."
    )
    description: Optional[str] = Field(
        None, description="Additional details such as chemical properties, location, or characteristics."
    )


class PollutantImpact(BaseModel):
    """The impact relationship between a source/pollutant and a target/receptor."""

    source: str = Field(description="The pollutant or contamination source.")
    target: str = Field(description="The impacted entity (ecosystem, organism, location).")
    impact_type: str = Field(
        description="Type of impact: 'bioaccumulation', 'toxicity', 'contamination', 'ecosystem damage', 'health effect'."
    )
    severity: Optional[str] = Field(
        None, description="Severity level: 'critical', 'high', 'moderate', 'low'. Include any quantitative measures if available."
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = """
You are an environmental scientist specializing in pollution assessment and ecosystem impact analysis.
Your task is to extract pollution sources, pollutants, and their environmental impacts from reports, monitoring data, and news articles.

Guidelines:
1. Identify all pollutants mentioned (e.g., Mercury, PM2.5, Plastic, Carbon dioxide).
2. Identify pollution sources (factories, vehicles, agricultural runoff, etc.) and impacted targets (rivers, air, soil, human populations, wildlife).
3. Extract the causal relationships: which pollutant affects which entity and how.
4. Capture severity or quantitative impact information if mentioned (e.g., "50 mg/L concentration", "critical contamination level").
5. Be precise about the directionality: pollution flows FROM source TO target.

Output Format:
- Pollutants and impacted entities should be distinct nodes.
- Impacts should have a clear source (pollutant/source), target (receptor), impact type, and severity if available.
"""

_NODE_PROMPT = """
You are an environmental scientist specializing in pollution assessment.
Your task is to extract ONLY environmental entities (pollutants, sources, and targets) during the first extraction stage.
Do not identify pollution impacts yet - focus solely on finding all entities.

Guidelines:
1. Identify all pollutants mentioned (chemicals, particles, compounds).
2. Identify all pollution sources (factories, vehicles, sites).
3. Identify all impacted targets (water bodies, organisms, human populations, ecosystems).
4. For each entity, capture: name, entity_type, and any relevant characteristics.
5. Avoid duplicates: consolidate references to the same entity.

Output Format:
- Each entity should be a distinct node with name, type (Pollutant/Source/Target), and description.
"""

_EDGE_PROMPT = """
You are an environmental scientist analyzing pollution impacts.
Your task is to extract ONLY the causal relationships between given entities during the second extraction stage.
You will be provided with environmental entities (nodes). Your job is to identify pollution impacts between them.

Guidelines:
1. Given the list of confirmed entities, find all pollution impact relationships in the text.
2. For each impact, capture: source (pollutant/source entity), target (impacted entity), impact_type, and severity.
3. Preserve directionality: pollutant flows FROM source TO target.
4. Only extract impacts between given entities; ignore stands-alone entity mentions.
5. Include quantitative measures (concentrations, severity levels) if available.

Output Format:
- Each impact is an edge: Source → Target with impact_type and severity.
"""

# ==============================================================================
# 3. Template Class
# =============================================================================="


class PollutantImpactMap(AutoGraph[EnvironmentalEntity, PollutantImpact]):
    """
    Knowledge graph template for environmental pollution tracking and impact assessment.

    Transforms environmental monitoring reports and sustainability analyses into structured
    pollution source-target relationships, enabling environmental health risk analysis.

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4")
        >>> embedder = OpenAIEmbeddings()
        >>> 
        >>> pollutant_map = PollutantImpactMap(llm_client=llm, embedder=embedder)
        >>> text = "Mercury discharged from the factory contaminated the river, causing fish toxicity at critical levels."
        >>> pollutant_map.feed_text(text)
        >>> pollutant_map.show()  # Visualize pollution impacts and severity
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
        """Initialize the PollutantImpactMap template.

        Args:
            llm_client (BaseChatModel): Language model client for extracting pollutants and impacts.
            embedder (Embeddings): Embedding model for indexing pollutants, sources, and impacted targets.
            extraction_mode (str, optional): Extraction strategy. Defaults to "one_stage".
                - "one_stage": Extract pollutants and impacts simultaneously (faster).
                - "two_stage": Extract pollutants first, then impacts (higher accuracy).
            chunk_size (int, optional): Maximum characters per text chunk. Defaults to 2048.
            chunk_overlap (int, optional): Overlapping characters between chunks for context preservation. Defaults to 256.
            max_workers (int, optional): Maximum concurrent extraction workers for parallel processing. Defaults to 10.
            verbose (bool, optional): If True, prints detailed extraction progress and pollution tracking logs. Defaults to False.
            **kwargs: Additional arguments passed to the AutoGraph base class.
        """
        super().__init__(
            node_schema=EnvironmentalEntity,
            edge_schema=PollutantImpact,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.impact_type.lower()})-->{x.target.strip()}",
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
        """Visualize the pollutant impact network for environmental assessment.

        Displays pollution sources, pollutants, and impacted targets with severity information using OntoSight.
        Internally defines frontend labels for entities (name + entity_type) and impacts (impact_type + severity).

        Args:
            top_k_nodes_for_search (int, optional): Number of environmental entities (pollutants/sources/targets) to retrieve for search context. Defaults to 3.
            top_k_edges_for_search (int, optional): Number of impact relationships to retrieve for search context. Defaults to 3.
            top_k_nodes_for_chat (int, optional): Number of environmental entities to retrieve for chat context. Defaults to 3.
            top_k_edges_for_chat (int, optional): Number of impact relationships to retrieve for chat context. Defaults to 3.
        """

        def node_label_extractor(node: EnvironmentalEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: PollutantImpact) -> str:
            severity = f" [{edge.severity}]" if edge.severity else ""
            return f"{edge.impact_type}{severity}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
