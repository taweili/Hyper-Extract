"""Set Knowledge Pattern - extracts a unique collection of objects from text.

Provides automatic deduplication based on a user-specified unique key field.
Supports multiple merge strategies including LLM-powered intelligent merging.
"""

import json
from typing import List, Any, Type, TypeVar, Generic, Dict, Optional
from datetime import datetime
from pathlib import Path
from enum import Enum
from pydantic import BaseModel, Field, create_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

from ..base import BaseKnowledge

try:
    from hyperextract.config import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


Item = TypeVar("Item", bound=BaseModel)


class ItemSetSchema(BaseModel, Generic[Item]):
    """Generic schema container for set-based knowledge patterns."""

    items: List[Item] = Field(default_factory=list, description="Set of unique items")


class MergeItemStrategy(str, Enum):
    """Merge strategy for handling duplicate items.

    Strategies:
        KEEP_OLD: Keep the existing item, discard the new one
        KEEP_NEW: Keep the new item, discard the existing one (default)
        FIELD_MERGE: Merge fields from both items (new fills old's None fields)
        LLM_MERGE: Use LLM to intelligently merge both items
    """

    KEEP_OLD = "keep_old"
    KEEP_NEW = "keep_new"
    FIELD_MERGE = "field_merge"
    LLM_MERGE = "llm_merge"


