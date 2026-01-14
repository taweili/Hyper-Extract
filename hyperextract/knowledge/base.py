from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, Any, Dict, Type, List
from datetime import datetime
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate


T = TypeVar("T", bound=BaseModel)


# ===================== Knowledge Base Class =====================


class BaseKnowledge(ABC, Generic[T]):
    """Unified knowledge base class integrating extraction, storage, aggregation, and evolution.

    This abstract base class provides a complete framework for managing structured knowledge
    extracted from text. It handles the full lifecycle from extraction to serialization.

    Responsibilities:
        - Extract structured knowledge from text using LLM
        - Automatically handle long text chunking and parallel processing
        - Store and aggregate extracted knowledge with configurable merge strategies
        - Build and maintain vector indices for semantic search
        - Support knowledge evolution and optimization
        - Provide serialization and deserialization capabilities
    """

    def __init__(
        self,
        data_schema: Type[T],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        prompt: str = "",
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
        max_workers: int = 10,
        show_progress: bool = True,
    ):
        """Initialize the knowledge object with schema and processing configuration.

        Args:
            data_schema: Pydantic BaseModel subclass defining the knowledge structure.
            llm_client: Language model client for extraction and evolution.
            embedder: Embedding model for semantic search and similarity computation.
            prompt: Custom prompt template for extraction (defaults to generic prompt).
            chunk_size: Maximum chunk size for splitting long texts.
            chunk_overlap: Number of overlapping characters between chunks.
            max_workers: Maximum number of concurrent extraction tasks.
            show_progress: Whether to display progress information during processing.
        """
        self._data_schema = data_schema
        self.llm_client = llm_client
        self.embedder = embedder
        self.prompt = prompt or self._default_prompt()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_workers = max_workers
        self.show_progress = show_progress

        # Initialize prompt template and LLM chain for structured extraction
        self.prompt_template = ChatPromptTemplate.from_template(f"{self.prompt}{{chunk_text}}")
        self.llm_with_schema = self.llm_client.with_structured_output(self._data_schema)
        self.llm_chain_extract = self.prompt_template | self.llm_with_schema

        # Initialize text splitter for chunking long documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ". ", "! ", "? ", " ", ""],
        )

        # Vector index using FAISS for semantic search
        self._index = None

        # Internal state storing the extracted knowledge
        self._data: T = self._data_schema()
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    @staticmethod
    def _default_prompt() -> str:
        """Returns the default extraction prompt template."""
        return (
            "You are an expert knowledge extraction assistant. "
            "Your task is to carefully analyze the following text and extract structured information "
            "according to the specified schema. Be precise, comprehensive, and faithful to the source text. "
            "Extract all relevant details without adding information not present in the text.\n\n"
            "### Source Text:\n"
        )

    # ==================== Data Management ====================

    @property
    def data_schema(self) -> Type[T]:
        """Returns the Pydantic schema class used by this knowledge instance.

        Returns:
            The Pydantic BaseModel subclass defining the knowledge structure.
        """
        return self._data_schema

    @property
    def data(self) -> T:
        """Returns all stored knowledge (read-only access).

        Returns:
            The internal knowledge data as a Pydantic model instance.
        """
        return self._data

    def clear(self):
        """Clears all knowledge including data and vector index."""
        self.metadata["updated_at"] = datetime.now()
        self._data = self._data_schema()
        self.clear_index()

    def clear_index(self):
        """Clears the vector index without affecting the stored data."""
        self._index = None

    # ==================== Extraction & Aggregation ====================

    @abstractmethod
    def extract(self, text: str, *, store: bool = True) -> T:
        """Extracts structured knowledge from text with automatic chunking and aggregation.

        This is the main entry point for knowledge extraction. It handles the complete pipeline
        from text preprocessing to knowledge aggregation.

        Extraction pipeline:
            1. Determine if text chunking is needed based on length
            2. Extract knowledge from each chunk using LLM
            3. Merge all extracted data using the merge() method
            4. If store=True: merge with existing data and update internal state
            5. If store=False: return extracted data without modifying internal state
            6. Return the aggregated knowledge

        Args:
            text: Input text to extract knowledge from (can be short or long).
            store: Controls whether to store extracted knowledge internally.
                - True (default): Store mode - merge with existing knowledge and update internal state
                - False: Temporary mode - return extracted data without modifying internal state

        Returns:
            The extracted and aggregated knowledge data.
        """
        pass

    @abstractmethod
    def merge(self, data_list: List[T]) -> T:
        """Merges multiple knowledge data objects into a single unified object.

        This is a pure data transformation method that does not modify internal state.
        Subclasses implement specific merge strategies (deduplication, conflict resolution, etc.).

        Responsibilities:
            - Implement concrete merge algorithms (deduplication, conflict resolution, etc.)
            - Return a new merged data object
            - Never modify instance attributes

        Args:
            data_list: List of knowledge data objects to merge.

        Returns:
            A new merged knowledge object.
        """
        pass

    def _create_new_instance(self) -> "BaseKnowledge[T]":
        """Creates a new instance with the same configuration as this one.
        
        Subclasses can override this method if they have special initialization requirements.
        
        Returns:
            A new knowledge instance with the same configuration.
        """
        return self.__class__(
            data_schema=self._data_schema,
            llm_client=self.llm_client,
            embedder=self.embedder,
            prompt=self.prompt,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            max_workers=self.max_workers,
            show_progress=self.show_progress,
        )

    def __add__(self, other: "BaseKnowledge[T]") -> "BaseKnowledge[T]":
        """Operator overload for '+' to merge two knowledge instances.

        Creates a new knowledge instance by merging the data from both instances.
        The new instance inherits configuration from the left operand (self).

        Usage:
            >>> kb1 = UnitKnowledge(PersonSchema, ...)
            >>> kb2 = UnitKnowledge(PersonSchema, ...)
            >>> kb3 = kb1 + kb2  # ✅ Same schema, creates merged instance
            >>> 
            >>> kb4 = UnitKnowledge(CompanySchema, ...)
            >>> kb5 = kb1 + kb4  # ❌ TypeError: Different schemas

        Args:
            other: Another knowledge instance of the same type to merge with.

        Returns:
            A new knowledge instance containing merged data.

        Raises:
            TypeError: If other is not an instance of the same knowledge class or has different data schema.
        """
        # Check 1: Both must be instances of the same knowledge class
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot add {type(other).__name__} to {type(self).__name__}. "
                f"Both operands must be instances of the same knowledge class."
            )

        # Check 2: Both must have the same data schema
        if self._data_schema != other._data_schema:
            raise TypeError(
                f"Cannot add knowledge instances with different data schemas. "
                f"Left schema: {self._data_schema.__name__}, "
                f"Right schema: {other._data_schema.__name__}. "
                f"Both operands must have the same data schema to be merged."
            )

        # Merge the data from both instances
        merged_data = self.merge([self._data, other._data])

        # Create a new instance with the same configuration
        new_instance = self._create_new_instance()

        # Set the merged data and update metadata
        new_instance._data = merged_data
        new_instance.metadata["created_at"] = min(
            self.metadata["created_at"], other.metadata["created_at"]
        )
        new_instance.metadata["updated_at"] = datetime.now()
        new_instance.clear_index()  # Index needs to be rebuilt

        return new_instance

    # ==================== Evolution ====================

    def evolve(self, **kwargs) -> T:
        """Evolves and optimizes the internal knowledge through inference and refinement.

        Subclasses can implement this method to perform knowledge-specific evolution strategies.

        Evolution capabilities:
            - Infer implicit relationships between entities
            - Prune low-confidence nodes and connections
            - Apply clustering for better organization
            - Complete missing knowledge through reasoning

        Returns:
            The evolved knowledge data.
        """
        pass

    # ==================== Indexing & Query ====================

    @abstractmethod
    def build_index(self):
        """Builds or rebuilds the vector index for semantic search.

        Subclasses must implement this method to define how the vector index is constructed
        from the knowledge data. Uses FAISS as the vector store backend.
        """
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> List[Any]:
        """Performs semantic search over the knowledge base.

        Standard search workflow:
            1. Ensure index is built (call build_index if needed)
            2. Use vector_store.similarity_search for retrieval
            3. Restore original data structures from Document.metadata

        Subclasses can override this method to implement custom search logic.

        Args:
            query: Search query string.
            top_k: Number of results to return.

        Returns:
            List of relevant knowledge items.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Returns the number of knowledge items in the collection.

        Subclasses must implement this method to report their specific size metric.
        This enables using len() function on knowledge instances.

        Returns:
            The count of knowledge items.
        """
        pass

    # ==================== Serialization ====================

    @abstractmethod
    def dump(self, folder_path: str | Path):
        """Exports knowledge to a specified folder.

        Subclasses must implement this method to persist their knowledge data.

        Files to save:
            1. Structured data (self._data) - saved as JSON file
            2. Vector index (self._index) - saved as FAISS index files

        Args:
            folder_path: Target folder path for saving knowledge.
        """
        pass

    @abstractmethod
    def load(self, folder_path: str | Path):
        """Loads knowledge from a specified folder.

        Subclasses must implement this method to restore previously saved knowledge.

        Files to load:
            1. Structured data (self._data) - loaded from JSON file
            2. Vector index (self._index) - loaded from FAISS index files

        Args:
            folder_path: Source folder path containing saved knowledge.
        """
        pass
