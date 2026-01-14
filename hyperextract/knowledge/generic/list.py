"""List Knowledge Pattern - extracts a collection of objects from text."""

import json
from typing import List, Any, Type, TypeVar, Generic, TYPE_CHECKING
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field, create_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from ..base import BaseKnowledge

try:
    from hyperextract.config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


Item = TypeVar("Item", bound=BaseModel)


class ItemListSchema(BaseModel, Generic[Item]):
    """Generic schema container for list-based knowledge patterns."""

    items: List[Item] = Field(default_factory=list, description="Item list")


class ListKnowledge(BaseKnowledge[ItemListSchema[Item]], Generic[Item]):
    """List Knowledge Pattern - extracts a collection of objects from text.

    This pattern extracts multiple independent objects from a document, suitable for
    extracting entities, events, references, or any collection of structured items.

    Key characteristics:
        - Extraction target: A collection of structured objects
        - Merge strategy: Append with basic deduplication (extensible by subclasses)
        - Indexing strategy: Each item in the list is indexed independently

    Comparison with UnitKnowledge:
        - UnitKnowledge: Extracts a single structured object (e.g., summary, metadata)
        - ListKnowledge: Extracts multiple independent objects (e.g., entity list, event list)
    """

    if TYPE_CHECKING:
        # Use generic version during type checking to maintain complete type hints
        item_list_schema: Type[ItemListSchema[Item]]

    def __init__(
        self,
        item_schema: Type[Item],
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
        """Initialize ListKnowledge with item schema and configuration.

        Args:
            item_schema: Pydantic BaseModel subclass for individual list items.
            llm_client: Language model client for extraction.
            embedder: Embedding model for vector indexing.
            prompt: Custom extraction prompt (defaults to list-oriented prompt).
            chunk_size: Maximum characters per chunk for long texts.
            chunk_overlap: Overlapping characters between adjacent chunks.
            max_workers: Maximum concurrent extraction tasks.
            show_progress: Whether to log progress information.
        """
        self.item_schema = item_schema

        container_name = f"{item_schema.__name__}List"
        self.item_list_schema = create_model(
            container_name,
            items=(
                List[item_schema],
                Field(default_factory=list, description="Item list"),
            ),
        )

        super().__init__(
            data_schema=self.item_list_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt or self._default_prompt(),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            show_progress=show_progress,
            **kwargs,
        )

    @staticmethod
    def _default_prompt() -> str:
        """Returns the default extraction prompt for list-based extraction."""
        return (
            "You are an expert knowledge extraction assistant. "
            "Extract all relevant items from the text into a list. "
            "Be comprehensive and ensure no item is missed. "
            "Extract all items without adding information not present in the text.\n\n"
            "### Source Text:\n"
        )

    @property
    def items(self) -> List[Item]:
        """Returns the internal list of extracted items."""
        return getattr(self._data, "items", [])

    def _create_new_instance(self) -> "ListKnowledge[Item]":
        """Creates a new instance with the same configuration as this one.
        
        Overrides base class method to handle ListKnowledge's item_schema parameter.
        
        Returns:
            A new ListKnowledge instance with the same configuration.
        """
        return self.__class__(
            item_schema=self.item_schema,
            llm_client=self.llm_client,
            embedder=self.embedder,
            prompt=self.prompt,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            max_workers=self.max_workers,
            show_progress=self.show_progress,
        )

    def __add__(self, other):
        """Operator overload for '+' to combine knowledge instances.

        Supports multiple combination patterns:
        - ListKnowledge + ListKnowledge → ListKnowledge (merge lists)
        - ListKnowledge + UnitKnowledge → ListKnowledge (append unit to list)

        This enables chain operations like: unit1 + unit2 + unit3

        Args:
            other: Another ListKnowledge or UnitKnowledge with compatible schema.

        Returns:
            New ListKnowledge with combined items.

        Raises:
            TypeError: If schemas don't match or invalid operand type.
        """
        from .unit import UnitKnowledge

        # Case 1: ListKnowledge + ListKnowledge (call parent implementation)
        if isinstance(other, ListKnowledge):
            # Check schema compatibility
            if self.item_schema != other.item_schema:
                raise TypeError(
                    f"Cannot add ListKnowledge instances with different schemas. "
                    f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
                )
            # Use base class merge logic
            return super().__add__(other)

        # Case 2: ListKnowledge + UnitKnowledge → ListKnowledge (append unit)
        elif isinstance(other, UnitKnowledge):
            # Check schema compatibility
            if self.item_schema != other._data_schema:
                raise TypeError(
                    f"Cannot add UnitKnowledge to ListKnowledge with different schemas. "
                    f"List: {self.item_schema.__name__}, Unit: {other._data_schema.__name__}"
                )

            # Create new ListKnowledge with appended unit
            new_list = self._create_new_instance()
            new_list._data.items = self.items + [other._data]

            # Merge metadata
            new_list.metadata["created_at"] = min(
                self.metadata["created_at"], other.metadata["created_at"]
            )
            new_list.metadata["updated_at"] = datetime.now()

            return new_list

        else:
            raise TypeError(
                f"Unsupported operand type for +: 'ListKnowledge' and '{type(other).__name__}'"
            )

    def extract(self, text: str, *, store: bool = True) -> ItemListSchema:
        """Extracts a list of items using LangChain native batch processing.

        Args:
            text: Input text to extract items from.
            store: Controls whether to store extracted knowledge internally.
                - True (default): Store mode - merge with existing knowledge and update internal state
                - False: Temporary mode - return extracted data without modifying internal state

        Returns:
            The list of extracted items.
        """
        start_time = datetime.now()

        # Determine if chunking is needed
        if len(text) <= self.chunk_size:
            # Short text: extract in one pass
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
            if self._data and len(self.items) > 0:
                self._data = self.merge([self._data, merged_data])
            else:
                self._data = merged_data
            
            self.clear_index()
            self.metadata["updated_at"] = datetime.now()

        logger.info("Knowledge extraction completed")
        logger.info(
            f"Duration: {(datetime.now() - start_time).total_seconds():.2f} seconds"
        )
        
        # Return items list (either from stored data or temporary merged data)
        return self.items if store else merged_data.items

    def merge(self, data_list: List[ItemListSchema]) -> ItemListSchema:
        """Pure data merge method implementing list append strategy.

        Merge strategy: Collects all items from all container objects and merges them
        into a single list. Subclasses can override this method to implement more
        sophisticated deduplication logic (e.g., EntityKnowledge).

        Args:
            data_list: List of container objects to merge.

        Returns:
            A new merged ItemListSchema object.
        """
        all_items = []

        # Collect all items from each container
        for data in data_list:
            copied_data = data.model_copy(deep=True)
            all_items.extend(copied_data.items)

        # Return a new container object
        return self.item_list_schema(items=all_items)

    def build_index(self):
        """Builds independent vector index for each item in the list."""
        items = self.items
        if not items:
            logger.warning("No items to index")
            return

        if self._index is not None:
            return

        documents = []
        for idx, item in enumerate(items):
            # Serialize each Item as a Document
            content = item.model_dump_json()  # Use JSON string as content
            documents.append(
                Document(
                    page_content=content,
                    metadata={"raw": item.model_dump(), "index": idx},
                )
            )

        if documents:
            try:
                self._index = FAISS.from_documents(documents, self.embedder)
                logger.info(f"Built FAISS index with {len(documents)} items")
            except ImportError:
                logger.error("FAISS not available. Install with: pip install faiss-cpu")
                raise

    def search(self, query: str, top_k: int = 3) -> List[Any]:
        """Searches items in the list using semantic similarity.

        Args:
            query: Search query string.
            top_k: Number of results to return.

        Returns:
            List of relevant items.
        """
        if not self.items:
            logger.warning("No items to search")
            return []

        if self._index is None:
            raise Exception("Vector store not initialized")

        docs = self._index.similarity_search(query, k=top_k)
        results = []
        for doc in docs:
            # Attempt to restore as object
            try:
                raw = doc.metadata.get("raw", {})
                item = self.item_schema.model_validate(raw)
                results.append(item)
            except Exception as e:
                logger.warning(f"Failed to restore item: {e}")
                results.append(doc.metadata.get("raw"))

        logger.info(f"Found {len(results)} results for query: {query[:50]}...")
        return results

    def __len__(self) -> int:
        """Returns the number of elements in the list."""
        return len(self.items)

    def dump(self, folder_path: str) -> Any:
        """Exports knowledge to a specified folder.

        Uses the same serialization logic as UnitKnowledge since the container
        is also a BaseModel.
        """
        folder = Path(folder_path)
        folder.mkdir(parents=True, exist_ok=True)

        # 1. Save structured data
        data = {
            "schema_name": self.item_list_schema.__name__,
            "item_schema_name": self.item_schema.__name__,
            "item_schema": self.item_schema.model_json_schema(),
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

        return json_str

    def load(self, folder_path: str):
        """Loads knowledge from a specified folder."""
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

        self._data = self.item_list_schema.model_validate(data.get("data", {}))

        # Update metadata with loaded values
        if "metadata" in data:
            self.metadata.update(data["metadata"])
        self.metadata["updated_at"] = datetime.now()

        # 2. Load vector index
        index_path = str(folder / "faiss_index")
        if Path(index_path).exists():
            try:
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

        logger.info(f"Loaded knowledge successfully with {len(self)} items")
