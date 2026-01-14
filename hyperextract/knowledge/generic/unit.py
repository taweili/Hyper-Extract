"""Unit Knowledge Pattern - extracts a single structured object from text."""

import json
from typing import List, Any, Type
from datetime import datetime
from pathlib import Path
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from ..base import BaseKnowledge, T

try:
    from hyperextract.config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class UnitKnowledge(BaseKnowledge[T]):
    """Unit Knowledge Pattern - extracts a single structured object from text.

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
        """Initialize UnitKnowledge with schema and configuration.

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
            if self._data and any(v is not None for v in self._data.model_dump().values()):
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

    def __add__(self, other):
        """Operator overload for '+' to combine UnitKnowledge instances into ListKnowledge.

        When two UnitKnowledge instances are added, they are combined into a ListKnowledge
        containing both objects as separate items. This enables intuitive collection building.

        Usage:
            >>> unit1 = UnitKnowledge(PersonSchema, ...)
            >>> unit2 = UnitKnowledge(PersonSchema, ...)
            >>> person_list = unit1 + unit2  # → ListKnowledge[PersonSchema]
            >>> 
            >>> # Chain operations
            >>> unit3 = UnitKnowledge(PersonSchema, ...)
            >>> person_list = unit1 + unit2 + unit3  # → ListKnowledge with 3 items

        Args:
            other: Another UnitKnowledge with the same data schema, or ListKnowledge.

        Returns:
            ListKnowledge containing both objects as items.

        Raises:
            TypeError: If schemas don't match or invalid operand type.
        """
        from .list import ListKnowledge

        # Case 1: UnitKnowledge + UnitKnowledge → ListKnowledge
        if isinstance(other, UnitKnowledge):
            # Check schema compatibility
            if self._data_schema != other._data_schema:
                raise TypeError(
                    f"Cannot add UnitKnowledge instances with different schemas. "
                    f"Left: {self._data_schema.__name__}, Right: {other._data_schema.__name__}"
                )

            # Create new ListKnowledge
            list_kb = ListKnowledge(
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

        # Case 2: UnitKnowledge + ListKnowledge → ListKnowledge (for reverse order)
        elif isinstance(other, ListKnowledge):
            # Check schema compatibility
            if self._data_schema != other.item_schema:
                raise TypeError(
                    f"Cannot add UnitKnowledge to ListKnowledge with different schemas. "
                    f"Unit: {self._data_schema.__name__}, List: {other.item_schema.__name__}"
                )

            # Create new ListKnowledge with unit prepended
            new_list = ListKnowledge(
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
                f"Unsupported operand type for +: 'UnitKnowledge' and '{type(other).__name__}'"
            )

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

    def __len__(self) -> int:
        """Returns 1 since UnitKnowledge represents a single knowledge unit."""
        return 1

    # ==================== Serialization ====================

    def dump(self, folder_path: str | Path):
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
            logger.info(f"Creating folder: {folder}")
            folder.mkdir(parents=True, exist_ok=True)

        try:
            # 1. Save structured data
            data = {
                "schema_name": self.data_schema.__name__,
                "data_schema": self.data_schema.model_json_schema(),
                "data": self.data.model_dump(),
                "metadata": {
                    k: str(v) if isinstance(v, datetime) else v
                    for k, v in self.metadata.items()
                },
            }

            json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
            data_file = folder / "state.json"
            with open(data_file, "w", encoding="utf-8") as f:
                f.write(json_str)
            logger.info(f"Saved data to {data_file}")

            # 2. Save vector index
            if self._index is not None:
                index_path = str(folder / "faiss_index")
                self._index.save_local(index_path)
                logger.info(f"Saved FAISS index to {index_path}")
            else:
                logger.warning("No index to save")

        except Exception as e:
            logger.error(f"Failed to dump knowledge: {e}")

    def load(self, folder_path: str | Path):
        """Loads knowledge from a specified folder.

        Loads from the folder:
            1. Structured data (self._data) - loaded from state.json
            2. Vector index (self._index) - loaded from FAISS index files

        Args:
            folder_path: Source folder path containing saved knowledge.
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            raise ValueError(f"Folder does not exist: {folder_path}")

        # 1. Load structured data
        data_file = folder / "state.json"
        if not data_file.is_file():
            raise ValueError(f"Data file not found: {data_file}")

        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Loaded data from {data_file}")

        self._data = self.data_schema.model_validate(data.get("data", {}))

        # Update metadata with loaded values
        if "metadata" in data:
            self.metadata.update(data["metadata"])
        self.metadata["updated_at"] = datetime.now()

        # 2. Load vector index
        index_path = str(folder / "faiss_index")
        if Path(index_path).exists():
            try:
                from langchain_community.vectorstores import FAISS

                self._index = FAISS.load_local(
                    index_path, self.embedder, allow_dangerous_deserialization=True
                )
                logger.info(f"Loaded FAISS index from {index_path}")
            except Exception as e:
                logger.warning(f"Failed to load FAISS index: {e}")
                self._index = None
        else:
            logger.warning("No index file found, will rebuild on next search")
            self._index = None

        logger.info(f"Loaded knowledge successfully with {len(self)} unit(s)")