class SetKnowledge(BaseKnowledge[ItemSetSchema[Item]], Generic[Item]):
    """Set Knowledge Pattern - extracts a unique collection of objects.

    This pattern automatically deduplicates items based on a user-specified
    unique key field. Provides flexible merge strategies including LLM-powered
    intelligent merging for handling duplicates.

    Key characteristics:
        - Extraction target: A unique collection of structured objects
        - Deduplication: Based on unique_key field (user-specified)
        - Merge strategy: Configurable (keep_old/keep_new/field_merge/llm_merge)
        - Internal storage: Dict for O(1) lookup and deduplication
        - External interface: List (via items property)
        - Set operations: union (|), intersection (&), difference (-)

    Comparison with ListKnowledge:
        - ListKnowledge: Allows duplicates, simple append merge
        - SetKnowledge: Automatic deduplication, intelligent merge strategies

    Example:
        >>> class KeywordSchema(BaseModel):
        ...     term: str
        ...     category: str | None = None
        ...     frequency: int | None = None
        >>>
        >>> keywords = SetKnowledge(
        ...     item_schema=KeywordSchema,
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     unique_key="term",
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
        unique_key: str,
        merge_item_strategy: MergeItemStrategy = MergeItemStrategy.KEEP_NEW,
        prompt: str = "",
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
        max_workers: int = 10,
        show_progress: bool = True,
        llm_batch_size: int = 10,
        **kwargs,
    ):
        """Initialize SetKnowledge with unique key and merge strategy.

        Args:
            item_schema: Pydantic BaseModel subclass for individual items.
            llm_client: Language model client for extraction and merging.
            embedder: Embedding model for vector indexing.
            unique_key: Field name to use as unique identifier (required).
            merge_item_strategy: Strategy for merging duplicate items (default: KEEP_NEW).
            prompt: Custom extraction prompt.
            chunk_size: Maximum characters per chunk for long texts.
            chunk_overlap: Overlapping characters between adjacent chunks.
            max_workers: Maximum concurrent extraction tasks.
            show_progress: Whether to log progress information.
            llm_batch_size: Batch size for LLM merge operations (for LLM_MERGE strategy).
            **kwargs: Additional arguments passed to parent class.

        Raises:
            ValueError: If unique_key field does not exist in item_schema.
            TypeError: If unique_key field type is not hashable.
        """
        # Validate unique_key before initialization
        self._validate_unique_key(item_schema, unique_key)

        # Store item_schema
        self.item_schema = item_schema

        # Create ItemSetSchema container dynamically (similar to ListKnowledge's ItemListSchema)
        container_name = f"{item_schema.__name__}Set"
        self.item_set_schema = create_model(
            container_name,
            items=(
                List[item_schema],
                Field(default_factory=list, description="Set of unique items"),
            ),
        )

        # Call BaseKnowledge.__init__ (not ListKnowledge)
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

        # SetKnowledge-specific attributes
        self.unique_key = unique_key
        self.merge_item_strategy = merge_item_strategy
        self.llm_batch_size = llm_batch_size

        # Internal storage: Dict for O(1) deduplication
        self._items_dict: Dict[Any, Item] = {}

        # Create LLM merge chain (if using LLM_MERGE strategy)
        self._merge_chain = (
            self._create_merge_chain()
            if merge_item_strategy == MergeItemStrategy.LLM_MERGE
            else None
        )

    # ==================== Override Instance Creation ====================

    def _create_new_instance(self) -> "SetKnowledge[Item]":
        """Creates a new instance with the same configuration.

        Overrides parent method to include SetKnowledge-specific parameters.

        Returns:
            New SetKnowledge instance.
        """
        return self.__class__(
            item_schema=self.item_schema,
            llm_client=self.llm_client,
            embedder=self.embedder,
            unique_key=self.unique_key,
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

    @staticmethod
    def _validate_unique_key(item_schema: Type[Item], unique_key: str):
        """Validates that unique_key exists in schema and is hashable.

        Args:
            item_schema: The Pydantic schema to validate.
            unique_key: The field name to validate.

        Raises:
            ValueError: If unique_key field does not exist.
            TypeError: If unique_key field type is known to be unhashable.
        """
        # Check field existence
        if unique_key not in item_schema.model_fields:
            available_fields = list(item_schema.model_fields.keys())
            raise ValueError(
                f"unique_key '{unique_key}' not found in {item_schema.__name__}. "
                f"Available fields: {available_fields}"
            )

        # Check field type (basic unhashable type detection)
        field_info = item_schema.model_fields[unique_key]
        field_type = field_info.annotation

        # Extract actual type from Optional/Union if present
        import typing

        if (
            hasattr(typing, "get_origin")
            and typing.get_origin(field_type) is typing.Union
        ):
            args = typing.get_args(field_type)
            field_type = args[0] if args else field_type

        # Check for known unhashable types
        unhashable_types = (list, dict, set, List, Dict)
        if field_type in unhashable_types:
            raise TypeError(
                f"unique_key field '{unique_key}' has unhashable type {field_type}. "
                f"unique_key must be a hashable type (str, int, tuple, etc.)"
            )

    # ==================== LLM Merge Chain ====================

    def _create_merge_chain(self):
        """Creates an LLM chain for intelligently merging duplicate items.

        Subclasses can override this method to customize the merge prompt.

        Returns:
            LangChain chain for merging items.
        """
        merge_template = """You are an expert at merging structured data.
Given two instances of the same item (identified by the same unique key), 
intelligently merge their fields into one complete item.

Merging rules:
1. Keep the unique key field unchanged
2. For other fields: prefer non-null values
3. If both items have values for a field, choose the more complete/accurate one
4. Combine text fields if appropriate (e.g., descriptions)

Item A (existing):
{item_existing}

Item B (incoming):
{item_incoming}

