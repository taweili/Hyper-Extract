from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class KnowledgePointNode(BaseModel):
    """
    A discrete unit of knowledge, concept, or skill within a specific curriculum.
    """
    name: str = Field(
        description="Standardized name of the knowledge point or concept."
    )
    level: str = Field(
        description="Difficulty level: 'Primary', 'Intermediate', 'Advanced', 'Expert'."
    )
    concept_type: str = Field(
        description="Pedagogical type: 'Definition', 'Theorem', 'Formula', 'Method', 'Application'."
    )
    description: Optional[str] = Field(
        None, description="A brief pedagogical summary of what this concept entails."
    )

class PrerequisiteRelation(BaseModel):
    """
    Directional dependency indicating that one concept must be learned before another.
    """
    source: str = Field(description="The prerequisite knowledge point (must be learned first).")
    target: str = Field(description="The successor knowledge point (learned after).")
    dependency_type: str = Field(
        "Prerequisite",
        description="Nature of link: 'Prerequisite' (strict), 'Corequisite' (together), 'Recommended' (helpful)."
    )
    weight: float = Field(
        1.0, description="Strength of dependency from 0.0 to 1.0."
    )

# ==============================================================================
# 2. Prompts
# ==============================================================================

EDUCATION_CONSOLIDATED_PROMPT = (
    "You are a Senior Curriculum Architect and Educational Psychologist. Extract the logical structure of knowledge points from the text.\n\n"
    "Rules:\n"
    "- Identify atomic concepts that constitute the learning path.\n"
    "- Establish clear directional dependencies (prerequisites).\n"
    "- Ensure that the resulting graph reflects a sound pedagogical sequence."
)

EDUCATION_NODE_PROMPT = (
    "You are an Educational Psychologist specializing in knowledge decomposition. Your task is to identify all discrete Knowledge Points (Nodes).\n\n"
    "Extraction Rules:\n"
    "- Focus on nouns or noun phrases that represent specific academic concepts, formulas, or methods.\n"
    "- Assign a difficulty level and concept type based on the context.\n"
    "- DO NOT identify relationships or dependencies at this stage."
)

EDUCATION_EDGE_PROMPT = (
    "You are a Curriculum Designer. Given the identified knowledge points, map the Prerequisite Relations (Edges).\n\n"
    "Extraction Rules:\n"
    "- Determine if Concept A is a necessary precursor to Concept B.\n"
    "- Classify the dependency as Prerequisite, Corequisite, or Recommended.\n"
    "- Only create relationships between concepts identified in the provided list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class PrerequisiteMapGraph(AutoGraph[KnowledgePointNode, PrerequisiteRelation]):
    """
    Educational template for building Directed Acyclic Graphs (DAG) of knowledge dependencies.
    Useful for syllabus analysis, learning path generation, and student assessment planning.

    Example Usage:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.en.education.prerequisite_map import PrerequisiteMapGraph
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> graph = PrerequisiteMapGraph(llm, embedder)
        >>> graph.feed_text("To understand Calculus, one must first master Algebra and Functions.")
        >>> graph.extract()
        >>> print(graph.nodes)
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
        """
        Initialize the Prerequisite Map Template.

        Args:
            llm_client (BaseChatModel): The LLM used for extraction.
            embedder (Embeddings): The embedding model for node/edge deduplication.
            extraction_mode (str): 'one_stage' for consolidated extraction, 'two_stage' for separate node/edge passes.
            chunk_size (int): Size of text chunks for processing large documents.
            chunk_overlap (int): Overlap between chunks to preserve context.
            max_workers (int): Number of parallel workers for processing.
            verbose (bool): Whether to print detailed logs during execution.
            **kwargs: Additional parameters passed to the AutoGraph base class.
        """
        super().__init__(
            node_schema=KnowledgePointNode,
            edge_schema=PrerequisiteRelation,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}->{x.target.strip().lower()}"
            ),
            nodes_in_edge_extractor=lambda x: (x.source.strip().lower(), x.target.strip().lower()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=EDUCATION_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=EDUCATION_NODE_PROMPT,
            prompt_for_edge_extraction=EDUCATION_EDGE_PROMPT,
            **kwargs,
        )
