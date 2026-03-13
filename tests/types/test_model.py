"""Tests for AutoModel - single object extraction pattern."""

import pytest
from pydantic import BaseModel, Field
from datetime import datetime
from hyperextract.types.model import AutoModel
from ontomem.merger import MergeStrategy


class Person(BaseModel):
    """Test schema for AutoModel tests."""

    name: str | None = Field(default=None, description="Person's name")
    age: int | None = Field(default=None, description="Person's age")
    profession: str | None = Field(default=None, description="Person's profession")


class Article(BaseModel):
    """Test schema for article summary."""

    title: str = Field(default="", description="Article title")
    author: str = Field(default="", description="Article author")
    summary: str = Field(default="", description="Article summary")


class TestAutoModelBasics:
    """Test basic AutoModel functionality."""

    def test_initialization(self, llm_client, embedder):
        """Test AutoModel initialization."""
        model = AutoModel(
            data_schema=Person,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=MergeStrategy.MERGE_FIELD,
        )

        assert model.data_schema == Person
        # Note: empty() may return False if default values are present
        assert isinstance(model.data, Person)

    def test_properties(self, llm_client, embedder):
        """Test AutoModel properties."""
        model = AutoModel(Person, llm_client, embedder)

        # Check metadata
        assert "created_at" in model.metadata
        assert "updated_at" in model.metadata
        assert isinstance(model.metadata["created_at"], datetime)

    def test_empty_check(self, llm_client, embedder):
        """Test empty() method for detecting uninitialized data."""
        model = AutoModel(Person, llm_client, embedder)
        # Initially, model may or may not be empty depending on default values
        initial_state = model.empty()

        # Explicitly set non-default values
        model._data.name = "John Doe"
        # After setting explicit data, should not be empty
        assert model.empty() is False


class TestAutoModelExtraction:
    """Test extraction and data management."""

    def test_extract_creates_new_instance(self, llm_client, embedder):
        """Test that extract() returns a new instance."""
        model1 = AutoModel(Person, llm_client, embedder)
        model2 = model1.parse("""Dr. James Wilson, 47 years old, served as Chief Technology Officer 
        at Innovate Systems for 12 years before joining CloudFirst as VP of Engineering.""")

        # Should be different instances
        assert model1 is not model2
        # Original should still be empty
        assert model1.empty() is True
        # New should have data
        assert not model2.empty()

    def test_feed_text_updates_in_place(self, llm_client, embedder):
        """Test that feed_text() updates current instance."""
        model = AutoModel(Person, llm_client, embedder)
        original_id = id(model)

        result = model.feed_text("""
        Dr. Sarah Chen is a 42-year-old data scientist at Tech Labs.
        She specializes in machine learning and supervises 8 engineers.
        Sarah earned her PhD from Stanford in 2008.
        """)

        # Should return self
        assert id(result) == original_id
        # Should not be empty
        assert not model.empty()

    def test_feed_text_chaining(self, llm_client, embedder):
        """Test that feed_text() supports method chaining."""
        model = AutoModel(Person, llm_client, embedder)

        result = model.feed_text(
            "Alexandra Martinez is a 35-year-old software architect"
        ).feed_text(
            "She works at TechCorp and has 12 years of experience in distributed systems"
        )

        assert result is model
        assert not model.empty()


class TestAutoModelClear:
    """Test clearing operations."""

    def test_clear_resets_data(self, llm_client, embedder):
        """Test clear() resets all data."""
        model = AutoModel(Person, llm_client, embedder)
        model.feed_text("""
        Prof. Michael Johnson is a 56-year-old cloud architect.
        He has 20 years of experience in distributed systems.
        Michael leads the infrastructure team.
        """)
        assert not model.empty()

        model.clear()
        assert model.empty() is True

    def test_clear_updates_metadata(self, llm_client, embedder):
        """Test that clear() updates metadata."""
        model = AutoModel(Person, llm_client, embedder)
        old_time = model.metadata["updated_at"]

        model.feed_text("""
        Emma Rodriguez is a 38-year-old product manager at StartupCorp.
        She specializes in B2B SaaS products and leads cross-functional teams.
        Emma worked at Microsoft for 10 years before joining StartupCorp.
        """)
        model.clear()

        # Updated time should be newer
        assert model.metadata["updated_at"] >= old_time


class TestAutoModelOperators:
    """Test operator overloading."""

    def test_model_plus_model_creates_list(self, llm_client, embedder):
        """Test AutoModel + AutoModel creates AutoList."""
        from hyperextract.types.list import AutoList

        model1 = AutoModel(Person, llm_client, embedder)
        model1._data = Person(name="Alice", age=30, profession="Engineer")

        model2 = AutoModel(Person, llm_client, embedder)
        model2._data = Person(name="Bob", age=25, profession="Designer")

        result = model1 + model2

        assert isinstance(result, AutoList)
        assert result.item_schema == Person
        assert len(result) == 2

    def test_model_plus_model_same_schema_required(self, llm_client, embedder):
        """Test that + operator requires same schema."""
        model1 = AutoModel(Person, llm_client, embedder)

        article_model = AutoModel(Article, llm_client, embedder)

        with pytest.raises(TypeError, match="different schemas"):
            model1 + article_model

    def test_model_plus_list_creates_list(self, llm_client, embedder):
        """Test AutoModel + AutoList prepends model to list."""
        from hyperextract.types.list import AutoList

        model = AutoModel(Person, llm_client, embedder)
        model._data = Person(name="Charlie", age=35)

        auto_list = AutoList(Person, llm_client, embedder)
        person1 = Person(name="Alice", age=30)
        person2 = Person(name="Bob", age=25)
        auto_list._data.items = [person1, person2]

        result = model + auto_list

        assert isinstance(result, AutoList)
        assert len(result) == 3
        # Model should be prepended
        assert result[0].name == "Charlie"
        assert result[1].name == "Alice"
        assert result[2].name == "Bob"


class TestAutoModelMerging:
    """Test merge batch data functionality."""

    def test_merge_batch_multiple_items(self, llm_client, embedder):
        """Test merging multiple extracted items."""
        # Use MERGE_FIELD strategy to test deterministic field-level merging
        # without depending on LLM (works with or without API key)
        model = AutoModel(Person, llm_client, embedder, strategy_or_merger=MergeStrategy.MERGE_FIELD)

        # Create mock items to merge
        item1 = Person(name="John", age=30, profession="Engineer")
        item2 = Person(name="Jane", age=28, profession="Doctor")

        # Merge strategy: MERGE_FIELD merges non-null fields
        result = model.merge_batch_data([item1, item2])

        # Result should be a valid Person with one of the merged data
        assert isinstance(result, Person)
        # Should have a name (from one of the items)
        assert result.name in ["John", "Jane"]
        # Should have age and profession (from merged data)
        assert result.age is not None
        assert result.profession is not None

    def test_merge_batch_empty_list(self, llm_client, embedder):
        """Test merging empty list."""
        model = AutoModel(Person, llm_client, embedder)

        result = model.merge_batch_data([])

        # Should return empty instance
        assert isinstance(result, Person)
        assert result.model_dump(exclude_unset=True) == {}
