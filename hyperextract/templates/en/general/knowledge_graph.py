from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.graphs import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class Entity(BaseModel):
    """A general entity representing a person, organization, location, or object."""
    name: str = Field(description="The primary name of the entity.")
    category: str = Field(
        description="Category of the entity (e.g., Person, Organization, Location, Event, Object)."
    )
    description: Optional[str] = Field(
        description="A concise summary of the entity and its role in the text."
    )

class Relation(BaseModel):
    """A factual relationship between two entities."""
    source: str = Field(description="The name of the source entity.")
    target: str = Field(description="The name of the target entity.")
    relation: str = Field(description="The type of relationship (e.g., Works for, Located in, Born in, Acquired).")
    details: Optional[str] = Field(description="Additional context or details about this relationship.")

# ==============================================================================
# 2. Prompts
# ==============================================================================

KNOWLEDGE_GRAPH_PROMPT = (
    "You are an expert knowledge extraction system. Your task is to extract a factual knowledge graph "
    "from the provided text. Focus on identifying key entities (People, Organizations, Locations, and relevant Objects) "
    "and the explicit relationships between them.\n\n"
    "Guidelines:\n"
    "- Extract distinct entitles and their factual properties.\n"
    "- Map relationships that describe how entities interact or are connected.\n"
    "- Use clear, concise language for descriptions and relations."
)

KNOWLEDGE_GRAPH_NODE_PROMPT = (
    "Extract all key entities from the text. Focus on identifying People, Organizations, Locations, and important Objects. "
    "Provide a name, a category, and a concise description for each entity."
)

KNOWLEDGE_GRAPH_EDGE_PROMPT = (
    "Identify factual relationships between the following listed entities based on the text. "
    "Focus on interactions like 'works for', 'located in', 'acquired', or 'partnered with'. "
    "Do not hallucinate entities not in the provided list."
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class KnowledgeGraph(AutoGraph[Entity, Relation]):
    """
    A foundational knowledge graph template for factual extraction.
    
    This template is optimized for extracting entities (People, Places, Organizations) 
    and their factual interactions from news articles, biographies, and encyclopedic texts.
    
    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # Initialize the template
        >>> kg = KnowledgeGraph(llm_client=llm, embedder=embedder)
        >>> # Extract knowledge from text
        >>> text = "Steve Jobs co-founded Apple in Cupertino."
        >>> kg.feed_text(text)
        >>> print(kg.nodes)  # Output: [Entity(name='Steve Jobs', ...), Entity(name='Apple', ...)]
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
        Initialize the KnowledgeGraph template.

        Args:
            llm_client: The language model client used for extraction.
            embedder: The embedding model used for entity deduplication and indexing.
            extraction_mode: The strategy for extraction:
                - "one_stage": Extract nodes and edges simultaneously (faster).
                - "two_stage": Extract nodes first, then edges (higher accuracy).
            chunk_size: Maximum number of characters per text chunk.
            chunk_overlap: Number of characters to overlap between chunks.
            max_workers: Maximum number of parallel workers for processing.
            verbose: If True, prints detailed progress logs.
            **kwargs: Additional arguments passed to the AutoGraph constructor.
        """
        super().__init__(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--[{x.relation.lower()}]-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=KNOWLEDGE_GRAPH_PROMPT,
            prompt_for_node_extraction=KNOWLEDGE_GRAPH_NODE_PROMPT,
            prompt_for_edge_extraction=KNOWLEDGE_GRAPH_EDGE_PROMPT,
            **kwargs
        )
