from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, Any, Dict, Type, List
from datetime import datetime
import json
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate


T = TypeVar("T", bound=BaseModel)


# ===================== Knowledge Base Class =====================


class BaseAutoType(ABC, Generic[T]):
    """Unified knowledge base class integrating extraction, storage, and aggregation.

    This abstract base class provides a complete framework for managing structured knowledge
    extracted from text. It handles the full lifecycle from extraction to serialization.

    Responsibilities:
        - Extract structured knowledge from text using LLM
        - Automatically handle long text chunking and parallel processing
        - Store and aggregate extracted knowledge with configurable merge strategies
        - Build and maintain vector indices for semantic search
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
            llm_client: Language model client for extraction.
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
        self.prompt_template = ChatPromptTemplate.from_template(
            f"{self.prompt}{{chunk_text}}"
        )
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

        # Initialize internal state (calls hook for subclass setup)
        self._init_internal_state()

    def _create_empty_instance(self) -> "BaseAutoType[T]":
        """Creates a new empty instance with the same configuration as this one.

        Subclasses can override this method if they have special initialization requirements.

        Returns:
            A new empty knowledge instance with the same configuration.
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

    @abstractmethod
    def _default_prompt(self) -> str:
        """Returns the default extraction prompt template.
        
        Subclasses must implement this to provide a prompt tailored to their extraction pattern.
        """
        pass

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

    # ==================== State Management Lifecycle Hooks ====================

    def _init_internal_state(self) -> None:
        """
        Protected hook to initialize internal state (INIT).
        Called at the END of __init__ to ensure all basic attributes are set first.

        Subclasses can override to initialize their own structures (e.g., _set_memory for AutoSet).
        """
        self._data = self._data_schema()
        self._index = None

    def _set_internal_state(self, data: T) -> None:
        """
        Protected hook to overwrite internal state (SET).
        Called by extract() or load() where the data provided IS the new state.

        Responsibilities:
        1. Replace self._data (full reset)
        2. Invalidate vector index (data changed)
        3. Subclasses: Reset auxiliary structures and fill with data

        Args:
            data: The new data object to set.
        """
        self._data = data
        self.clear_index()

    def _update_internal_state(self, incoming_data: T) -> None:
        """
        Protected hook to merge new data into state (UPDATE).
        Called by feed() where the data provided is INCREMENTAL.

        Default behavior: Full merge (inefficient for large sets, good for lists).
        Subclasses override for optimized incremental updates (e.g., set.add instead of merge_batch).

        Responsibilities:
        1. Merge incoming_data with self._data
        2. Update self._data
        3. Invalidate vector index
        4. Subclasses: Optimized incremental update

        Args:
            incoming_data: The incremental data to merge into the current state.
        """
        # Default: Merge incoming with current (works but may be inefficient)
        merged_data = self.merge_batch([self._data, incoming_data])
        self._data = merged_data
        self.clear_index()

    def _clear_internal_state(self) -> None:
        """
        Protected hook to fully clear internal state (CLEAR).
        Called by clear() method.

        Default: Reset to empty schema instance via _set_internal_state hook.
        """
        self._set_internal_state(self._data_schema())

    # ==================== Data Management ====================

    def clear(self):
        """Clears all knowledge including data and vector index."""
        self._clear_internal_state()
        self.metadata["updated_at"] = datetime.now()

    def clear_index(self):
        """Clears the vector index without affecting the stored data."""
        self._index = None

    # ==================== Extraction & Merge ====================

    def _extract_data(self, text: str) -> T:
        """
        Internal: Unified extraction logic (Chunking -> LLM -> Merge).
        Implemented in BaseAutoType for code reuse by List and Set.

        Args:
            text: Input text.

        Returns:
            The extracted knowledge data.
        """
        if len(text) <= self.chunk_size:
            extracted_data = self.llm_chain_extract.invoke({"chunk_text": text})
            extracted_data_list = [extracted_data]
        else:
            chunks = self.text_splitter.split_text(text)
            inputs = [{"chunk_text": chunk} for chunk in chunks]
            extracted_data_list = self.llm_chain_extract.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )

        merged_data = self.merge_batch(extracted_data_list)
        return merged_data

    def extract(self, text: str) -> "BaseAutoType[T]":
        """
        Extracts knowledge into a NEW instance without modifying the current one.

        Use this for previewing data or branching knowledge bases.

        Args:
            text: Input text.

        Returns:
            A new knowledge instance containing only the extracted data.
        """
        extracted_data = self._extract_data(text)

        new_instance = self._create_empty_instance()
        new_instance._set_internal_state(extracted_data)

        new_instance.metadata["created_at"] = datetime.now()
        new_instance.metadata["updated_at"] = datetime.now()

        return new_instance

    def feed(self, text: str) -> "BaseAutoType[T]":
        """
        Ingests text into the CURRENT knowledge base instance.

        This modifies the internal state by merging new data with existing data.
        Supports method chaining (e.g., kb.feed(text1).feed(text2)).

        Args:
            text: Input text.

        Returns:
            Self (the current instance).
        """
        extracted_data = self._extract_data(text)
        
        # Use UPDATE hook instead of manual merge+set
        self._update_internal_state(extracted_data)
        
        self.metadata["updated_at"] = datetime.now()

        return self

    @abstractmethod
    def merge_batch(self, data_list: List[T]) -> T:
        """Merges multiple knowledge data objects into a single unified object.

        This is a pure data transformation method that does not modify internal state.
        Subclasses implement specific merge strategies (deduplication, conflict resolution, etc.).
        The batch merge is typically used during multi-chunk extraction where results from
        different chunks need to be aggregated into a single knowledge object.

        Responsibilities:
            - Implement concrete merge algorithms (deduplication, conflict resolution, etc.)
            - Return a new merged data object
            - Never modify instance attributes

        Args:
            data_list: List of knowledge data objects to merge from batch processing.

        Returns:
            A new merged knowledge object.
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

    # ==================== Serialization ====================

    def dump(self, folder_path: str | Path) -> None:
        """Exports knowledge to a specified folder.

        Saves to the folder:
            1. Structured data (self._data) - saved as state.json
            2. Vector index (self._index) - saved as FAISS index files

        Args:
            folder_path: Target folder path for saving.
        """
        folder = Path(folder_path)
        if folder.exists() and folder.is_file():
            raise Exception("Folder path is a file, please provide a folder path.")

        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)

        try:
            # 1. Save structured data
            data = {
                "schema_name": self._data_schema.__name__,
                "data_schema": self._data_schema.model_json_schema(),
                "data": self._data.model_dump(),
                "metadata": self._prepare_metadata_for_dump(),
            }

            # Allow subclasses to add extra fields
            data.update(self._get_extra_dump_data())

            json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
            data_file = folder / "state.json"
            with open(data_file, "w", encoding="utf-8") as f:
                f.write(json_str)

            # 2. Save vector index
            if self._index is not None:
                index_path = str(folder / "faiss_index")
                self._index.save_local(index_path)

        except Exception:
            raise

    def load(self, folder_path: str | Path) -> None:
        """Loads knowledge from a specified folder.

        Loads from the folder:
            1. Structured data (self._data) - loaded from state.json
            2. Vector index (self._index) - loaded from FAISS index files

        Args:
            folder_path: Source folder path containing saved knowledge.
        """
        from langchain_community.vectorstores import FAISS

        folder = Path(folder_path)
        if not folder.is_dir():
            raise ValueError(f"Folder does not exist: {folder_path}")

        # 1. Load structured data
        data_file = folder / "state.json"
        if not data_file.is_file():
            raise ValueError(f"Data file not found: {data_file}")

        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Load data using hook for proper state sync
        loaded_data = self._data_schema.model_validate(data.get("data", {}))
        self._set_internal_state(loaded_data)

        # Update metadata with loaded values
        if "metadata" in data:
            self.metadata.update(data["metadata"])
        self.metadata["updated_at"] = datetime.now()

        # Allow subclasses to load extra data
        self._load_extra_data(data)

        # 2. Load vector index
        index_path = str(folder / "faiss_index")
        if Path(index_path).exists():
            try:
                self._index = FAISS.load_local(
                    index_path, self.embedder, allow_dangerous_deserialization=True
                )
            except Exception:
                self._index = None

    # ==================== Serialization Helpers ====================

    def _prepare_metadata_for_dump(self) -> Dict[str, Any]:
        """Helper to serialize metadata values (e.g., datetimes)."""
        return {
            k: str(v) if isinstance(v, datetime) else v
            for k, v in self.metadata.items()
        }

    def _get_extra_dump_data(self) -> Dict[str, Any]:
        """Hook for subclasses to add extra fields to state.json.

        Override this method to save subclass-specific data (e.g., merge strategy).

        Returns:
            Dictionary of extra data to include in state.json.
        """
        return {}

    def _load_extra_data(self, json_data: Dict[str, Any]) -> None:
        """Hook for subclasses to extract extra fields from state.json.

        Override this method to restore subclass-specific data.

        Args:
            json_data: The loaded JSON data dictionary.
        """
        pass

    # ==================== Operator Overloads ====================

    def __add__(self, other: "BaseAutoType[T]") -> "BaseAutoType[T]":
        """Operator overload for '+' to merge two knowledge instances.

        Creates a new knowledge instance by merging the data from both instances.
        The new instance inherits configuration from the left operand (self).

        Usage:
            >>> kb1 = AutoList(PersonSchema, ...)
            >>> kb2 = AutoList(PersonSchema, ...)
            >>> kb3 = kb1 + kb2  # ✅ Same schema, creates merged instance
            >>>
            >>> kb4 = AutoList(CompanySchema, ...)
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
        merged_data = self.merge_batch([self._data, other._data])

        # Create a new instance with the same configuration
        new_instance = self._create_empty_instance()

        # Set the merged data using hook and update metadata
        new_instance._set_internal_state(merged_data)
        new_instance.metadata["created_at"] = min(
            self.metadata["created_at"], other.metadata["created_at"]
        )
        new_instance.metadata["updated_at"] = datetime.now()

        return new_instance
