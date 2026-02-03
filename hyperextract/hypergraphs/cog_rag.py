"""
COG_RAG: Cognitive-Inspired Dual-Hypergraph RAG System Pattern
Extracts and manages Theme-Entity relationships where Themes act as Hyperedges connecting multiple Entities.
"""

from typing import List, Type, Callable, Tuple, Any
from pydantic import BaseModel, Field, create_model
from hyperextract.hypergraphs.base import AutoHypergraph, AutoHypergraphSchema
from hyperextract.utils.logging import logger
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from ontomem.merger import CustomRuleMerger


# ============================================================================
# Node Schema
# ============================================================================


class NodeSchema(BaseModel):
    """Represents an entity extracted from the source text."""

    name: str = Field(description="Name of the entity")
    type: str = Field(
        description="Entity type (person, organization, geo, event, role, concept, etc.)",
    )
    description: str = Field(
        description="Comprehensive description of the entity's attributes and activities",
    )


# ============================================================================
# Edge Schema (Theme)
# ============================================================================


class ThemeSchema(BaseModel):
    """Represents a Theme or Narrative Arc connecting multiple entities (Hyperedge)."""

    participants: List[str] = Field(
        description="Names of key entities involved in this theme"
    )
    description: str = Field(
        description="A sentence that describes the primary theme, reflecting the main conflict, resolution, or key message"
    )


# ============================================================================
# Edge Schema (Entity Relation)
# ============================================================================


class EdgeSchema(BaseModel):
    """Represents a relationship or event connecting multiple entities (low-order or high-order)."""

    participants: List[str] = Field(
        description="Names of entities involved in this relationship"
    )
    description: str = Field(
        description="Detailed explanation of the relationship or event"
    )
    keywords: List[str] = Field(
        description="List of keywords summarizing the relationship themes (e.g., ['conflict', 'trade', 'alliance'])",
    )
    strength: int = Field(
        ge=1,
        le=10,
        description="Numerical score indicating relationship strength (1-10)",
    )


class EdgeDescriptionList(BaseModel):
    """Intermediate schema for identifying edge concepts first."""

    items: List[str] = Field(
        description="List of primary edge concepts/themes identified"
    )


# ============================================================================
# Extraction Prompts
# ============================================================================


DEFAULT_CONTEXTUAL_NODE_PROMPT = """-Goal-
You are given a list of "Primary Concepts" (Themes/Events/Relationships) identified from the text.
Your task is to Populate these concepts with their specific Participant Entities.

CRITICAL RULES:
1. Extract ALL key participants for each concept.
2. Nodes must be specific entities (People, Organizations, Locations, Concepts, etc.).
"""

COG_RAG_THEME_PROMPT = """
-Goal-
Analyze the text to identify the primary themes (narrative arcs).
A Theme is a high-level concept, conflict, or main idea acting as a Hyperedge.
"""

COG_RAG_KEY_ENTITY_PROMPT = """
-Goal-
You are given a list of "Primary Themes" identified from the text.
Your task is to populate these themes with key entities (Participants).
"""

COG_RAG_NODE_EXTRACTION_PROMPT = """
-Goal-
Identify relevant entities from the text.
Entities will serve as participants in complex events later.
### Source Text:
"""

COG_RAG_EDGE_EXTRACTION_PROMPT = """
-Goal-
You are an expert hypergraph knowledge extraction assistant. 
Extract "Hyperedges" that represent relationships, events, or thematic groupings involving MULTIPLE entities (2 or more) simultaneously.

-Definition-
A Hyperedge is a unified concept for any connection. 
It treats all involved entities as **participants** in a shared context 
(e.g., a conversation, a joint mission, a conflict, or a shared concept).

-Constraints-
1. You MUST ONLY use names from the "Allowed Entities" list provided below.
2. Do NOT create edges for entities that represent strictly different concepts with no interaction.
3. Ensure every edge has at least 2 participants.

"""

# ============================================================================
# Merge Templates for LLM.CUSTOM_RULE Strategy
# ============================================================================

COG_RAG_NODE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Entity.

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **name/type**: Keep the most frequent or precise value.
2. **description**: Synthesize a single, comprehensive description containing all unique details from the input descriptions. Write it in the third person. Resolve any contradictions coherently.
"""

COG_RAG_THEME_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Theme.

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **participants**: Keep the list (they should be identical for the same theme key).
2. **description**: Synthesize a global theme description that encompasses the narrative details from all input themes. Write it in the third person.
"""

COG_RAG_EDGE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Relationship.

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **participants**: Keep the list (they should be identical for the same relationship key).
2. **description**: Synthesize a single, comprehensive description covering the relationship dynamics from all inputs. Write it in the third person.
3. **keywords**: Combine keyword lists from all inputs, removing duplicates.
4. **strength**: Calculate the average of the input strengths (round to nearest integer).
"""

# ============================================================================
# Theme Hypergraph (Layer 1: Macro Narrative)
# ============================================================================


class EdgeAutoHypergraph(AutoHypergraph[NodeSchema, EdgeSchema]):
    """EdgeAutoHypergraph - Edge-First extraction: Extract relationships/themes first, then entities.

    Extraction Strategy: Two-Stage (Edge-First)
    1. Stage 1: Extract all Edges/Concepts (high-level themes, events, narratives).
    2. Stage 2: Extract Nodes (entities) that participate in those specific Edges.

    Suitable for:
    - Narrative-driven knowledge graphs (Theme -> Character)
    - Event-driven extraction (Event -> Participant)
    """

    def __init__(
        self,
        node_schema: Type[NodeSchema],
        edge_schema: Type[EdgeSchema],
        node_key_extractor: Callable[[NodeSchema], str],
        edge_key_extractor: Callable[[EdgeSchema], str],
        nodes_in_edge_extractor: Callable[[EdgeSchema], Tuple[str, ...]],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        prompt_for_node_extraction: str = "",
        **kwargs: Any,
    ):
        """Initialize EdgeAutoHypergraph and build dynamic Stage 2 schemas.

        Args:
            prompt_for_node_extraction: In pure Edge-First context, this is the "Stage 2 Prompt".
                                        (Extract Nodes given Edges).
        """
        super().__init__(
            node_schema=node_schema,
            edge_schema=edge_schema,
            node_key_extractor=node_key_extractor,
            edge_key_extractor=edge_key_extractor,
            nodes_in_edge_extractor=nodes_in_edge_extractor,
            llm_client=llm_client,
            embedder=embedder,
            prompt_for_node_extraction=prompt_for_node_extraction,
            **kwargs,
        )

        # Build Stage 2 Schema (Edges containing nested Nodes)
        # We assume the edge schema has a 'participants' field (List[str]).
        # We create a new model where 'participants' is List[NodeSchema].

        # 1. Base fields from EdgeSchema (excluding participants)
        valid_fields = {
            k: (v.annotation, v)
            for k, v in edge_schema.model_fields.items()
            if k != "participants"
        }

        # 2. Add Nested Participants field
        valid_fields["participants"] = (
            List[node_schema],
            Field(description="List of entities participating in this concept/edge."),
        )

        # 3. Create Contextual Edge Model
        self.contextual_edge_schema = create_model(
            f"Contextual{edge_schema.__name__}", **valid_fields
        )

        # 4. Create Result List Model
        self.stage2_result_schema = create_model(
            f"{edge_schema.__name__}FirstResult",
            items=(List[self.contextual_edge_schema], Field(default_factory=list)),
        )

        # Set default prompt if not provided
        if not prompt_for_node_extraction:
            self.node_prompt = DEFAULT_CONTEXTUAL_NODE_PROMPT

    def _extract_data(self, text: str) -> AutoHypergraphSchema:
        """Main extraction logic dispatcher (Edge-First)."""
        if self.extraction_mode == "two_stage":
            raw_graph = self._extract_data_by_two_stage(text)
        elif self.extraction_mode == "one_stage":
            raise NotImplementedError(
                "Single-stage extraction not yet supported for EdgeAutoHypergraph."
            )
        else:
            raise ValueError(f"Invalid extraction_mode: {self.extraction_mode}")

        # Note: Dangle pruning might be less critical here since nodes are derived from edges,
        # but we keep it for consistency if nodes are merged globally.
        return self._prune_dangling_edges(raw_graph)

    def _extract_data_by_two_stage(self, text: str) -> AutoHypergraphSchema:
        """Extract edges/themes first, then entities within those contexts (batch processing).

        Process:
        1. Split text into chunks.
        2. Batch extract Edge Concepts (Theme Strings) for all chunks.
        3. Batch extract Nodes and Full Edges for all chunks (using Edge Concepts as context).
        4. Merge all partial results into one global hypergraph.
        """
        # 1. Prepare chunks
        if len(text) <= self.chunk_size:
            chunks = [text]
        else:
            chunks = self.text_splitter.split_text(text)

        if self.verbose:
            logger.info(f"Edge-First Extraction: Processing {len(chunks)} chunks...")

        # 2. Stage 1: Identify Edge Concepts (Strings)
        edge_concepts_lists = self._extract_edge_concepts_batch(chunks)

        # 3. Stage 2: Extract Nodes and Full Edges (Context-aware)
        chunk_results = self._extract_details_batch(chunks, edge_concepts_lists)

        # 4. Global Merge
        # chunk_results is List[AutoHypergraphSchema]
        return self.merge_batch_data(chunk_results)

    def _extract_edge_concepts_batch(self, chunks: List[str]) -> List[List[str]]:
        """Stage 1: Batch extract edge concept strings."""
        # This uses the 'prompt_for_edge_extraction' (self.edge_prompt) to find concepts
        # We assume the prompt is geared towards finding a LIST of themes/concepts.

        prompt_template = ChatPromptTemplate.from_template(
            f"{self.edge_prompt}\n\n### Source Text:\n{{chunk_text}}"
        )
        chain = prompt_template | self.llm_client.with_structured_output(
            EdgeDescriptionList
        )

        inputs = [{"chunk_text": chunk} for chunk in chunks]
        results = chain.batch(inputs, config={"max_concurrency": self.max_workers})

        return [res.items if res else [] for res in results]

    def _extract_details_batch(
        self, chunks: List[str], edge_concepts_list: List[List[str]]
    ) -> List[AutoHypergraphSchema]:
        """Generic Stage 2: Extract entities and details given identified edge concepts."""

        # 1. Prepare Inputs
        inputs = []
        valid_map = {}
        for i, (chunk, concepts) in enumerate(zip(chunks, edge_concepts_list)):
            if concepts:
                concepts_str = "- " + "\n- ".join(concepts)
                inputs.append({"chunk_text": chunk, "edge_concepts": concepts_str})
                valid_map[len(inputs) - 1] = i

        if not inputs:
            return [self.graph_schema(nodes=[], edges=[]) for _ in chunks]

        # 2. Chain Execution
        # Uses self.node_prompt as the instruction for contextual node extraction
        prompt = ChatPromptTemplate.from_template(
            f"{self.node_prompt}\n\n### Primary Concepts/Themes:\n{{edge_concepts}}\n\n### Source Text:\n{{chunk_text}}"
        )
        chain = prompt | self.llm_client.with_structured_output(
            self.stage2_result_schema
        )

        results = chain.batch(inputs, config={"max_concurrency": self.max_workers})

        # 3. Transform Nested Result -> Flat AutoHypergraphSchema
        final_schemas = [
            self.graph_schema(nodes=[], edges=[]) for _ in range(len(chunks))
        ]

        for i, result in enumerate(results):
            if not result or not result.items:
                continue

            original_idx = valid_map[i]
            current_nodes = []
            current_edges = []

            for item in result.items:
                # item is a ContextualEdge (has nested participants=List[Node])

                # Extract Nodes
                nested_nodes = item.participants
                node_names = []
                for n in nested_nodes:
                    current_nodes.append(n)
                    node_names.append(self.node_key_extractor(n))

                # Reconstruct Flat Edge
                edge_data = item.model_dump()
                edge_data["participants"] = sorted(
                    node_names
                )  # Ensure sorted for consistency

                new_edge = self.edge_schema(**edge_data)
                current_edges.append(new_edge)

            final_schemas[original_idx] = self.graph_schema(
                nodes=current_nodes, edges=current_edges
            )

        return final_schemas


# ============================================================================


class Cog_RAG_ThemeLayer(EdgeAutoHypergraph[NodeSchema, ThemeSchema]):
    """
    Layer 1 of Cog_RAG: Theme-First Extraction.
    Extracts Themes (Hyperedges) and Key Entities (Nodes).
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = True,
    ):
        """
        Initialize COG_RAG engine.

        Args:
            llm_client (BaseChatModel): LLM client for text generation.
            embedder (Embeddings): Embedding model for text embeddings.
            chunk_size (int): Size of text chunks for indexing.
            chunk_overlap (int): Overlap between text chunks for indexing.
            max_workers (int): Maximum number of workers for indexing.
            verbose (bool): Display detailed execution logs and progress information.
        """
        # 1. Define Key Extractors
        # Node key: exact match by name
        node_key_fn = lambda x: x.name

        # Edge key: sorted tuple of participants
        edge_key_fn = lambda x: tuple(sorted(x.participants))

        # 2. Edge consistency check: tell AutoHypergraph which nodes this edge connects
        nodes_in_edge_fn = lambda x: x.participants

        # 3. Create custom Mergers with LLM.CUSTOM_RULE strategy
        node_merger = CustomRuleMerger(
            key_extractor=node_key_fn,
            llm_client=llm_client,
            item_schema=NodeSchema,
            rule=COG_RAG_NODE_MERGE_RULE,
        )

        edge_merger = CustomRuleMerger(
            key_extractor=edge_key_fn,
            llm_client=llm_client,
            item_schema=ThemeSchema,
            rule=COG_RAG_THEME_MERGE_RULE,
        )

        # 4. Call parent class initialization
        super().__init__(
            node_schema=NodeSchema,
            edge_schema=ThemeSchema,
            node_key_extractor=node_key_fn,
            edge_key_extractor=edge_key_fn,
            nodes_in_edge_extractor=nodes_in_edge_fn,
            llm_client=llm_client,
            embedder=embedder,
            # Enforce two-stage extraction
            extraction_mode="two_stage",
            # Inject customized prompts for extraction
            # prompt_for_node_extraction acts as the Stage 2 (Edge -> Node) prompt
            prompt_for_node_extraction=COG_RAG_KEY_ENTITY_PROMPT,
            prompt_for_edge_extraction=COG_RAG_THEME_PROMPT,
            # Pass custom merger instances
            node_strategy_or_merger=node_merger,
            edge_strategy_or_merger=edge_merger,
            # Optimize indexing
            node_fields_for_index=["name", "type", "description"],
            edge_fields_for_index=["description"],
            # Other parameters
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )


