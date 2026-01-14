"""Entity knowledge extraction module.

Provides entity extraction implementation based on ListKnowledge.
"""

from typing import List, Dict, Type, TypeVar, Generic
from pydantic import BaseModel, Field as PydanticField
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS

from .generic import ListKnowledge

try:
    from src.config import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


# Entity type variable
E = TypeVar("E", bound="BaseEntitySchema")


class BaseEntitySchema(BaseModel):
    """Base entity class defining required core fields for all entities.

    Users can inherit from this class to add custom fields.
    """

    name: str = PydanticField(description="Unique entity name", min_length=1)
    description: str = PydanticField(description="Entity description")

    class Config:
        """Configuration allowing users to extend with additional fields."""

        extra = "allow"  # Allow additional fields
        validate_assignment = True  # Validate on assignment


class EntityKnowledge(ListKnowledge[E], Generic[E]):
    """Specialized knowledge class for entity extraction and management.

    Key features:
        1. Automatic deduplication based on entity.name
        2. Intelligent LLM-powered merging for entities with the same name
        3. Each entity indexed as an independent document
        4. Support for entity-level semantic search
    """

    def __init__(
        self,
        entity_schema: Type[E],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        prompt: str = "",
        **kwargs,
    ):
        """Initialize EntityKnowledge with entity schema and configuration.

        Args:
            entity_schema: User-defined entity class (must inherit from BaseEntity).
            llm_client: Language model client for extraction and merging.
            embedder: Embedding model for vector indexing.
            prompt: Custom extraction prompt.
        """
        self._entity_schema = entity_schema

        super().__init__(
            item_schema=entity_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt or self._default_prompt(),
            **kwargs,
        )

        self._merge_chain = self._create_merge_chain()

        # Global entity mapping (primary storage, type-safe)
        self._entity_map: Dict[str, E] = {}

    @staticmethod
    def _default_prompt() -> str:
        """Returns the default entity extraction prompt."""
        return (
            "You are an expert entity extraction assistant. "
            "Carefully read the following text and extract all entities "
            "according to the specified schema. Be precise and comprehensive."
            "Extract all entities without adding information not present in the text.\n\n"
            "### Source Text:\n"
        )

    def _create_merge_chain(self):
        """Creates an LLM chain for intelligently merging entities with the same name."""
        merge_template = """You are an expert at merging entity information. 
Given two instances of the same entity, intelligently merge their fields into one.

Rules:
1. Keep the 'name' field unchanged
2. Merge 'description' by combining both descriptions (remove duplicates)
3. For other fields: prefer non-null values, if both exist choose the more complete/accurate one

Entity A:
{entity_a}

Entity B:
{entity_b}

Please merge these two entities intelligently and return the result."""

        merge_prompt = ChatPromptTemplate.from_template(merge_template)

        return merge_prompt | self.llm_client.with_structured_output(
            self._entity_schema
        )

    # ==================== Data Management ====================

    def clear(self):
        """Clears all entities from storage."""
        super().clear()
        self._entity_map.clear()

    # ==================== Extraction & Aggregation ====================

    def extract(self, text: str, *, merge_mode: bool = False) -> BaseModel:
        """Extracts entity knowledge with support for replace/accumulate modes.

        Mode explanation:
            - merge_mode=False (default): Replace mode
              Only uses newly extracted entities

            - merge_mode=True: Accumulate mode
              Keeps existing entities, extracts new entities and intelligently merges
              (LLM-powered deduplication)

        Args:
            text: Input text to extract entities from.
            merge_mode: Merge mode (default False).

        Returns:
            Container with extracted entities.
        """
        # Call parent extraction method with merge_mode
        result = super().extract(text, merge_mode=merge_mode)
        
        # Synchronize extracted items to entity_map after extraction
        self._sync_items_to_map()

        logger.info(
            f"Entity extraction completed ({'Accumulate' if merge_mode else 'Replace'} mode)"
        )
        logger.info(f"Total entities: {len(self._entity_map)}")

        return result

    def merge(self, data_list: List[BaseModel]) -> BaseModel:
        """Entity-level intelligent merging using LLM.

        Strategy:
            1. Call parent merge to get all extracted items
            2. Assign result to self._data
            3. Synchronize to entity_map for LLM-powered deduplication
            4. Return deduplicated data

        Args:
            data_list: Multiple container objects.

        Returns:
            Merged entity data.
        """
        # Call parent merge to get merged result
        merged_result = super().merge(data_list)
        
        # Temporarily assign to self._data so _sync_items_to_map can access self.items
        self._data = merged_result
        
        # Synchronize to entity_map for deduplication
        self._sync_items_to_map()
        
        # Return final self._data (updated by _sync_items_to_map)
        return self._data

    def _sync_items_to_map(self):
        """Synchronizes self.items to entity_map, performing deduplication and LLM merging."""
        total_entities = 0
        duplicate_count = 0

        # Traverse parent's items and merge with existing entity_map
        for entity in self.items:
            total_entities += 1
            entity_name = entity.name.strip()

            if not entity_name:  # Skip empty names
                logger.warning(f"Skipping entity with empty name: {entity}")
                continue

            if entity_name in self._entity_map:
                # Entity exists - merge using LLM
                duplicate_count += 1
                existing = self._entity_map[entity_name]
                merged = self._merge_entity_with_llm(existing, entity)
                if merged:
                    self._entity_map[entity_name] = merged
                else:
                    logger.warning(
                        f"LLM merge failed for entity '{entity_name}', keeping existing"
                    )
            else:
                # New entity - deep copy and add
                self._entity_map[entity_name] = entity.model_copy(deep=True)

        # Write deduplicated results back to self.items
        self._data.items = list(self._entity_map.values())
        self.clear_index()

        logger.info(
            f"Merged {len(self._entity_map)} unique entities "
            f"from {total_entities} total (removed {duplicate_count} duplicates)"
        )

    def _merge_entity_with_llm(self, entity_a: E, entity_b: E) -> E | None:
        """Uses LLM to intelligently merge two entities with the same name.

        Args:
            entity_a: First entity.
            entity_b: Second entity.

        Returns:
            Merged entity (returns None on failure).
        """
        try:
            # Prepare inputs
            entity_a_json = entity_a.model_dump_json(indent=2)
            entity_b_json = entity_b.model_dump_json(indent=2)

            # Call LLM for merging
            merged_entity = self._merge_chain.invoke(
                {
                    "entity_a": entity_a_json,
                    "entity_b": entity_b_json,
                }
            )

            logger.debug(f"Successfully merged entity: {merged_entity.name}")
            return merged_entity

        except Exception as e:
            logger.error(f"Error merging entity '{entity_a.name}' with LLM: {e}")
            return None

    # ==================== Indexing & Query ====================

    def build_index(self):
        """Builds independent vector index document for each entity.

        Each entity → one Document:
            - page_content: "{name}: {description} + other fields"
            - metadata: {"entity": entity.model_dump()}
        """
        if len(self._entity_map) == 0:
            logger.warning("No entities to index")
            return

        if self._index is not None:
            return  # Index already exists

        documents = []
        for entity in self._entity_map.values():
            # Build document content for vectorization
            content_parts = [
                f"name: {entity.name}",
                f"description: {entity.description}",
            ]

            # Add other fields if user extended the schema
            for field_name in self._entity_schema.model_fields:
                if field_name not in ("name", "description"):
                    value = getattr(entity, field_name, None)
                    if value is not None:
                        content_parts.append(f"{field_name}: {value}")

            content = "\n".join(content_parts)

            # Save complete entity data to metadata
            documents.append(
                Document(
                    page_content=content,
                    metadata={"raw": entity.model_dump()},
                )
            )

        self._index = FAISS.from_documents(documents, self.embedder)
        logger.info(f"Built FAISS index with {len(documents)} entities")


    def search(self, query: str, top_k: int = 3, return_raw: bool = False) -> List[E]:
        """Performs semantic search over entities.

        Args:
            query: Search query string.
            top_k: Number of results to return.
            return_raw: Whether to return raw entity objects (default returns dict).

        Returns:
            List of entities.
        """
        if len(self) == 0:
            logger.warning("No items to search")
            return []

        if self._index is None:
            raise Exception("Index is not built, please build the index first.")

        docs = self._index.similarity_search(query, k=top_k)

        # Restore entity objects
        results = []
        for doc in docs:
            try:
                entity_data = doc.metadata["raw"]
                if return_raw:
                    # Return Pydantic object
                    entity = self._entity_schema.model_validate(entity_data)
                    results.append(entity)
                else:
                    # Return dictionary
                    results.append(entity_data)
            except Exception as e:
                logger.warning(f"Failed to restore entity: {e}")

        logger.info(f"Found {len(results)} entities for query: {query[:50]}...")
        return results

    def __len__(self) -> int:
        """Returns the number of entities (reads directly from entity_map)."""
        return len(self._entity_map)

    # ==================== Convenience Properties ====================

    @property
    def entities(self) -> List[E]:
        """Quick access to entity list."""
        return self.items

    @property
    def entity_schema(self) -> Type[E]:
        """Returns the user-defined entity schema."""
        return self._entity_schema

    @property
    def entity_names(self) -> List[str]:
        """Returns all entity names (reads directly from entity_map)."""
        return list(self._entity_map.keys())

    # ==================== Optional Enhancement Methods ====================

    def get_entity_by_name(self, name: str) -> E | None:
        """Retrieves entity by name (O(1) dictionary lookup)."""
        return self._entity_map.get(name)

    def remove_entity(self, name: str) -> bool:
        """Removes specified entity (from both entity_map and items)."""
        if name in self._entity_map:
            del self._entity_map[name]
            self._data.items = list(self._entity_map.values())
            self.clear_index()
            logger.info(f"Removed entity: {name}")
            return True
        return False

    # ==================== Serialization ====================

    def load(self, folder_path: str, **kwargs):
        """Loads knowledge and rebuilds entity_map."""
        super().load(folder_path, **kwargs)

        # Rebuild entity_map from items
        self._entity_map = {
            entity.name: entity.model_copy(deep=True) for entity in self.items
        }

        logger.info(f"Loaded {len(self._entity_map)} entities")
