"""
Hyper-RAG: Hypergraph-based Retrieval-Augmented Generation
Extracts and manages multi-entity relationships with support for n-ary hyperedges.
"""

from typing import List
from pydantic import BaseModel, Field
from hyperextract.hypergraphs.base import AutoHypergraph
from langchain_core.messages import AIMessage
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts.chat import ChatPromptTemplate
from ontomem.merger import CustomRuleMerger
from ..utils.logging import logger

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
# Query Analysis Schema
# ============================================================================


class QueryKeywords(BaseModel):
    """Extracted keywords for multi-granular hypergraph retrieval."""

    high_level_keywords: List[str] = Field(
        description="Overarching concepts, themes, or abstract topics (e.g., 'International trade', 'Deforestation')."
    )
    low_level_keywords: List[str] = Field(
        description="Specific entities, concrete details, or tangible objects (e.g., 'Tariffs', 'Rainforest')."
    )


# ============================================================================
# Extraction Prompts
# ============================================================================

Hyper_RAG_NODE_EXTRACTION_PROMPT = """
-Goal-
Identify relevant entities from the text.
Entities will serve as participants in complex events later.\n\n
### Source Text:
"""

Hyper_RAG_EDGE_EXTRACTION_PROMPT = """
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

Hyper_RAG_KEYWORDS_EXTRACTION_PROMPT = """---Role---
You are a helpful assistant tasked with identifying both high-level and low-level keywords in the user's query.

---Goal---
Given the query, extract both high-level and low-level keywords.
- High-level keywords focus on overarching concepts, themes, or abstract topics.
- Low-level keywords focus on specific entities, concrete details, or tangible objects.

---Instructions---
- Output as a structured response with two lists.
- High-level keywords capture broader themes and relationships.
- Low-level keywords capture specific entities and concrete terms.

---Examples---

Example 1:
Query: "How does international trade influence global economic stability?"
High-Level: ["International trade", "Global economic stability", "Economic impact"]
Low-Level: ["Trade agreements", "Tariffs", "Currency exchange", "Imports", "Exports"]

Example 2:
Query: "What are the environmental consequences of deforestation on biodiversity?"
High-Level: ["Environmental consequences", "Deforestation", "Biodiversity loss"]
Low-Level: ["Species extinction", "Habitat destruction", "Carbon emissions", "Rainforest", "Ecosystem"]

Example 3:
Query: "What is the role of education in reducing poverty?"
High-Level: ["Education", "Poverty reduction", "Socioeconomic development"]
Low-Level: ["School access", "Literacy rates", "Job training", "Income inequality"]

---Real Data---
Query: {query}
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
# Hyper_RAG Class
# ============================================================================