# ============================================================================
# Detail Hypergraph (Layer 2: Micro Relations)
# ============================================================================


class Cog_RAG_DetailLayer(AutoHypergraph[NodeSchema, EdgeSchema]):
    """
    Layer 2 of Cog_RAG: Entity-First Extraction.
    Extracts Entities (Nodes) and Semantic Relationships (Hyperedges).
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = True,
    ):
        """
        Initialize COG_RAG Entity-Relation engine.
        """
        node_key_fn = lambda x: x.name
        edge_key_fn = lambda x: tuple(sorted(x.participants))
        nodes_in_edge_fn = lambda x: x.participants

        node_merger = CustomRuleMerger(
            key_extractor=node_key_fn,
            llm_client=llm_client,
            item_schema=NodeSchema,
            rule=COG_RAG_NODE_MERGE_RULE,
        )

        edge_merger = CustomRuleMerger(
            key_extractor=edge_key_fn,
            llm_client=llm_client,
            item_schema=EdgeSchema,
            rule=COG_RAG_EDGE_MERGE_RULE,
        )

        super().__init__(
            node_schema=NodeSchema,
            edge_schema=EdgeSchema,
            node_key_extractor=node_key_fn,
            edge_key_extractor=edge_key_fn,
            nodes_in_edge_extractor=nodes_in_edge_fn,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode="two_stage",
            prompt_for_node_extraction=COG_RAG_NODE_EXTRACTION_PROMPT,
            prompt_for_edge_extraction=COG_RAG_EDGE_EXTRACTION_PROMPT,
            node_strategy_or_merger=node_merger,
            edge_strategy_or_merger=edge_merger,
            node_fields_for_index=["name", "type", "description"],
            edge_fields_for_index=["description", "keywords"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )


# ============================================================================
# Main System Class (Wrapper)
# ============================================================================


class Cog_RAG:
    """
    Cognitive-Inspired Dual-Hypergraph RAG System.

    Combines two Hypergraph Layers:
    1. Theme Layer (Cog_RAG_ThemeLayer): Captures macro narratives and themes.
    2. Detail Layer (Cog_RAG_DetailLayer): Captures micro entity relationships.
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = True,
    ):
        self.theme_layer = Cog_RAG_ThemeLayer(
            llm_client=llm_client,
            embedder=embedder,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )
        self.detail_layer = Cog_RAG_DetailLayer(
            llm_client=llm_client,
            embedder=embedder,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )
        self.llm = llm_client
        self.verbose = verbose

    def feed_text(self, text: str):
        """Feed text to both hypergraph layers."""
        if self.verbose:
            logger.info("Cog_RAG: Feeding text to Theme Layer...")
        self.theme_layer.feed_text(text)

        if self.verbose:
            logger.info("Cog_RAG: Feeding text to Detail Layer...")
        self.detail_layer.feed_text(text)

    def build_index(self):
        """Build indices for both layers."""
        if self.verbose:
            logger.info("Cog_RAG: Building indices...")
        self.theme_layer.build_index()
        self.detail_layer.build_index()

    def search(self, query: str, top_k_themes: int = 3, top_k_entities: int = 3):
        """
        Dual-Layer Search.
        Strategy:
        1. Macro: Search for Themes in ThemeLayer (Edge-First).
        2. Micro: Search for Entities in DetailLayer (Node-First).
        """
        # 1. Macro Context: Themes
        themes = self.theme_layer.search_edges(query, top_k=top_k_themes)

        # 2. Micro Context: Entities (Nodes)
        # Note: The user requested searching for "Specific Entities" in the second step.
        entities = self.detail_layer.search_nodes(query, top_k=top_k_entities)

        return {"themes": themes, "entities": entities}

    def chat(self, query: str, top_k_themes: int = 3, top_k_entities: int = 3):
        """Generate an answer using context from both layers."""
        results = self.search(query, top_k_themes, top_k_entities)

        context_parts = []
        if results["themes"]:
            context_parts.append("=== MACRO THEMES (Narrative Context) ===")
            for t in results["themes"]:
                context_parts.append(
                    f"- {t.description} (Involved: {', '.join(t.participants)})"
                )

        if results["entities"]:
            context_parts.append("\n=== MICRO ENTITIES (Specific Details) ===")
            for e in results["entities"]:
                context_parts.append(f"- [{e.type}] {e.name}: {e.description}")

        if not context_parts:
            context = "No relevant information found."
        else:
            context = "\n".join(context_parts)

        prompt = ChatPromptTemplate.from_template(
            "You are an intelligent assistant using a Dual-Layer Hypergraph Knowledge Base.\n"
            "Use the provided Themes (Macro) and Key Entities (Micro) to answer the user's question comprehensively.\n\n"
            "{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )

        chain = prompt | self.llm
        return chain.invoke({"context": context, "question": query})

    def dump(self, folder_path: str):
        """Save both extracted graphs."""
        import os

        self.theme_layer.dump(os.path.join(folder_path, "theme_layer"))
        self.detail_layer.dump(os.path.join(folder_path, "detail_layer"))

    @property
    def nodes(self):
        """Return combined unique nodes from both layers (simple aggregation)."""
        # Note: This is a property for valid introspection, but nodes are managed separately.
        # We perform a simple name-based deduction for display.
        seen = set()
        unique = []
        for n in self.theme_layer.nodes + self.detail_layer.nodes:
            if n.name not in seen:
                seen.add(n.name)
                unique.append(n)
        return unique

    @property
    def edges(self):
        """Return all edges (Themes + Relations)."""
        return self.theme_layer.edges + self.detail_layer.edges