Please merge these two items intelligently and return the merged result."""

        merge_prompt = ChatPromptTemplate.from_template(merge_template)
        return merge_prompt | self.llm_client.with_structured_output(self.item_schema)

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
        return f"SetKnowledge[{self.item_schema.__name__}]({len(self)} unique items)"

    def __str__(self) -> str:
        """Returns a user-friendly string representation."""
        return f"SetKnowledge with {len(self)} unique {self.item_schema.__name__} items"

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
                self._data = self.merge([self._data, merged_data])
            else:
                self._data = merged_data

            self.clear_index()
            self.metadata["updated_at"] = datetime.now()

        logger.info("Knowledge extraction completed")
        logger.info(
            f"Duration: {(datetime.now() - start_time).total_seconds():.2f} seconds"
        )

        # Return items list
        return self.items if store else merged_data.items

    def merge(self, data_list: List[ItemSetSchema[Item]]) -> ItemSetSchema[Item]:
        """Merges multiple data containers with automatic deduplication.

        Overrides parent's merge to implement set semantics:
        1. Collect all items from all containers
        2. For each item, check if unique_key already exists
        3. If duplicate, call merge_item() to resolve
        4. Return deduplicated result

        For LLM_MERGE strategy, batches duplicate pairs for efficient processing.

        Args:
            data_list: List of container objects to merge.

        Returns:
            Merged ItemSetSchema with deduplicated items.
        """
        # Collect all items and track duplicates for batch LLM merge
        merge_pairs = []  # [(existing, incoming, key), ...]

        for data in data_list:
            for item in data.items:
                # Get unique key value
                key_value = self._get_key_value(item)
                if key_value is None:
                    continue

                if key_value in self._items_dict:
                    # Duplicate found
                    if self.merge_item_strategy == MergeItemStrategy.LLM_MERGE:
                        # Collect for batch processing
                        merge_pairs.append(
                            (self._items_dict[key_value], item, key_value)
                        )
                    else:
                        # Merge immediately with non-LLM strategies
                        merged = self.merge_item(self._items_dict[key_value], item)
                        if merged is not None:
                            self._items_dict[key_value] = merged
                else:
                    # New item
                    self._items_dict[key_value] = item.model_copy(deep=True)

        # Batch process LLM merges if any
        if merge_pairs and self.merge_item_strategy == MergeItemStrategy.LLM_MERGE:
            merged_results = self._batch_merge_with_llm(merge_pairs)
            # Update items_dict with merged results
            self._items_dict.update(merged_results)

        # Update internal _data to match _items_dict
        self._data.items = list(self._items_dict.values())

        logger.info(
            f"Merged into {len(self._items_dict)} unique items "
            f"(strategy: {self.merge_item_strategy.value})"
        )

        return self._data

    def merge_item(self, existing: Item, incoming: Item) -> Optional[Item]:
        """Merges two duplicate items based on the configured strategy.

        This method can be overridden by subclasses to implement custom merge logic.

        Args:
            existing: The existing item in the set.
            incoming: The incoming item to merge.

        Returns:
            Merged item, or None to skip this item.
        """
        if self.merge_item_strategy == MergeItemStrategy.KEEP_OLD:
            return existing

        elif self.merge_item_strategy == MergeItemStrategy.KEEP_NEW:
            return incoming

        elif self.merge_item_strategy == MergeItemStrategy.FIELD_MERGE:
            # Field-level merge: existing's non-None values override incoming
            return incoming.model_copy(update=existing.model_dump(exclude_none=True))

        elif self.merge_item_strategy == MergeItemStrategy.LLM_MERGE:
            # LLM merge (should be handled by batch processing in merge())
            # Fallback to single merge if called directly
            return self._merge_item_with_llm(existing, incoming)

        else:
            logger.warning(
                f"Unknown merge strategy: {self.merge_item_strategy}, using KEEP_NEW"
            )
            return incoming

    def _get_key_value(self, item: Item) -> Optional[Any]:
        """Extracts the unique key value from an item.

        Args:
            item: The item to extract key from.

        Returns:
            The unique key value, or None if invalid.
        """
        try:
            key_value = getattr(item, self.unique_key)

            # Validate key value
            if key_value is None:
                logger.warning(
                    f"Item has None value for unique_key '{self.unique_key}', skipping"
                )
                return None

            # Verify hashability
            hash(key_value)
            return key_value

        except TypeError:
            logger.error(
                f"Value {key_value} for unique_key '{self.unique_key}' is not hashable"
            )
            return None
        except AttributeError:
            logger.error(f"Item missing unique_key field '{self.unique_key}'")
            return None

    # ==================== LLM Merge Methods ====================

    def _batch_merge_with_llm(self, merge_pairs: List[tuple]) -> Dict[Any, Item]:
        """Batch processes LLM merges for efficiency.

        Args:
            merge_pairs: List of (existing, incoming, key_value) tuples to merge.

        Returns:
            Dictionary mapping key_value to merged items.
        """
        results = {}

        if not self._merge_chain:
            logger.warning("LLM merge chain not initialized, falling back to KEEP_NEW")
            for existing, incoming, key_value in merge_pairs:
                results[key_value] = incoming
            return results

        total_pairs = len(merge_pairs)
        logger.info(f"Batch merging {total_pairs} duplicate items with LLM...")

        # Process in batches
        for i in range(0, total_pairs, self.llm_batch_size):
            batch = merge_pairs[i : i + self.llm_batch_size]

            # Prepare batch inputs
            inputs = [
                {
                    "item_existing": existing.model_dump_json(indent=2),
                    "item_incoming": incoming.model_dump_json(indent=2),
                }
                for existing, incoming, _ in batch
            ]

            try:
                # Batch invoke LLM
                merged_results = self._merge_chain.batch(inputs)

                # Collect merged results
                for (existing, incoming, key_value), merged in zip(
                    batch, merged_results
                ):
                    if merged:
                        results[key_value] = merged
                        logger.debug(f"Successfully merged item with key '{key_value}'")
                    else:
                        logger.warning(
                            f"LLM merge returned None for key '{key_value}', keeping incoming"
                        )
                        results[key_value] = incoming

            except Exception as e:
                logger.error(f"Batch LLM merge failed: {e}, falling back to KEEP_NEW")
                # Fallback: keep incoming items
                for existing, incoming, key_value in batch:
                    results[key_value] = incoming

        return results

    def _merge_item_with_llm(self, existing: Item, incoming: Item) -> Optional[Item]:
        """Uses LLM to intelligently merge two duplicate items (single merge).

        Args:
            existing: The existing item.
            incoming: The incoming item to merge.

        Returns:
            Merged item, or None on failure.
        """
        if not self._merge_chain:
            logger.warning("LLM merge chain not initialized")
            return incoming

        try:
            merged = self._merge_chain.invoke(
                {
                    "item_existing": existing.model_dump_json(indent=2),
                    "item_incoming": incoming.model_dump_json(indent=2),
                }
            )
            logger.debug("Successfully merged item with LLM")
            return merged
        except Exception as e:
            logger.error(f"LLM merge failed: {e}")
            return incoming  # Fallback to incoming item

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

        Saves both the items and the SetKnowledge-specific metadata.

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
            "unique_key": self.unique_key,
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

        self._data = self.item_set_schema.model_validate(data.get("data", {}))

        # Rebuild items_dict from _data.items (not self.items property!)
        self._items_dict = {}
        for item in self._data.items:
            key_value = self._get_key_value(item)
            if key_value is not None:
                self._items_dict[key_value] = item

        # Update metadata
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
            merged = self.merge_item(self._items_dict[key_value], item)
            if merged:
                self._items_dict[key_value] = merged
        else:
            # Add new
            self._items_dict[key_value] = item.model_copy(deep=True)

        # Update _data
        self._data.items = list(self._items_dict.values())
        self.clear_index()

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
        removed = self._items_dict.pop(key, None)
        if removed:
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
            raise KeyError("pop from an empty SetKnowledge")

        key = next(iter(self._items_dict))
        item = self._items_dict.pop(key)
        self._data.items = list(self._items_dict.values())
        self.clear_index()
        self.metadata["updated_at"] = datetime.now()

        return item

    def copy(self) -> "SetKnowledge[Item]":
        """Creates a deep copy of the set.

        Returns:
            A new SetKnowledge instance with copies of all items.

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

    def __or__(self, other: "SetKnowledge[Item]") -> "SetKnowledge[Item]":
        """Union operation: set1 | set2.

        Returns a new set containing all items from both sets.

        Args:
            other: Another SetKnowledge instance.

        Returns:
            New SetKnowledge with union of items.
        """
        if not isinstance(other, SetKnowledge):
            raise TypeError(
                f"Unsupported operand type for |: 'SetKnowledge' and '{type(other).__name__}'"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot union SetKnowledge instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        # Create new instance
        new_set = self._create_new_instance()
        new_set._items_dict = self._items_dict.copy()

        # Add items from other (merge duplicates)
        for key, item in other._items_dict.items():
            if key in new_set._items_dict:
                merged = new_set.merge_item(new_set._items_dict[key], item)
                if merged:
                    new_set._items_dict[key] = merged
            else:
                new_set._items_dict[key] = item.model_copy(deep=True)

        new_set._data.items = list(new_set._items_dict.values())
        new_set.metadata["updated_at"] = datetime.now()

        return new_set

    def __and__(self, other: "SetKnowledge[Item]") -> "SetKnowledge[Item]":
        """Intersection operation: set1 & set2.

        Returns a new set containing only items present in both sets.

        Args:
            other: Another SetKnowledge instance.

        Returns:
            New SetKnowledge with intersection of items.
        """
        if not isinstance(other, SetKnowledge):
            raise TypeError(
                f"Unsupported operand type for &: 'SetKnowledge' and '{type(other).__name__}'"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot intersect SetKnowledge instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        # Create new instance
        new_set = self._create_new_instance()

        # Only keep items present in both sets
        for key in self._items_dict:
            if key in other._items_dict:
                # Merge the two versions
                merged = new_set.merge_item(
                    self._items_dict[key], other._items_dict[key]
                )
                if merged:
                    new_set._items_dict[key] = merged

        new_set._data.items = list(new_set._items_dict.values())
        new_set.metadata["updated_at"] = datetime.now()

        return new_set

    def __sub__(self, other: "SetKnowledge[Item]") -> "SetKnowledge[Item]":
        """Difference operation: set1 - set2.

        Returns a new set containing items in self but not in other.

        Args:
            other: Another SetKnowledge instance.

        Returns:
            New SetKnowledge with difference of items.
        """
        if not isinstance(other, SetKnowledge):
            raise TypeError(
                f"Unsupported operand type for -: 'SetKnowledge' and '{type(other).__name__}'"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot subtract SetKnowledge instances with different schemas. "
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

    def __xor__(self, other: "SetKnowledge[Item]") -> "SetKnowledge[Item]":
        """Symmetric difference operation: set1 ^ set2.

        Returns a new set containing items in either set but not in both.

        Args:
            other: Another SetKnowledge instance.

        Returns:
            New SetKnowledge with symmetric difference of items.
        """
        if not isinstance(other, SetKnowledge):
            raise TypeError(
                f"Unsupported operand type for ^: 'SetKnowledge' and '{type(other).__name__}'"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot compute symmetric difference of SetKnowledge instances with different schemas. "
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

    def union(self, other: "SetKnowledge[Item]") -> "SetKnowledge[Item]":
        """Union operation (named method)."""
        return self | other

    def intersection(self, other: "SetKnowledge[Item]") -> "SetKnowledge[Item]":
        """Intersection operation (named method)."""
        return self & other

    def difference(self, other: "SetKnowledge[Item]") -> "SetKnowledge[Item]":
        """Difference operation (named method)."""
        return self - other

    def symmetric_difference(self, other: "SetKnowledge[Item]") -> "SetKnowledge[Item]":
        """Symmetric difference operation (named method)."""
        return self ^ other

    # ==================== Set Comparison Operations ====================

    def __eq__(self, other: Any) -> bool:
        """Equality comparison: set1 == set2.

        Two sets are equal if they have the same schema, unique_key, and key set.
        Note: Does not compare item contents, only keys.

        Args:
            other: Another object to compare with.

        Returns:
            True if both sets have the same keys, False otherwise.

        Examples:
            >>> skills1 == skills2  # True if same keys
        """
        if not isinstance(other, SetKnowledge):
            return False

        if self.item_schema != other.item_schema:
            return False

        if self.unique_key != other.unique_key:
            return False

        return set(self._items_dict.keys()) == set(other._items_dict.keys())

    def __ne__(self, other: Any) -> bool:
        """Inequality comparison: set1 != set2.

        Returns:
            True if sets are not equal, False otherwise.
        """
        return not self.__eq__(other)

    def __le__(self, other: "SetKnowledge[Item]") -> bool:
        """Subset comparison: set1 <= set2.

        Args:
            other: Another SetKnowledge instance.

        Returns:
            True if self is a subset of other (all keys in self are in other).

        Raises:
            TypeError: If other is not a SetKnowledge or has different schema.

        Examples:
            >>> skills1 <= skills2  # True if skills1 is subset of skills2
        """
        if not isinstance(other, SetKnowledge):
            return NotImplemented

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot compare SetKnowledge instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        return set(self._items_dict.keys()).issubset(set(other._items_dict.keys()))

    def __lt__(self, other: "SetKnowledge[Item]") -> bool:
        """Proper subset comparison: set1 < set2.

        Args:
            other: Another SetKnowledge instance.

        Returns:
            True if self is a proper subset of other (subset and not equal).

        Examples:
            >>> skills1 < skills2  # True if skills1 is proper subset
        """
        if not isinstance(other, SetKnowledge):
            return NotImplemented

        return self <= other and self != other

    def __ge__(self, other: "SetKnowledge[Item]") -> bool:
        """Superset comparison: set1 >= set2.

        Args:
            other: Another SetKnowledge instance.

        Returns:
            True if self is a superset of other (all keys in other are in self).

        Examples:
            >>> skills1 >= skills2  # True if skills1 is superset of skills2
        """
        if not isinstance(other, SetKnowledge):
            return NotImplemented

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot compare SetKnowledge instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        return set(self._items_dict.keys()).issuperset(set(other._items_dict.keys()))

    def __gt__(self, other: "SetKnowledge[Item]") -> bool:
        """Proper superset comparison: set1 > set2.

        Args:
            other: Another SetKnowledge instance.

        Returns:
            True if self is a proper superset of other (superset and not equal).

        Examples:
            >>> skills1 > skills2  # True if skills1 is proper superset
        """
        if not isinstance(other, SetKnowledge):
            return NotImplemented

        return self >= other and self != other

    def issubset(self, other: "SetKnowledge[Item]") -> bool:
        """Test whether every key in the set is in other.

        Args:
            other: Another SetKnowledge instance.

        Returns:
            True if self is a subset of other.

        Examples:
            >>> skills1.issubset(skills2)
        """
        return self <= other

    def issuperset(self, other: "SetKnowledge[Item]") -> bool:
        """Test whether every key in other is in the set.

        Args:
            other: Another SetKnowledge instance.

        Returns:
            True if self is a superset of other.

        Examples:
            >>> skills1.issuperset(skills2)
        """
        return self >= other

    def isdisjoint(self, other: "SetKnowledge[Item]") -> bool:
        """Test whether the set has no keys in common with other.

        Args:
            other: Another SetKnowledge instance.

        Returns:
            True if the two sets have no keys in common.

        Raises:
            TypeError: If other is not a SetKnowledge or has different schema.

        Examples:
            >>> skills1.isdisjoint(skills2)  # True if no common skills
        """
        if not isinstance(other, SetKnowledge):
            raise TypeError(
                f"isdisjoint() argument must be SetKnowledge, not {type(other).__name__}"
            )

        if self.item_schema != other.item_schema:
            raise TypeError(
                f"Cannot compare SetKnowledge instances with different schemas. "
                f"Left: {self.item_schema.__name__}, Right: {other.item_schema.__name__}"
            )

        return set(self._items_dict.keys()).isdisjoint(set(other._items_dict.keys()))
