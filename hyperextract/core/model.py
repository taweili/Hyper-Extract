"""Unit Knowledge Pattern - extracts a single structured object from text."""

from pathlib import Path
from typing import List, Any, Type
from datetime import datetime
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from .base import BaseAutoType, T

try:
    from hyperextract.config import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class AutoModel(BaseAutoType[T]):
    """AutoModel - extracts a single structured object from text.

    This pattern is designed for extracting exactly one structured object per document,
    regardless of document length. Suitable for document-level information like summaries,
    metadata, or aggregate statistics.

    Key characteristics:
        - Extraction target: One unique structured object per document
        - Merge strategy: Field-level update (Upsert/Patch) - first extraction wins,
          subsequent extractions only fill missing fields
        - Indexing strategy: Each non-null field of the object is indexed independently
        - Processing: Uses LangChain native batch processing for efficient multi-chunk handling
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
        **kwargs,
    ):
        """Initialize AutoModel with schema and configuration.

        Args:
            data_schema: Pydantic BaseModel subclass defining the object structure.
            llm_client: Language model client for extraction.
            embedder: Embedding model for vector indexing.
            prompt: Custom extraction prompt (defaults to generic prompt).
            chunk_size: Maximum characters per chunk for long texts.
            chunk_overlap: Overlapping characters between adjacent chunks.
            max_workers: Maximum concurrent extraction tasks.
            show_progress: Whether to log progress information.
        """
        super().__init__(
            data_schema,
            llm_client,
            embedder,
            prompt=prompt or self._default_prompt(),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            show_progress=show_progress,
            **kwargs,
        )

    def _default_prompt(self) -> str:
        """Returns the default extraction prompt for single-object extraction."""
        return (
            "You are an expert knowledge extraction assistant. "
            "Your task is to carefully analyze the following text and extract structured information "
            "according to the specified schema. Be precise, comprehensive, and faithful to the source text. "
            "Extract all relevant details without adding information not present in the text.\n\n"
            "### Source Text:\n"
        )

    @property
    def data(self) -> T:
        """Returns all stored knowledge (read-only access).

        Returns:
            The internal knowledge data as a Pydantic model instance.
        """
        return self._data

    # ==================== State Management Lifecycle Hooks ====================

    def _init_data_state(self) -> None:
        """
        INIT/RESET: Initialize or reset with empty schema instance.
        Called during __init__ and when clear() is called.
        """
        self._data = self._data_schema()

    def _init_index_state(self) -> None:
        """Initialize vector index to empty state."""
        self._index = None

    def _set_data_state(self, data: T) -> None:
        """
        SET: Full reset. Replace with new data (e.g., load from disk).
        Called by extract() or load() where data IS the new state.
        """
        self._data = data
        self.clear_index()

    def _update_data_state(self, incoming_data: T) -> None:
        """
        UPDATE: Incremental merge. Merge fields with field-level update strategy (called by feed()).

        For AutoModel, incremental update means filling missing fields, first extraction wins.
        """
        merged_data = self.merge_batch_data([self._data, incoming_data])
        self._data = merged_data
        self.clear_index()

    # ==================== Core Methods ====================

    def merge_batch_data(self, data_list: List[T]) -> T:
        """Pure data merge method implementing field-level update strategy.

        Merge strategy: First extraction takes precedence. Subsequent extractions only fill
        missing fields without overwriting existing values. Implemented using model_copy(update=...).
        This is used to aggregate results from batch extraction across multiple chunks.

        Args:
            data_list: List of extracted data objects from batch processing to merge.

        Returns:
            A new merged knowledge object with all fields populated.
        """
        result = data_list[0].model_copy()

        for item in data_list[1:]:
            result = item.model_copy(update=result.model_dump(exclude_none=True))

        return result

    # ==================== Indexing & Query ====================

    def build_index(self):
        """Builds vector index from all non-null fields in the data object."""
        # Check if there's data to index
        if len(self) == 0:
            logger.warning("No data to index")
            return

        if self._index is not None:
            return

        documents = []
        for field_name in self.data_schema.model_fields:
            field_value = getattr(self._data, field_name)
            if field_value is not None:
                documents.append(
                    Document(
                        page_content=field_name,
                        metadata={"raw": {field_name: field_value}},
                    )
                )

        self._index = FAISS.from_documents(documents, self.embedder)
        logger.info(f"Built FAISS index with {len(documents)} documents")

    def __len__(self) -> int:
        """Returns 1 if there is data (non-empty fields), 0 otherwise.

        AutoModel always represents a single unit of knowledge, so it's either
        empty (0) or contains one item (1).
        """
        if not self._data:
            return 0
        # Check if any field is non-null
        has_data = any(v is not None for v in self._data.model_dump().values())
        return 1 if has_data else 0

    def search(self, query: str, top_k: int = 3) -> List[Any]:
        """Searches all indexed fields using semantic similarity.

        Args:
            query: Search query string.
            top_k: Number of results to return.

        Returns:
            List of relevant knowledge items (field-value dictionaries).
        """
        # Check if there's data to search
        if len(self) == 0:
            logger.warning("No items to search")
            return []

        if self._index is None:
            raise Exception("Index is not built, please build the index first.")

        docs = self._index.similarity_search(query, k=top_k)

        # Restore original objects from metadata
        results = []
        for doc in docs:
            try:
                raw_data = doc.metadata["raw"]  # {field_name: field_value}
                results.append(raw_data)
            except Exception as e:
                logger.warning(f"Failed to restore item: {e}")

        logger.info(f"Found {len(results)} results for query: {query[:50]}...")
        return results

    # ==================== Index Storage ====================

    def _dump_index_storage(self, folder: Path) -> None:
        """Saves FAISS vector index to disk."""
        if self._index is None:
            return
        index_path = str(folder / "index")
        self._index.save_local(index_path)

    def _load_index_storage(self, folder: Path) -> None:
        """Loads FAISS vector index from disk."""
        from langchain_community.vectorstores import FAISS

        index_path = folder / "index"
        if index_path.exists():
            try:
                self._index = FAISS.load_local(
                    str(index_path), self.embedder, allow_dangerous_deserialization=True
                )
            except Exception:
                self._index = None
        else:
            self._index = None

    # ==================== Operators ====================

    def __add__(self, other):
        """Operator overload for '+' to combine AutoModel instances into AutoList.

        Supports multiple combination patterns:
        - AutoModel + AutoModel → AutoList (create list from both items)
        - AutoModel + AutoList → AutoList (prepend model to list)

        This enables intuitive chain operations like: unit1 + unit2 + unit3

        Usage:
            >>> unit1 = AutoModel(PersonSchema, ...)
            >>> unit2 = AutoModel(PersonSchema, ...)
            >>> person_list = unit1 + unit2  # → AutoList[PersonSchema]
            >>>
            >>> # Chain operations
            >>> unit3 = AutoModel(PersonSchema, ...)
            >>> person_list = unit1 + unit2 + unit3  # → AutoList with 3 items

        Args:
            other: Another AutoModel with the same data schema, or AutoList.

        Returns:
            AutoList containing both objects as items.

        Raises:
            TypeError: If schemas don't match or invalid operand type.
        """
        from .list import AutoList

        # Case 1: AutoModel + AutoModel → AutoList
        if isinstance(other, AutoModel):
            # Check schema compatibility
            if self._data_schema != other._data_schema:
                raise TypeError(
                    f"Cannot add AutoModel instances with different schemas. "
                    f"Left: {self._data_schema.__name__}, Right: {other._data_schema.__name__}"
                )

            # Create new AutoList
            list_kb = AutoList(
                item_schema=self._data_schema,
                llm_client=self.llm_client,
                embedder=self.embedder,
                prompt=self.prompt,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                max_workers=self.max_workers,
                show_progress=self.show_progress,
            )

            # Set items from both units
            list_kb._data.items = [self._data, other._data]

            # Merge metadata
            list_kb.metadata["created_at"] = min(
                self.metadata["created_at"], other.metadata["created_at"]
            )
            list_kb.metadata["updated_at"] = datetime.now()

            return list_kb

        # Case 2: AutoModel + AutoList → AutoList (prepend model)
        elif isinstance(other, AutoList):
            # Check schema compatibility
            if self._data_schema != other.item_schema:
                raise TypeError(
                    f"Cannot add AutoModel to AutoList with different schemas. "
                    f"Unit: {self._data_schema.__name__}, List: {other.item_schema.__name__}"
                )

            # Create new AutoList with unit prepended
            new_list = AutoList(
                item_schema=self._data_schema,
                llm_client=self.llm_client,
                embedder=self.embedder,
                prompt=self.prompt,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                max_workers=self.max_workers,
                show_progress=self.show_progress,
            )

            # Prepend self to other's items
            new_list._data.items = [self._data] + other.items

            # Merge metadata
            new_list.metadata["created_at"] = min(
                self.metadata["created_at"], other.metadata["created_at"]
            )
            new_list.metadata["updated_at"] = datetime.now()

            return new_list

        else:
            raise TypeError(
                f"Unsupported operand type for +: 'AutoModel' and '{type(other).__name__}'"
            )
