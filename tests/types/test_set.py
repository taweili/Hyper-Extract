"""Tests for AutoSet - set extraction pattern with deduplication."""

import pytest
from pydantic import BaseModel, Field
from ontomem.merger import MergeStrategy
from hyperextract.types.set import AutoSet


class BookEntry(BaseModel):
    """Test schema for book entries."""

    title: str = Field(description="Book title (unique key)")
    author: str | None = Field(None, description="Book author")
    year: int | None = Field(None, description="Publication year")


class TestAutoSetBasics:
    """Test basic AutoSet functionality."""

    def test_initialization(self, llm_client, embedder):
        """Test AutoSet initialization."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
            strategy_or_merger=MergeStrategy.MERGE_FIELD,
        )

        assert books.item_schema == BookEntry
        assert books.empty()
        assert len(books) == 0
        assert books.keys == []

    def test_key_extractor_validation(self, llm_client, embedder):
        """Test that key_extractor is properly stored."""
        key_func = lambda x: x.title

        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=key_func,
        )

        assert books.key_extractor == key_func


class TestAutoSetDeduplication:
    """Test deduplication core functionality."""

    def test_add_deduplicates_same_key(self, llm_client, embedder):
        """Test that adding items with same key deduplicates."""
        # Use MERGE_FIELD strategy to test deterministic deduplication
        # without depending on LLM (works with or without API key)
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
            strategy_or_merger=MergeStrategy.MERGE_FIELD,
        )

        b1 = BookEntry(title="Python Basics", author="John", year=2020)
        books.add(b1)
        assert len(books) == 1

        # Add same book with different author info
        b2 = BookEntry(title="Python Basics", author="John Smith", year=2021)
        books.add(b2)

        # Should still be 1 item (deduplicated with MERGE_FIELD strategy)
        # MERGE_FIELD merges non-null fields, so both books merge into one
        assert len(books) == 1

    def test_add_keeps_distinct_keys(self, llm_client, embedder):
        """Test that distinct keys are kept."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        books.add(BookEntry(title="Python Basics"))
        books.add(BookEntry(title="Web Development"))
        books.add(BookEntry(title="Data Science"))

        assert len(books) == 3
        assert "Python Basics" in books
        assert "Web Development" in books
        assert "Data Science" in books

    def test_keys_property(self, llm_client, embedder):
        """Test keys property returns all unique keys."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        books.add(BookEntry(title="Advanced Python"))
        books.add(BookEntry(title="Web Frameworks"))
        books.add(BookEntry(title="ML Fundamentals"))

        keys = books.keys
        assert len(keys) == 3
        assert "Advanced Python" in keys
        assert "Web Frameworks" in keys
        assert "ML Fundamentals" in keys


class TestAutoSetOperations:
    """Test set-like operations."""

    def test_contains_operator(self, llm_client, embedder):
        """Test 'in' operator (contains)."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        books.add(BookEntry(title="Python Pro"))

        assert "Python Pro" in books
        assert "Java Expert" not in books

    def test_contains_method(self, llm_client, embedder):
        """Test contains method."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        books.add(BookEntry(title="Go Guide"))

        assert books.contains("Go Guide") is True
        assert books.contains("Rust Book") is False

    def test_get_method(self, llm_client, embedder):
        """Test get method retrieves items by key."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        book = BookEntry(title="TypeScript Handbook", author="Microsoft", year=2022)
        books.add(book)

        retrieved = books.get("TypeScript Handbook")
        assert retrieved is not None
        assert retrieved.title == "TypeScript Handbook"

    def test_get_with_default(self, llm_client, embedder):
        """Test get with default value."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        result = books.get("Nonexistent Book", default=None)
        assert result is None


class TestAutoSetRemoval:
    """Test removal operations."""

    def test_remove_removes_by_key(self, llm_client, embedder):
        """Test remove method by key."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        book = BookEntry(title="Remove This")
        books.add(book)
        assert len(books) == 1

        removed = books.remove("Remove This")
        assert removed is not None
        assert removed.title == "Remove This"
        assert len(books) == 0
        assert "Remove This" not in books

    def test_remove_nonexistent(self, llm_client, embedder):
        """Test removing non-existent key returns None."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        result = books.remove("Nonexistent")
        assert result is None


class TestAutoSetIteration:
    """Test iteration operations."""

    def test_iter_over_items(self, llm_client, embedder):
        """Test iterating over set items."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        titles = ["Book A", "Book B", "Book C"]
        for title in titles:
            books.add(BookEntry(title=title))

        collected = [b.title for b in books]
        assert len(collected) == 3
        assert set(collected) == set(titles)

    def test_len_operator(self, llm_client, embedder):
        """Test len() operator."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        assert len(books) == 0

        for i in range(5):
            books.add(BookEntry(title=f"Book_{i}"))

        assert len(books) == 5


class TestAutoSetFeedText:
    """Test feed_text extraction."""

    def test_feed_text_populates_set(self, llm_client, embedder):
        """Test feeding text extracts and deduplicates."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        books.feed_text("Some text about popular books and authors")

        # In mock mode, should have mock items
        assert not books.empty()
        assert len(books) > 0

    def test_feed_text_maintains_uniqueness(self, llm_client, embedder):
        """Test that feed_text maintains deduplication."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        # Manually add some books
        books.add(BookEntry(title="Python Guide"))
        books.add(BookEntry(title="Java Basics"))
        initial_size = len(books)

        # Feed text (in mock mode, generates mock data that might have same title)
        books.feed_text("More information about programming books")

        # Size should be >= initial (due to mock data being indeterminate)
        assert len(books) >= initial_size


class TestAutoSetRepr:
    """Test string representations."""

    def test_repr(self, llm_client, embedder):
        """Test __repr__ method."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        repr_str = repr(books)
        assert "AutoSet" in repr_str
        assert "BookEntry" in repr_str
        assert "0" in repr_str

    def test_str(self, llm_client, embedder):
        """Test __str__ method."""
        books = AutoSet(
            item_schema=BookEntry,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.title,
        )

        books.add(BookEntry(title="Book One"))
        books.add(BookEntry(title="Book Two"))

        str_repr = str(books)
        assert "AutoSet" in str_repr
        assert "2" in str_repr
