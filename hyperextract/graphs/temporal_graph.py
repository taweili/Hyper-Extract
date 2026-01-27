"""Generic temporal graph implementation supporting custom schemas with time-aware deduplication."""

from typing import Type, Callable, Tuple, Any, List, Optional
from datetime import datetime
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.embeddings import Embeddings
from ontomem.merger import MergeStrategy, BaseMerger

from .base import AutoGraph, NodeSchema, EdgeSchema, NodeListSchema, EdgeListSchema

# ==============================================================================
# Prompt Definition
# ==============================================================================

GENERIC_TEMPORAL_NODE_PROMPT = """
You are a professional entity extraction specialist.
Your task is to extract all important entities (Nodes) from the text.

# Core Principles
1. **Comprehensiveness**: Extract persons, organizations, locations, events, concepts, and other noun-based entities.
2. **Accuracy**: Keep entity names consistent with the source text.
3. **Exclude Time Expressions**: **NEVER** extract dates, years, or time periods (e.g., "2023", "last year", "today") as entity nodes!
   Time is an attribute of relationships, not a node.
4. **Exclude Pure Numbers**: Do not extract standalone amounts or numeric values as independent nodes.

### Source Text:
"""

# Note: This prompt contains {observation_date} placeholder for dynamic injection during extraction
GENERIC_TEMPORAL_EDGE_PROMPT = """
You are an expert temporal knowledge extraction specialist.
Extract meaningful relationships (edges) between the provided entities, paying STRICT attention to temporal correctness.

### Temporal Extraction Rules
Current Observation Date: {observation_date}

1. **Relative Time Resolution**: You MUST resolve relative time expressions based on the Observation Date.
   - "last year" -> Calculate the year before {observation_date}
   - "yesterday" -> Calculate the date before {observation_date}
   - "currently" -> The relationship is active (implies no end date)
   - "this month" -> First day of the month in {observation_date}
   - "last month" -> First day of the month before {observation_date}

2. **Explicit Dates**: Keep explicit dates (e.g., "2023", "2024-01-01") exactly as written.

3. **Missing Time**: If no time information is present, leave time fields empty. DO NOT hallucinate dates.

### General Constraints
1. ONLY extract edges connecting entities from the known entity list provided below.
2. DO NOT create edges involving entities that are not listed.
3. Use the defined schema fields for time (e.g., t_start, t_end, timestamp) as specified in your output format.

"""


