"""
HyperGraph_RAG: Integration of EdgeAutoHypergraph (Edge-First Extraction).
Matches the structure of Hyper_RAG regarding Schemas and Mergers.
"""

from typing import List
from pydantic import BaseModel, Field
from hyperextract.hypergraphs.base import EdgeAutoHypergraph
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
# Edge Schema
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


# ============================================================================
# Extraction Prompts (Edge-First)
# ============================================================================

HyperGraph_RAG_THEME_EXTRACTION_PROMPT = """
-Goal-
Identify the key "Themes", "Narratives", or "Complex Events" present in the text.
A Theme/Event should represent a significant interaction or grouping involving multiple participants.

-Output-
Return a list of these Themes/Events as descriptive strings.
Do not list participants data formats yet, just the essence of the event (e.g., "The secret meeting at Titan Station", "The ambush in the Aurora Sector").
"""

HyperGraph_RAG_CONTEXT_NODE_PROMPT = """
-Goal-
You are an expert knowledge extractor.
You have been given a list of "Themes/Events" (Hyperedges) that occurred in the text.
Your job is to identify the specific ENTITIES (participants) involved in each theme.

-Output-
For each Theme, list the entities that participated.
"""


# ============================================================================
# Merge Templates for LLM.CUSTOM_RULE Strategy
# ============================================================================

Hyper_RAG_NODE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Entity.

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **name/type**: Keep the most frequent or precise value.
2. **description**: Synthesize a single, comprehensive description containing all unique details from the input descriptions. Write it in the third person. Resolve any contradictions coherently.
"""

Hyper_RAG_EDGE_MERGE_RULE = """You are an intelligent data merging assistant.
You will receive a list of objects representing the same Hyperedge (Relationship/Event).

Your task is to merge them into a SINGLE object exactly matching the schema.

Merge strategy:
1. **participants**: Keep the list (they should be identical for the same hyperedge key).
2. **description**: Synthesize a single, comprehensive description covering the relationship dynamics from all inputs. Write it in the third person.
3. **keywords**: Combine keyword lists from all inputs, removing duplicates.
4. **strength**: Calculate the average of the input strengths (round to nearest integer).
"""

# ============================================================================
# HyperGraph_RAG Class
# ============================================================================


class HyperGraph_RAG(EdgeAutoHypergraph[NodeSchema, EdgeSchema]):
    """
    HyperGraph_RAG: Hypergraph-based RAG with Edge-First Extraction Strategy.

    Difference from Hyper_RAG:
    - Uses EdgeAutoHypergraph (extracts Themes first, then Entities).
    - Suitable for high-level narrative understanding where Themes map to specific Actors.
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
        Initialize HyperGraph_RAG engine.

        Args:
            llm_client (BaseChatModel): LLM client for text generation.
            embedder (Embeddings): Embedding model for text embeddings.
            chunk_size (int): Size of text chunks for extraction.
            chunk_overlap (int): Overlap between text chunks.
            max_workers (int): Maximum number of workers for extraction.
            verbose (bool): Display detailed logs.
        """
        # 1. Define Key Extractors
        node_key_fn = lambda x: x.name
        edge_key_fn = lambda x: tuple(sorted(x.participants))
        nodes_in_edge_fn = lambda x: x.participants

        # 2. Setup Mergers
        node_merger = CustomRuleMerger(
            key_extractor=node_key_fn,
            llm_client=llm_client,
            item_schema=NodeSchema,
            rule=Hyper_RAG_NODE_MERGE_RULE,
        )

        edge_merger = CustomRuleMerger(
            key_extractor=edge_key_fn,
            llm_client=llm_client,
            item_schema=EdgeSchema,
            rule=Hyper_RAG_EDGE_MERGE_RULE,
        )

        # 3. Initialize EdgeAutoHypergraph (Parent)
        super().__init__(
            node_schema=NodeSchema,
            edge_schema=EdgeSchema,
            node_key_extractor=node_key_fn,
            edge_key_extractor=edge_key_fn,
            nodes_in_edge_extractor=nodes_in_edge_fn,
            llm_client=llm_client,
            embedder=embedder,
            # Prompts
            # Stage 1: Extract Themes
            prompt_for_edge_extraction=HyperGraph_RAG_THEME_EXTRACTION_PROMPT,
            # Stage 2: Extract Particles given Themes
            prompt_for_node_extraction=HyperGraph_RAG_CONTEXT_NODE_PROMPT,
            # Merger strategies
            node_strategy_or_merger=node_merger,
            edge_strategy_or_merger=edge_merger,
            # Indexing optimization
            node_fields_for_index=["name", "type", "description"],
            edge_fields_for_index=["keywords", "description"],
            # BaseAutoType Params
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )

