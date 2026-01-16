"""Unit Knowledge Pattern - extracts a single structured object from text."""

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

    @staticmethod
    def _default_prompt() -> str:
        """Returns the default extraction prompt for single-object extraction."""
        return (
            "You are an expert knowledge extraction assistant. "
            "Your task is to carefully analyze the following text and extract structured information "
            "according to the specified schema. Be precise, comprehensive, and faithful to the source text. "
            "Extract all relevant details without adding information not present in the text.\n\n"
            "### Source Text:\n"
        )

    # ==================== Extraction & Aggregation ====================

    def extract(self, text: str, *, store: bool = True) -> T:
        """Extracts knowledge using LangChain native batch processing.

        Automatically handles text chunking for long documents and aggregates results
        using the field-level merge strategy.

        Args:
            text: Input text to extract knowledge from.
            store: Controls whether to store extracted knowledge internally.
                - True (default): Store mode - merge with existing knowledge and update internal state
                - False: Temporary mode - return extracted data without modifying internal state

        Returns:
            The extracted knowledge object.
        """
        start_time = datetime.now()

        # Determine if chunking is needed based on text length
        if len(text) <= self.chunk_size:
            # Short text: direct extraction without chunking
            if self.show_progress:
                logger.info(f"Processing single text (length: {len(text)})...")

            extracted_data = self.llm_chain_extract.invoke({"chunk_text": text})
            extracted_data_list = [extracted_data]

        else:
            # Long text: extract by chunking
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks")

            if self.show_progress:
                logger.info(f"Processing {len(chunks)} chunk(s)...")

            inputs = [{"chunk_text": chunk} for chunk in chunks]
            extracted_data_list = self.llm_chain_extract.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )

        if self.show_progress:
            logger.info(f"Extracted {len(extracted_data_list)} chunks")

        logger.info("Merging extracted knowledge...")
        merged_data = self.merge(extracted_data_list)

        # If store=True, merge with existing data and update internal state
        if store:
            if self._data and any(
                v is not None for v in self._data.model_dump().values()
            ):
                self._data = self.merge([self._data, merged_data])
            else:
                self._data = merged_data

            self.clear_index()
            self.metadata["updated_at"] = datetime.now()

        logger.info("Knowledge extraction completed")
        logger.info(
            f"Duration: {(datetime.now() - start_time).total_seconds():.2f} seconds"
        )

        return self._data if store else merged_data

    def merge(self, data_list: List[T]) -> T:
        """Pure data merge method implementing field-level update strategy.

        Merge strategy: First extraction takes precedence. Subsequent extractions only fill
        missing fields without overwriting existing values. Implemented using model_copy(update=...).

        Args:
            data_list: List of extracted data objects to merge.

        Returns:
            A new merged knowledge object.
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