class AutoTemporalGraph(AutoGraph[NodeSchema, EdgeSchema]):
    """
    Generic Temporal Graph Extractor (AutoTemporalGraph).

    A flexible implementation supporting user-defined Node and Edge schemas with:
    - **Schema Agnosticism**: Support any user-defined Node and Edge Pydantic models.
    - **Temporal-Aware Deduplication**: Time information is integrated into edge deduplication logic.
    - **Dynamic Time Injection**: Observation Date is injected during extraction for relative time resolution.

    Key Design:
    - `edge_timestamp_extractor`: Function to extract time info from edges (e.g., lambda x: x.year).
      This ensures (A, rel, B) @ 2020 and (A, rel, B) @ 2021 are treated as different edges.
    - Wrapper around `edge_key_extractor`: Combines base relation key with timestamp key.
    - Dynamic Prompt Injection: Observation Date is injected into edge extraction prompts at runtime.

    Example:
        >>> from pydantic import BaseModel, Field
        >>> 
        >>> class MyEntity(BaseModel):
        ...     name: str
        ...     category: str = "Unknown"
        >>> 
        >>> class MyTemporalEdge(BaseModel):
        ...     src: str
        ...     dst: str
        ...     relation: str
        ...     year: Optional[str] = None
        >>> 
        >>> kg = AutoTemporalGraph(
        ...     node_schema=MyEntity,
        ...     edge_schema=MyTemporalEdge,
        ...     node_key_extractor=lambda x: x.name,
        ...     edge_key_extractor=lambda x: f"{x.src}|{x.relation}|{x.dst}",
        ...     edge_timestamp_extractor=lambda x: x.year or "",
        ...     nodes_in_edge_extractor=lambda x: (x.src, x.dst),
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     observation_date="2024-01-15"
        ... )
    """

    def __init__(
        self,
        node_schema: Type[NodeSchema],
        edge_schema: Type[EdgeSchema],
        node_key_extractor: Callable[[NodeSchema], str],
        edge_key_extractor: Callable[[EdgeSchema], str],
        edge_timestamp_extractor: Callable[[EdgeSchema], str],
        nodes_in_edge_extractor: Callable[[EdgeSchema], Tuple[str, str]],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        observation_date: str | None = None,
        extraction_mode: str = "two_stage",
        **kwargs: Any,
    ):
        """
        Initialize AutoTemporalGraph.

        Args:
            node_schema: User-defined Node Pydantic model.
            edge_schema: User-defined Edge Pydantic model with time fields.
            node_key_extractor: Function to extract unique key from node (e.g., lambda x: x.name).
            edge_key_extractor: Function to extract base relationship key (e.g., lambda x: f"{x.src}|{x.relation}|{x.dst}").
            edge_timestamp_extractor: Function to extract time fingerprint from edge (e.g., lambda x: x.year).
                This is critical for differentiating edges at different times.
            nodes_in_edge_extractor: Function to extract (source_key, target_key) from edge.
            llm_client: LangChain BaseChatModel for extraction.
            embedder: LangChain Embeddings for semantic operations.
            observation_date: Date context for relative time resolution (default: today in YYYY-MM-DD format).
            extraction_mode: "one_stage" or "two_stage" (default: "two_stage").
            **kwargs: Additional arguments passed to parent AutoGraph (e.g., prompt_for_node_extraction,
                     node_strategy_or_merger, edge_strategy_or_merger, etc.).
        """
        # Set observation date (default: today)
        self.observation_date = observation_date or datetime.now().strftime("%Y-%m-%d")
        
        # Store raw extractors for instance recreation (_create_empty_instance)
        self.raw_timestamp_extractor = edge_timestamp_extractor
        self.raw_edge_key_extractor = edge_key_extractor

        # -----------------------------------------------------------
        # Core Logic 1: Decorate Edge Key Extractor
        # -----------------------------------------------------------
        # Combine "base relation fingerprint" (e.g., A|rel|B) with "time fingerprint" (e.g., 2023)
        # This ensures OMem treats (A, rel, B) @ t1 and (A, rel, B) @ t2 as different records
        def temporal_edge_key_wrapper(edge: EdgeSchema) -> str:
            base_key = edge_key_extractor(edge)
            time_key = edge_timestamp_extractor(edge)
            # Only append timestamp if valid time info exists
            if time_key:
                return f"{base_key}|{time_key}"
            return base_key

        # -----------------------------------------------------------
        # Core Logic 2: Prepare Edge Extraction Prompt
        # -----------------------------------------------------------
        # Extract user-provided edge prompt or use default
        edge_prompt = kwargs.pop("prompt_for_edge_extraction", GENERIC_TEMPORAL_EDGE_PROMPT)
        
        # Store the template (with {observation_date} placeholder) for later injection
        self.temporal_edge_prompt_template = edge_prompt

        # Initialize parent AutoGraph
        super().__init__(
            node_schema=node_schema,
            edge_schema=edge_schema,
            node_key_extractor=node_key_extractor,
            edge_key_extractor=temporal_edge_key_wrapper,  # Inject wrapped extractor
            nodes_in_edge_extractor=nodes_in_edge_extractor,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            prompt_for_edge_extraction=edge_prompt,  # Pass template with placeholder
            # Use default node prompt if not provided
            prompt_for_node_extraction=kwargs.pop(
                "prompt_for_node_extraction", GENERIC_TEMPORAL_NODE_PROMPT
            ),
            **kwargs,
        )

    # ==============================================================================
    # Override Extraction Methods to Dynamically Inject Observation Date
    # ==============================================================================

    def _extract_edges_batch(
        self, chunks: List[str], node_lists: List[NodeListSchema[NodeSchema]]
    ) -> List[EdgeListSchema[EdgeSchema]]:
        """
        Override: Inject observation_date into edge extraction chain during two-stage extraction.

        This method is called during the second stage (edge extraction from nodes + text).
        It dynamically injects the observation_date into the LLM chain inputs.

        Args:
            chunks: List of text chunks.
            node_lists: List of extracted node schemas for each chunk.

        Returns:
            List of extracted edge schemas.
        """
        inputs = []
        for chunk, node_list in zip(chunks, node_lists):
            nodes = node_list.items if node_list else []
            if not nodes:
                node_context = "No specific entities identified in this chunk."
            else:
                node_keys = [self.node_key_extractor(n) for n in nodes]
                node_context = "Known entities: " + ", ".join(node_keys)

            # Build input dictionary with dynamic observation_date injection
            inputs.append(
                {
                    "chunk_text": chunk,
                    "node_context": node_context,
                    "observation_date": self.observation_date,  # <--- DYNAMIC INJECTION
                }
            )

        # Create prompt template with placeholder for observation_date
        # The self.temporal_edge_prompt_template contains {observation_date} which will be filled
        prompt_template = ChatPromptTemplate.from_template(
            f"{self.temporal_edge_prompt_template}{{node_context}}\n\n### Source Text:\n{{chunk_text}}"
        )
        llm_chain = prompt_template | self.llm_client.with_structured_output(
            self.edge_list_schema
        )

        return llm_chain.batch(inputs, config={"max_concurrency": self.max_workers})

    def _extract_data_by_one_stage(self, text: str) -> Any:
        """
        Override: Inject observation_date into one-stage extraction if the prompt contains the placeholder.

        Args:
            text: Input text to extract.

        Returns:
            Extracted graph.
        """
        # Check if prompt template contains observation_date placeholder
        needs_date = "{observation_date}" in self.prompt

        template_str = f"{self.prompt}{{chunk_text}}"
        prompt_template = ChatPromptTemplate.from_template(template_str)
        llm_chain = prompt_template | self.llm_client.with_structured_output(
            self.graph_schema
        )

        # Prepare base input
        base_input = {}
        if needs_date:
            base_input["observation_date"] = self.observation_date

        # Process text (chunked if necessary)
        if len(text) <= self.chunk_size:
            inp = {"chunk_text": text, **base_input}
            graph = llm_chain.invoke(inp)
            graph_list = [graph]
        else:
            chunks = self.text_splitter.split_text(text)
            inputs = [{"chunk_text": chunk, **base_input} for chunk in chunks]
            graph_list = llm_chain.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )

        return self.merge_batch_data(graph_list)

    def _create_empty_instance(self) -> "AutoTemporalGraph[NodeSchema, EdgeSchema]":
        """
        Override: Recreate instance with all temporal-specific attributes.

        This is called by the parent class to create new instances during certain operations.
        We need to preserve raw extractors and temporal configuration.
        """
        return self.__class__(
            node_schema=self.node_schema,
            edge_schema=self.edge_schema,
            node_key_extractor=self.node_key_extractor,
            edge_key_extractor=self.raw_edge_key_extractor,  # Pass original (unwrapped)
            edge_timestamp_extractor=self.raw_timestamp_extractor,  # Pass original
            nodes_in_edge_extractor=self.nodes_in_edge_extractor,
            llm_client=self.llm_client,
            embedder=self.embedder,
            observation_date=self.observation_date,
            extraction_mode=self.extraction_mode,
            node_strategy_or_merger=self.node_merger,
            edge_strategy_or_merger=self.edge_merger,
            prompt_for_node_extraction=self.node_prompt,
            prompt_for_edge_extraction=self.temporal_edge_prompt_template,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            max_workers=self.max_workers,
            verbose=self.verbose,
            node_fields_for_index=self.node_fields_for_index,
            edge_fields_for_index=self.edge_fields_for_index,
        )
