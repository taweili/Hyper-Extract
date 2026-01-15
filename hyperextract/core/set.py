"""Set Knowledge Pattern - extracts a unique collection of objects from text.

Provides automatic deduplication based on a user-specified unique key field.
Supports multiple merge strategies including LLM-powered intelligent merging.
"""

import json
from typing import List, Any, Type, TypeVar, Generic, Dict, Optional, Callable
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field, create_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

from .base import BaseAutoType
from hyperextract.utils.merger import (
    BaseMerger,
    MergeStrategy,
    KeepNewMerger,
    KeepOldMerger,
    FieldMerger,
    LLMMerger,
)

try:
    from hyperextract.config import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


Item = TypeVar("Item", bound=BaseModel)


class AutoSetSchema(BaseModel, Generic[Item]):
    """Generic schema container for set-based knowledge patterns."""

    items: List[Item] = Field(default_factory=list, description="Set of unique items")


class AutoSet(BaseAutoType[AutoSetSchema[Item]], Generic[Item]):
    """AutoSet - extracts a unique collection of objects.

    This pattern automatically deduplicates items based on a user-specified
    key extractor function. Provides flexible merge strategies including LLM-powered
    intelligent merging for handling duplicates.

    Key characteristics:
        - Extraction target: A unique collection of structured objects
        - Deduplication: Based on key_extractor function (user-specified)
        - Merge strategy: Configurable (keep_old/keep_new/field_merge/llm_merge)
        - Internal storage: Dict for O(1) lookup and deduplication
        - External interface: List (via items property)
        - Set operations: union (|), intersection (&), difference (-)

    Comparison with AutoList:
        - AutoList: Allows duplicates, simple append merge
        - AutoSet: Automatic deduplication, intelligent merge strategies

    Example:
        >>> class KeywordSchema(BaseModel):
        ...     term: str
        ...     category: str | None = None
        ...     frequency: int | None = None
        >>>
        >>> keywords = AutoSet(
        ...     item_schema=KeywordSchema,
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     key_extractor=lambda x: x.term,
        ...     merge_item_strategy="field_merge"
        ... )
        >>> keywords.extract("Python is great. Python is powerful.")
        >>> len(keywords)  # Only 1 item (deduplicated)
        1
    """

    def __init__(
        self,
        item_schema: Type[Item],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        key_extractor: Callable[[Item], Any],
        merge_item_strategy: MergeStrategy = MergeStrategy.KEEP_NEW,
        prompt: str = "",
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
        max_workers: int = 10,
        show_progress: bool = True,
        llm_batch_size: int = 10,
        **kwargs,
    ):
        """Initialize AutoSet with key extractor and merge strategy.

        Args:
            item_schema: Pydantic BaseModel subclass for individual items.
            llm_client: Language model client for extraction and merging.
            embedder: Embedding model for vector indexing.
            key_extractor: Function to extract unique key from an item (required).
            merge_item_strategy: Strategy for merging duplicate items (default: KEEP_NEW).
            prompt: Custom extraction prompt.
            chunk_size: Maximum characters per chunk for long texts.
            chunk_overlap: Overlapping characters between adjacent chunks.
            max_workers: Maximum concurrent extraction tasks.
            show_progress: Whether to log progress information.
            llm_batch_size: Batch size for LLM merge operations (for LLM_MERGE strategy).
            **kwargs: Additional arguments passed to parent class.
        """

        # Store item_schema
        self.item_schema = item_schema

        # Create AutoSetSchema container dynamically (similar to AutoList's AutoListSchema)
        container_name = f"{item_schema.__name__}Set"
        self.item_set_schema = create_model(
            container_name,
            items=(
                List[item_schema],
                Field(default_factory=list, description="Set of unique items"),
            ),
        )

        # Call BaseAutoType.__init__ (not ListKnowledge)
        super().__init__(
            data_schema=self.item_set_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt or self._default_prompt(),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            show_progress=show_progress,
            **kwargs,
        )

        # AutoSet-specific attributes
        self.key_extractor = key_extractor
        self.merge_item_strategy = merge_item_strategy
        self.llm_batch_size = llm_batch_size

        # Internal storage: Dict for O(1) deduplication
        self._items_dict: Dict[Any, Item] = {}

        # Create Merger instance based on strategy
        self._merger: BaseMerger[Item] = self._create_merger(
            item_schema=item_schema,
            llm_client=llm_client,
            merge_item_strategy=merge_item_strategy,
        )

    # ==================== Override Instance Creation ====================

    def _create_new_instance(self) -> "AutoSet[Item]":
        """Creates a new instance with the same configuration.

        Overrides parent method to include AutoSet-specific parameters.

        Returns:
            New AutoSet instance.
        """
        return self.__class__(
            item_schema=self.item_schema,
            llm_client=self.llm_client,
            embedder=self.embedder,
            key_extractor=self.key_extractor,
            merge_item_strategy=self.merge_item_strategy,
            prompt=self.prompt,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            max_workers=self.max_workers,
            show_progress=self.show_progress,
            llm_batch_size=self.llm_batch_size,
        )

    # ==================== Validation ====================

    @staticmethod
    def _default_prompt() -> str:
        """Returns the default extraction prompt for set-based extraction."""
        return (
            "You are an expert knowledge extraction assistant. "
            "Extract all unique items from the text into a set. "
            "Be comprehensive and ensure no item is missed. "
            "Extract all items without adding information not present in the text.\n\n"
            "### Source Text:\n"
        )

    # ==================== Merger Factory ====================

    def _create_merger(
        self,
        item_schema: Type[Item],
        llm_client: BaseChatModel,
        merge_item_strategy: MergeStrategy,
    ) -> BaseMerger[Item]:
        """Creates the appropriate Merger instance based on strategy.

        Args:
            item_schema: Pydantic model for items.
            llm_client: LLM client for LLM_MERGE strategy.
            merge_item_strategy: The merge strategy to use.

        Returns:
            A Merger instance implementing the specified strategy.
        """
        key_extractor = self.key_extractor

        if merge_item_strategy == MergeStrategy.KEEP_OLD:
            return KeepOldMerger(key_extractor, logger_instance=logger)

        elif merge_item_strategy == MergeStrategy.KEEP_NEW:
            return KeepNewMerger(key_extractor, logger_instance=logger)

        elif merge_item_strategy == MergeStrategy.FIELD_MERGE:
            return FieldMerger(key_extractor, logger_instance=logger)

        elif merge_item_strategy == MergeStrategy.LLM_MERGE:
            return LLMMerger(
                key_extractor=key_extractor,
                llm_client=llm_client,
                item_schema=item_schema,
                logger_instance=logger,
            )

        else:
            logger.warning(
                f"Unknown merge strategy: {merge_item_strategy}, using KEEP_NEW"
            )
            return KeepNewMerger(key_extractor, logger_instance=logger)

    # ==================== Properties ====================

    @property
    def items(self) -> List[Item]:
        """Returns the internal items as a list (for external interface compatibility).

        Converts the internal dictionary values to a list.

        Returns:
            List of unique items.
        """
        return list(self._items_dict.values())

    @property
    def keys(self) -> List[Any]:
        """Returns all unique key values.

        Returns:
            List of unique key values.
        """
        return list(self._items_dict.keys())

    def __len__(self) -> int:
        """Returns the number of unique items in the set."""
        return len(self._items_dict)

    def __contains__(self, key: Any) -> bool:
        """Checks if a unique key exists in the set.

        Args:
            key: The unique key value to check.

        Returns:
            True if key exists, False otherwise.
        """
        return key in self._items_dict

    def __repr__(self) -> str:
        """Returns a developer-friendly representation."""
        return f"AutoSet[{self.item_schema.__name__}]({len(self)} unique items)"

    def __str__(self) -> str:
        """Returns a user-friendly string representation."""
        return f"AutoSet with {len(self)} unique {self.item_schema.__name__} items"

    def __iter__(self):
        """Enables iteration over all items in the set.

        Returns:
            Iterator over all unique items.

        Examples:
            >>> for skill in skills:
            ...     print(skill.name)
            >>> names = [s.name for s in skills]
        """
        return iter(self.items)

    # ==================== Core Override Methods ====================

    def clear(self):
        """Clears all items from the set."""
        self._data = self.item_set_schema()
        self._items_dict.clear()
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

    def extract(self, text: str, *, store: bool = True):
        """Extracts a set of unique items using LLM with automatic deduplication.

        Args:
            text: Input text to extract items from.
            store: Whether to store extracted knowledge internally.

        Returns:
            The set of extracted unique items.
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
                final_data = self.merge([self._data, merged_data])
            else:
                final_data = merged_data
            self._update_internal_state(final_data)

        logger.info("Knowledge extraction completed")
        logger.info(
            f"Duration: {(datetime.now() - start_time).total_seconds():.2f} seconds"
        )

        # Return items list
        return self.items if store else merged_data.items

    def merge(self, data_list: List[AutoSetSchema[Item]]) -> AutoSetSchema[Item]:
        """Merges multiple data containers with automatic deduplication.

        Pure function: Does not modify internal state.
        Delegates to Merger for efficient tournament-style merging.
        All merge strategies (including LLM batch processing) are handled
        by the Merger implementation.

        Args:
            data_list: List of container objects to merge.

        Returns:
            New merged AutoSetSchema with deduplicated items.
        """
        # Step 1: Collect all items from all containers
        all_items = []
        for data in data_list:
            all_items.extend(data.items)

        if not all_items:
            return self.item_set_schema()

        logger.info(
            f"Merging {len(all_items)} items from {len(data_list)} containers..."
        )

        # Step 2: Use Merger to deduplicate and merge items
        merged_items = self._merger.merge(all_items)

        logger.info(
            f"Merged into {len(merged_items)} unique items "
            f"(strategy: {self.merge_item_strategy.value})"
        )

        # Step 3: Return new container (does not modify self)
        return self.item_set_schema(items=merged_items)

    def _update_internal_state(self, data: AutoSetSchema[Item]) -> None:
        """Updates internal state from a data container.

        Private method that synchronizes _items_dict and _data with new data.
        Also clears vector index and updates metadata timestamp.

        Args:
            data: The data container to update from.
        """
        self._items_dict.clear()
        for item in data.items:
            key = self._get_key_value(item)
            if key is not None:
                self._items_dict[key] = item

        self._data = data
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

    def _get_key_value(self, item: Item) -> Optional[Any]:
        """Extracts the unique key value from an item using key_extractor.

        Args:
            item: The item to extract key from.

        Returns:
            The unique key value, or None if invalid.
        """
        try:
            key_value = self.key_extractor(item)

            # Validate key value
            if key_value is None:
                logger.warning("Item has None value for key, skipping")
                return None

            # Verify hashability
            hash(key_value)
            return key_value

        except TypeError as e:
            logger.error(f"Key value is not hashable: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to extract key from item: {e}")
            return None

    # ==================== LLM Merge Methods (Removed - Now handled by LLMMerger) ====================

    def build_index(self):
        """Builds independent vector index for each unique item."""
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
                from langchain_community.vectorstores import FAISS

                self._index = FAISS.from_documents(documents, self.embedder)
                logger.info(f"Built FAISS index with {len(documents)} items")
            except ImportError:
                logger.error("FAISS not available. Install with: pip install faiss-cpu")
                raise

    def search(self, query: str, top_k: int = 3) -> List[Any]:
        """Searches items in the set using semantic similarity.

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

    # ==================== Serialization ====================

    def dump(self, folder_path: str | Path):
        """Exports knowledge to a specified folder.

        Saves both the items and the AutoSet-specific metadata.

        Args:
            folder_path: Target folder path for saving.
        """
        folder = Path(folder_path)
        folder.mkdir(parents=True, exist_ok=True)

        # Save structured data
        data = {
            "schema_name": self.item_set_schema.__name__,
            "item_schema_name": self.item_schema.__name__,
            "item_schema": self.item_schema.model_json_schema(),
            "merge_item_strategy": self.merge_item_strategy.value,
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

        # Save vector index
        if self._index is not None:
            index_path = str(folder / "faiss_index")
            self._index.save_local(index_path)
            logger.info(f"Saved FAISS index to {index_path}")
        else:
            logger.warning("No index to save")

    def load(self, folder_path: str | Path):
        """Loads knowledge from a specified folder.

        Args:
            folder_path: Source folder path containing saved knowledge.
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            raise ValueError(f"Folder does not exist: {folder_path}")

        # Load structured data
        data_file = folder / "state.json"
        if not data_file.is_file():
            raise ValueError(f"Data file not found: {data_file}")

        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Loaded data from {data_file}")

        loaded_data = self.item_set_schema.model_validate(data.get("data", {}))
        self._update_internal_state(loaded_data)

        # Update metadata from saved data
        if "metadata" in data:
            self.metadata.update(data["metadata"])
        self.metadata["updated_at"] = datetime.now()

        # Load vector index
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

        logger.info(f"Loaded knowledge successfully with {len(self)} unique items")

    # ==================== Set-Specific Methods ====================

    def add(self, item: Item) -> None:
        """Adds a single item to the set with automatic deduplication.

        Args:
            item: The item to add.
        """
        key_value = self._get_key_value(item)
        if key_value is None:
            return

        if key_value in self._items_dict:
            # Merge with existing
            merged = self._merger.pair_merge(self._items_dict[key_value], item)
            if merged:
                self._items_dict[key_value] = merged
        else:
            # Add new
            self._items_dict[key_value] = item.model_copy(deep=True)

        # Update internal state
        self._data.items = list(self._items_dict.values())
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

    def remove(self, key: Any) -> Optional[Item]:
        """Removes an item by its unique key value.

        Args:
            key: The unique key value to remove.

        Returns:
            The removed item, or None if not found.
        """
        removed = self._items_dict.pop(key, None)
        if removed:
            self._data.items = list(self._items_dict.values())
            self.clear_index()
            self.metadata["updated_at"] = datetime.now()
            logger.debug(f"Removed item with key '{key}'")
        return removed

    def contains(self, key: Any) -> bool:
        """Checks if an item with the given key exists in the set.

        Args:
            key: The unique key value to check.

        Returns:
            True if key exists, False otherwise.
        """
        return key in self._items_dict

    def get(self, key: Any, default: Optional[Item] = None) -> Optional[Item]:
        """Gets an item by its unique key value.

        Args:
            key: The unique key value to retrieve.
            default: Default value if key not found.

        Returns:
            The item if found, otherwise default.
        """
        return self._items_dict.get(key, default)

    def update(self, items: List[Item]) -> None:
        """Batch adds multiple items.

        Args:
            items: List of items to add.
        """
        for item in items:
            self.add(item)

    def discard(self, key: Any) -> None:
        """Removes an item by its unique key value, silently ignoring if not found.

        Unlike remove(), this method does not raise an error if the key does not exist.

        Args:
            key: The unique key value to remove.

        Examples:
            >>> skills.discard("Python")  # No error if not found

        Side Effects:
            - Clears the vector index (needs rebuild)
            - Updates metadata timestamp
        """
        if key in self._items_dict:
            self._items_dict.pop(key)
            self._data.items = list(self._items_dict.values())
            self.clear_index()
            self.metadata["updated_at"] = datetime.now()

    def pop(self) -> Item:
        """Removes and returns an arbitrary item from the set.

        Args:
            None

        Returns:
            The removed item.

        Raises:
            KeyError: If the set is empty.

        Examples:
            >>> skill = skills.pop()
            >>> print(f"Removed: {skill.name}")

        Side Effects:
            - Clears the vector index (needs rebuild)
            - Updates metadata timestamp
        """
        if not self._items_dict:
            raise KeyError("pop from an empty AutoSet")

        key = next(iter(self._items_dict))
        item = self._items_dict.pop(key)
        self._data.items = list(self._items_dict.values())
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

        return item

    def copy(self) -> "AutoSet[Item]":
        """Creates a deep copy of the set.

        Returns:
            A new AutoSet instance with copies of all items.

        Examples:
            >>> backup = skills.copy()
            >>> backup.add(new_skill)
            >>> # Original skills unchanged
        """
        new_set = self._create_new_instance()
        new_set._items_dict = {
            key: item.model_copy(deep=True) for key, item in self._items_dict.items()
        }
        new_set._data.items = list(new_set._items_dict.values())
        new_set.metadata = self.metadata.copy()
        new_set.metadata["created_at"] = datetime.now()

        return new_set

    # ==================== Set Operations ====================

    def __or__(self, other: "AutoSet[Item]") -> "AutoSet[Item]":
        """Union operation: set1 | set2.

        Returns a new set containing all items from both sets.

        Args:
            other: Another AutoSet instance.

        Returns:
            New AutoSet with union of items.
        """
        if not isinstance(other, AutoSet):
            raise TypeError(
                f"Unsupported operand type for |: 'AutoSet' and '{type(other).__name__}'"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot union AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        # Create new instance
        new_set = self._create_new_instance()
        new_set._items_dict = self._items_dict.copy()

        # Add items from other (merge duplicates)
        for key, item in other._items_dict.items():
            if key in new_set._items_dict:
                merged = new_set._merger.pair_merge(new_set._items_dict[key], item)
                if merged:
                    new_set._items_dict[key] = merged
            else:
                new_set._items_dict[key] = item.model_copy(deep=True)

        new_set._data.items = list(new_set._items_dict.values())
        new_set.metadata["updated_at"] = datetime.now()

        return new_set

    def __and__(self, other: "AutoSet[Item]") -> "AutoSet[Item]":
        """Intersection operation: set1 & set2.

        Returns a new set containing only items present in both sets.

        Args:
            other: Another AutoSet instance.

        Returns:
            New AutoSet with intersection of items.
        """
        if not isinstance(other, AutoSet):
            raise TypeError(
                f"Unsupported operand type for &: 'AutoSet' and '{type(other).__name__}'"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot intersect AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        # Create new instance
        new_set = self._create_new_instance()

        # Only keep items present in both sets
        for key in self._items_dict:
            if key in other._items_dict:
                # Merge the two versions
                merged = new_set._merger.pair_merge(
                    self._items_dict[key], other._items_dict[key]
                )
                if merged:
                    new_set._items_dict[key] = merged

        new_set._data.items = list(new_set._items_dict.values())
        new_set.metadata["updated_at"] = datetime.now()

        return new_set

    def __sub__(self, other: "AutoSet[Item]") -> "AutoSet[Item]":
        """Difference operation: set1 - set2.

        Returns a new set containing items in self but not in other.

        Args:
            other: Another AutoSet instance.

        Returns:
            New AutoSet with difference of items.
        """
        if not isinstance(other, AutoSet):
            raise TypeError(
                f"Unsupported operand type for -: 'AutoSet' and '{type(other).__name__}'"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot subtract AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        # Create new instance
        new_set = self._create_new_instance()

        # Only keep items not in other
        for key, item in self._items_dict.items():
            if key not in other._items_dict:
                new_set._items_dict[key] = item.model_copy(deep=True)

        new_set._data.items = list(new_set._items_dict.values())
        new_set.metadata["updated_at"] = datetime.now()

        return new_set

    def __xor__(self, other: "AutoSet[Item]") -> "AutoSet[Item]":
        """Symmetric difference operation: set1 ^ set2.

        Returns a new set containing items in either set but not in both.

        Args:
            other: Another AutoSet instance.

        Returns:
            New AutoSet with symmetric difference of items.
        """
        if not isinstance(other, AutoSet):
            raise TypeError(
                f"Unsupported operand type for ^: 'AutoSet' and '{type(other).__name__}'"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot compute symmetric difference of AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        # Create new instance
        new_set = self._create_new_instance()

        # Add items only in self
        for key, item in self._items_dict.items():
            if key not in other._items_dict:
                new_set._items_dict[key] = item.model_copy(deep=True)

        # Add items only in other
        for key, item in other._items_dict.items():
            if key not in self._items_dict:
                new_set._items_dict[key] = item.model_copy(deep=True)

        new_set._data.items = list(new_set._items_dict.values())
        new_set.metadata["updated_at"] = datetime.now()

        return new_set

    # ==================== Named Set Operations ====================

    def union(self, other: "AutoSet[Item]") -> "AutoSet[Item]":
        """Union operation (named method)."""
        return self | other

    def intersection(self, other: "AutoSet[Item]") -> "AutoSet[Item]":
        """Intersection operation (named method)."""
        return self & other

    def difference(self, other: "AutoSet[Item]") -> "AutoSet[Item]":
        """Difference operation (named method)."""
        return self - other

    def symmetric_difference(self, other: "AutoSet[Item]") -> "AutoSet[Item]":
        """Symmetric difference operation (named method)."""
        return self ^ other

    # ==================== Set Comparison Operations ====================

    def __eq__(self, other: Any) -> bool:
        """Equality comparison: set1 == set2.

        Two sets are equal if they have the same schema and key set.
        Note: Does not compare item contents, only keys.

        Args:
            other: Another object to compare with.

        Returns:
            True if both sets have the same keys, False otherwise.

        Examples:
            >>> skills1 == skills2  # True if same keys
        """
        if not isinstance(other, AutoSet):
            return False

        if self.item_schema != other.item_schema:
            return False

        return set(self._items_dict.keys()) == set(other._items_dict.keys())

    def __ne__(self, other: Any) -> bool:
        """Inequality comparison: set1 != set2.

        Returns:
            True if sets are not equal, False otherwise.
        """
        return not self.__eq__(other)

    def __le__(self, other: "AutoSet[Item]") -> bool:
        """Subset comparison: set1 <= set2.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if self is a subset of other (all keys in self are in other).

        Raises:
            TypeError: If other is not a AutoSet or has different schema.

        Examples:
            >>> skills1 <= skills2  # True if skills1 is subset of skills2
        """
        if not isinstance(other, AutoSet):
            return NotImplemented

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot compare AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        return set(self._items_dict.keys()).issubset(set(other._items_dict.keys()))

    def __lt__(self, other: "AutoSet[Item]") -> bool:
        """Proper subset comparison: set1 < set2.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if self is a proper subset of other (subset and not equal).

        Examples:
            >>> skills1 < skills2  # True if skills1 is proper subset
        """
        if not isinstance(other, AutoSet):
            return NotImplemented

        return self <= other and self != other

    def __ge__(self, other: "AutoSet[Item]") -> bool:
        """Superset comparison: set1 >= set2.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if self is a superset of other (all keys in other are in self).

        Examples:
            >>> skills1 >= skills2  # True if skills1 is superset of skills2
        """
        if not isinstance(other, AutoSet):
            return NotImplemented

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot compare AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        return set(self._items_dict.keys()).issuperset(set(other._items_dict.keys()))

    def __gt__(self, other: "AutoSet[Item]") -> bool:
        """Proper superset comparison: set1 > set2.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if self is a proper superset of other (superset and not equal).

        Examples:
            >>> skills1 > skills2  # True if skills1 is proper superset
        """
        if not isinstance(other, AutoSet):
            return NotImplemented

        return self >= other and self != other

    def issubset(self, other: "AutoSet[Item]") -> bool:
        """Test whether every key in the set is in other.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if self is a subset of other.

        Examples:
            >>> skills1.issubset(skills2)
        """
        return self <= other

    def issuperset(self, other: "AutoSet[Item]") -> bool:
        """Test whether every key in other is in the set.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if self is a superset of other.

        Examples:
            >>> skills1.issuperset(skills2)
        """
        return self >= other

    def isdisjoint(self, other: "AutoSet[Item]") -> bool:
        """Test whether the set has no keys in common with other.

        Args:
            other: Another AutoSet instance.

        Returns:
            True if the two sets have no keys in common.

        Raises:
            TypeError: If other is not a AutoSet or has different schema.

        Examples:
            >>> skills1.isdisjoint(skills2)  # True if no common skills
        """
        if not isinstance(other, AutoSet):
            raise TypeError(
                f"isdisjoint() argument must be AutoSet, not {type(other).__name__}"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot compare AutoSet instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        return set(self._items_dict.keys()).isdisjoint(set(other._items_dict.keys()))
