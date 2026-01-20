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

    # ==================== Initialization & Configuration ====================

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

        # Initialize text splitter for chunking long documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ". ", "! ", "? ", " ", ""],
        )

        # Internal state storing the extracted knowledge
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

    # ==================== Data Access Interface ====================

    @property
    def data_schema(self) -> Type[T]:
        """Returns the Pydantic schema class used by this knowledge instance.

        Returns:
            The Pydantic BaseModel subclass defining the knowledge structure.
        """
        return self._data_schema

    @property
    @abstractmethod
    def data(self) -> T:
        """Returns all stored knowledge (read-only access).

        This is an abstract property that subclasses must implement.
        Subclasses may apply transformations to convert internal _data structure
        to the external Schema T if they differ (e.g., AutoSet converts OMem → List).

        Returns:
            The internal knowledge data as a Pydantic model instance (or converted form).
        """
        pass

    # ==================== Data Management Operations ====================

    def clear(self):
        """Clears all knowledge including data and vector index."""
        self._init_internal_state()
        self.metadata["updated_at"] = datetime.now()

    def clear_index(self):
        """Clears the vector index without affecting the stored data."""
        self._init_index_state()

    # ==================== Lifecycle Hooks: State Management ====================

    def _init_internal_state(self) -> None:
        """Master control: Initialize or reset all internal state (INIT/RESET).

        This concrete method orchestrates the reset process by calling two hooks:
        1. _init_data_state() - Subclass responsibility: reset data structures
        2. _init_index_state() - Default: reset index, can be overridden by subclass

        Called in two scenarios:
        - During __init__ to set up the initial state
        - When clear() is called to reset to empty state
        """
        self._init_data_state()
        self._init_index_state()

    @abstractmethod
    def _init_data_state(self) -> None:
        """HOOK: Initialize or reset data structures to empty state.

        Subclass Responsibility:
        - Initialize self._data with appropriate structure (may differ from Schema T)
        - Reset any auxiliary data structures (e.g., lookup dicts, caches)

        Subclasses must implement this to set up internal structures that may be optimized
        beyond the standard Pydantic schema (e.g., OMem for AutoSet, dict-based for others).
        """
        pass

    @abstractmethod
    def _set_data_state(self, data: T) -> None:
        """HOOK: Overwrite data state with new data (SET).

        Called by extract() or load() where the data provided IS the new state.

        Subclass Responsibilities:
        1. Replace self._data with new data (full reset)
        2. Convert standard Schema T to optimized internal structure if needed
        3. Invalidate vector index (self.clear_index())

        Args:
            data: The new data object to set.
        """
        pass

    @abstractmethod
    def _update_data_state(self, incoming_data: T) -> None:
        """HOOK: Merge new data into state (UPDATE).

        Called by feed() where the data provided is INCREMENTAL.

        Subclass Responsibilities:
        1. Merge incoming_data into current data state (optimized for incremental updates)
        2. Invalidate vector index (self.clear_index())

        Subclasses should implement optimized incremental updates (e.g., set.add instead of
        full merge_batch, graph.add_edge instead of graph rebuild).

        Args:
            incoming_data: The incremental data to merge into the current state.
        """
        pass

    @abstractmethod
    def _init_index_state(self) -> None:
        """HOOK: Initialize or reset vector index to empty state.

        Subclass Responsibility:
        - Initialize or reset vector index structures
        - Can be FAISS, Chroma, Pinecone, or custom implementation
        - Typically sets self._index = None or initializes specific index instance

        This separation allows index implementation to be decoupled from base class.
        """
        pass

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

        prompt_template = ChatPromptTemplate.from_template(
            f"{self.prompt}{{chunk_text}}"
        )
        llm_chain = prompt_template | self.llm_client.with_structured_output(
            self._data_schema
        )

        if len(text) <= self.chunk_size:
            extracted_data = llm_chain.invoke({"chunk_text": text})
            extracted_data_list = [extracted_data]
        else:
            chunks = self.text_splitter.split_text(text)
            inputs = [{"chunk_text": chunk} for chunk in chunks]
            extracted_data_list = llm_chain.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )

        merged_data = self.merge_batch_data(extracted_data_list)
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
        new_instance._set_data_state(extracted_data)

        new_instance.metadata["created_at"] = datetime.now()
        new_instance.metadata["updated_at"] = datetime.now()

        return new_instance

    def feed_text(self, text: str) -> "BaseAutoType[T]":
        """
        Ingests text into the CURRENT knowledge base instance.

        This modifies the internal state by merging new data with existing data.
        Supports method chaining (e.g., kb.feed_text(text1).feed_text(text2)).

        Args:
            text: Input text.

        Returns:
            Self (the current instance).
        """
        extracted_data = self._extract_data(text)

        # Use UPDATE hook instead of manual merge+set
        self._update_data_state(extracted_data)

        self.metadata["updated_at"] = datetime.now()

        return self

    @abstractmethod
    def merge_batch_data(self, data_list: List[T]) -> T:
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

    # ==================== Indexing & Search ====================

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

    # ==================== Serialization: Core Interface ====================

    def dump(self, folder_path: str | Path) -> None:
        """Exports knowledge to a specified folder.

        Storage Structure:
            folder/
            ├── config.json   # Metadata, Schema Info, Parameters
            ├── data.json     # Pure Knowledge Data
            └── index/        # Vector Index Files

        Args:
            folder_path: Target folder path for saving.
        """
        folder = Path(folder_path)
        if folder.is_file():
            raise FileExistsError(f"Path is a file, expected directory: {folder}")
        folder.mkdir(parents=True, exist_ok=True)

        # 1. Save Configuration (Schema, Metadata, Parameters)
        self._save_config(folder)

        # 2. Save Data (Pure Data)
        self._save_data(folder)

        # 3. Save Index (Optional)
        if self._index is not None:
            self._dump_index_storage(folder)

    def load(self, folder_path: str | Path) -> None:
        """Loads knowledge from a specified folder.

        Args:
            folder_path: Source folder path containing saved knowledge.
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        # 1. Load Configuration (Validate compatibility)
        self._load_config(folder)

        # 2. Load Data (Restore state)
        self._load_data(folder)

        # 3. Load Index (Restore vector search)
        self._load_index_storage(folder)

    # ==================== Serialization: Components ====================

    def _save_config(self, folder: Path) -> None:
        """Saves metadata, schema info, and instance parameters."""
        config = {
            "version": "1.0",
            "type": self.__class__.__name__,
            "schema": self._data_schema.__name__,
            "params": {
                "prompt": self.prompt,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "max_workers": self.max_workers,
            },
            "metadata": {
                k: str(v) if isinstance(v, datetime) else v
                for k, v in self.metadata.items()
            },
            "extra": self._get_extra_config_data(),
        }

        with open(folder / "config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _save_data(self, folder: Path) -> None:
        """Saves the pure knowledge data."""
        export_data = self.data.model_dump()

        with open(folder / "data.json", "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

    def _load_config(self, folder: Path) -> None:
        """Loads and validates configuration."""
        config_path = folder / "config.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Strict schema validation - raise error if mismatch
        if config.get("schema") != self._data_schema.__name__:
            raise ValueError(
                f"Schema mismatch: Expected '{self._data_schema.__name__}', "
                f"but found '{config.get('schema')}' in config.json"
            )

        # Restore metadata
        if "metadata" in config:
            self.metadata.update(config["metadata"])

        # Restore extra config
        if "extra" in config:
            self._load_extra_config_data(config["extra"])

    def _load_data(self, folder: Path) -> None:
        """Loads data and restores internal state."""
        data_path = folder / "data.json"
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")

        with open(data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # Validate and Set State
        validated_data = self._data_schema.model_validate(raw_data)
        self._set_data_state(validated_data)

    @abstractmethod
    def _dump_index_storage(self, folder: Path) -> None:
        """HOOK: Save vector index to disk.

        Subclasses must implement to support their specific vector store
        (FAISS, Chroma, Pinecone, etc.).

        Args:
            folder: Target folder for saving index files.
        """
        pass

    @abstractmethod
    def _load_index_storage(self, folder: Path) -> None:
        """HOOK: Load vector index from disk.

        Subclasses must implement to support their specific vector store
        (FAISS, Chroma, Pinecone, etc.).

        Args:
            folder: Source folder containing index files.
        """
        pass

    # ==================== Serialization: Hooks ====================

    def _get_extra_config_data(self) -> Dict[str, Any]:
        """Hook to save subclass-specific configuration (not data).

        Override this method to save subclass-specific config like merge strategy.

        Returns:
            Dictionary of extra config data.
        """
        return {}

    def _load_extra_config_data(self, extra_config: Dict[str, Any]) -> None:
        """Hook to load subclass-specific configuration.

        Override this method to restore subclass-specific config.

        Args:
            extra_config: Extra configuration data from config.json.
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
        merged_data = self.merge_batch_data([self._data, other._data])

        # Create a new instance with the same configuration
        new_instance = self._create_empty_instance()

        # Set the merged data using hook and update metadata
        new_instance._set_data_state(merged_data)
        new_instance.metadata["created_at"] = min(
            self.metadata["created_at"], other.metadata["created_at"]
        )
        new_instance.metadata["updated_at"] = datetime.now()

        return new_instance