class Hyper_RAG(AutoHypergraph[NodeSchema, EdgeSchema]):
    """
    Hyper-RAG: Hypergraph-based Retrieval-Augmented Generation

    Extracts multi-entity relationships (hyperedges) from text documents.

    Features:
    - Two-stage extraction: Entities first, then low-order (binary) and high-order (n-ary) relationships.
    - Custom Key Extractors: Precise deduplication using name-based node keys and sorted participant tuples for edges.
    - Hyperedge Support: Handles complex n-ary relationships connecting multiple entities simultaneously.
    - Structured Knowledge Representation: Pydantic-based Node and Edge schemas with comprehensive attributes.
    - Advanced Indexing: Optimized field-level indexing for efficient semantic search and retrieval."""

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
        Initialize Hyper_RAG engine.

        Args:
            llm_client (BaseChatModel): LLM client for text generation.
            embedder (Embeddings): Embedding model for text embeddings.
            chunk_size (int): Size of text chunks for indexing.
            chunk_overlap (int): Overlap between text chunks for indexing.
            max_workers (int): Maximum number of workers for indexing.
            verbose (bool): Display detailed execution logs and progress information.
        """
        # 1. Define Key Extractors (critical for deduplication)
        # Node key: exact match by name
        node_key_fn = lambda x: x.name

        # Edge key: sorted tuple of participants (set-like behavior for hyperedges)
        edge_key_fn = lambda x: tuple(sorted(x.participants))

        # 2. Edge consistency check: tell AutoHypergraph which nodes this edge connects
        nodes_in_edge_fn = lambda x: x.participants

        # 3. Create custom Mergers with LLM.CUSTOM_RULE strategy
        # Node merger: merges entity descriptions using NODE_MERGE_RULE
        node_merger = CustomRuleMerger(
            key_extractor=node_key_fn,
            llm_client=llm_client,
            item_schema=NodeSchema,
            rule=Hyper_RAG_NODE_MERGE_RULE,
        )

        # Edge merger: merges relationship descriptions using EDGE_MERGE_RULE
        edge_merger = CustomRuleMerger(
            key_extractor=edge_key_fn,
            llm_client=llm_client,
            item_schema=EdgeSchema,
            rule=Hyper_RAG_EDGE_MERGE_RULE,
        )

        # 4. Call parent class initialization
        super().__init__(
            node_schema=NodeSchema,
            edge_schema=EdgeSchema,
            node_key_extractor=node_key_fn,
            edge_key_extractor=edge_key_fn,
            nodes_in_edge_extractor=nodes_in_edge_fn,
            llm_client=llm_client,
            embedder=embedder,
            # Enforce two-stage extraction (nodes first, then edges)
            extraction_mode="two_stage",
            # Inject customized prompts for extraction
            prompt_for_node_extraction=Hyper_RAG_NODE_EXTRACTION_PROMPT,
            prompt_for_edge_extraction=Hyper_RAG_EDGE_EXTRACTION_PROMPT,
            # Pass custom merger instances
            node_strategy_or_merger=node_merger,
            edge_strategy_or_merger=edge_merger,
            # Optimize indexing
            node_fields_for_index=["name", "type", "description"],
            edge_fields_for_index=["keywords", "description"],
            # Other parameters
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
        )

    def chat(
        self,
        query: str,
        top_k_nodes: int = 3,
        top_k_edges: int = 3,
    ) -> AIMessage:
        """Performs a chat-like interaction using hypergraph knowledge.

        Implements the 'Hyper-RAG' dual-level retrieval strategy:
        1. Analyzes the query to extract 'Low-Level' keywords (specific entities/details) and 'High-Level' keywords (overarching themes).
        2. Retrieves Nodes using Low-Level keywords (finding specific entities).
        3. Retrieves Hyperedges using High-Level keywords (finding broader relationships and themes).
        4. Synthesizes an answer based on the combined multi-granular context.

        Args:
            query: User query string.
            top_k_nodes: Number of relevant nodes to retrieve (default: 3). Set to 0 to disable node context.
            top_k_edges: Number of relevant hyperedges to retrieve (default: 3). Set to 0 to disable edge context.

        Returns:
            An AIMessage object containing the LLM-generated response.
            Access the text content via response.content.

        Example:
            >>> # Dual-level retrieval: specific entities + broader themes
            >>> response = hg.chat("How does education reduce poverty?", top_k_nodes=5, top_k_edges=3)
            >>> print(response.content)
        """
        # Step 1: Validation
        if top_k_nodes <= 0 and top_k_edges <= 0:
            raise ValueError(
                "At least one of top_k_nodes or top_k_edges must be positive."
            )

        # Step 2: Extract Keywords (Dual-Level Strategy)
        keyword_prompt = ChatPromptTemplate.from_template(
            Hyper_RAG_KEYWORDS_EXTRACTION_PROMPT
        )
        keyword_chain = keyword_prompt | self.llm_client.with_structured_output(
            QueryKeywords
        )

        # Containers for keywords
        low_level_targets = []
        high_level_targets = []
        extraction_success = False

        try:
            keywords_result: QueryKeywords = keyword_chain.invoke({"query": query})
            if keywords_result.low_level_keywords:
                low_level_targets = keywords_result.low_level_keywords
            if keywords_result.high_level_keywords:
                high_level_targets = keywords_result.high_level_keywords

            extraction_success = True

            if self.verbose:
                logger.info(
                    f"Query Analysis:\n"
                    f"  - Low-Level Targets: {low_level_targets}\n"
                    f"  - High-Level Targets: {high_level_targets}"
                )

        except Exception as e:
            if self.verbose:
                logger.warning(
                    f"Keyword extraction failed ({e}), falling back to raw query."
                )

        context_parts = []

        # Step 3: Retrieve and format nodes context (Using Low-Level Keywords)
        if top_k_nodes > 0:
            found_nodes = []
            if extraction_success and low_level_targets:
                # Search for EACH keyword independently
                for kw in low_level_targets:
                    # Append ALL results directly (no deduplication)
                    found_nodes.extend(self.search_nodes(kw, top_k=top_k_nodes))
            else:
                # Fallback: search with original query
                found_nodes = self.search_nodes(query, top_k=top_k_nodes)

            if found_nodes:
                context_parts.append("=== Relevant Nodes (Entity Level) ===")
                for node in found_nodes:
                    assert isinstance(node, BaseModel), (
                        "Node must be a Pydantic BaseModel"
                    )
                    context_parts.append(node.model_dump_json(indent=2))

        # Step 4: Retrieve and format edges context (Using High-Level Keywords)
        if top_k_edges > 0:
            found_edges = []
            if extraction_success and high_level_targets:
                # Search for EACH keyword independently
                for kw in high_level_targets:
                    # Append ALL results directly (no deduplication)
                    found_edges.extend(self.search_edges(kw, top_k=top_k_edges))
            else:
                # Fallback: search with original query
                found_edges = self.search_edges(query, top_k=top_k_edges)

            if found_edges:
                context_parts.append("=== Relevant Hyperedges (Thematic Level) ===")
                for edge in found_edges:
                    assert isinstance(edge, BaseModel), (
                        "Edge must be a Pydantic BaseModel"
                    )
                    context_parts.append(edge.model_dump_json(indent=2))

        # Step 5: Combine context or use fallback
        if not context_parts:
            context = "No relevant information found in the knowledge base."
        else:
            context = "\n\n".join(context_parts)

        # Step 6: Invoke LLM with structured context
        qa_prompt = ChatPromptTemplate.from_template(
            "Based on the following Hypergraph Knowledge, answer the user's question.\n"
            "The context includes both specific entities (Nodes) found via low-level keywords \n"
            "and broader relationships/themes (Hyperedges) found via high-level keywords.\n\n"
            "{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )

        qa_chain = qa_prompt | self.llm_client
        return qa_chain.invoke({"context": context, "question": query})
