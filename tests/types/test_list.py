"""Tests for AutoList - list extraction pattern."""

import pytest
from pydantic import BaseModel, Field
from hyperextract.types.list import AutoList


class Task(BaseModel):
    """Test schema for list items."""

    title: str = Field(default="", description="Task title")
    priority: int = Field(default=1)
    done: bool = Field(default=False)


class Person(BaseModel):
    """Test schema for people."""

    name: str = Field(default="", description="Person's name")
    age: int = Field(default=0)


class TestAutoListBasics:
    """Test basic AutoList functionality."""

    def test_initialization(self, llm_client, embedder):
        """Test AutoList initialization."""
        task_list = AutoList(
            item_schema=Task, llm_client=llm_client, embedder=embedder
        )

        assert task_list.item_schema == Task
        assert task_list.empty()
        assert len(task_list) == 0

    def test_properties(self, llm_client, embedder):
        """Test AutoList properties."""
        task_list = AutoList(Task, llm_client, embedder)

        # Check items property
        assert task_list.items == []
        assert isinstance(task_list.items, list)


class TestAutoListFeed:
    """Test feeding text to AutoList."""

    def test_feed_text_populates_list(self, llm_client, embedder):
        """Test feeding text extracts items into list."""
        task_list = AutoList(Task, llm_client, embedder)

        task_list.feed_text("Buy milk and walk the dog")

        assert not task_list.empty()
        assert len(task_list) > 0
        assert isinstance(task_list[0], Task)

    def test_feed_text_appends(self, llm_client, embedder):
        """Test that feed_text appends, not replaces."""
        task_list = AutoList(Task, llm_client, embedder)

        # Manually set initial items
        task_list._data.items = [Task(title="Item 1", priority=1)]
        initial_len = len(task_list)

        # Feed more text (in mock mode, this adds mock items)
        task_list.feed_text("""
        Q1 2024 Sprint Tasks:
        1. Implement user authentication (High priority)
        2. Optimize database queries (Medium priority)  
        3. Write API documentation (Low priority)
        4. Security audit review (Critical priority)
        5. Deploy staging environment (High priority)
        """)

        # Should have more items
        assert len(task_list) >= initial_len


class TestAutoListIndexing:
    """Test indexing and slicing operations."""

    def test_integer_indexing(self, llm_client, embedder):
        """Test integer indexing returns single item."""
        task_list = AutoList(Task, llm_client, embedder)

        t1 = Task(title="First", priority=1)
        t2 = Task(title="Second", priority=2)
        t3 = Task(title="Third", priority=3)
        task_list._data.items = [t1, t2, t3]

        assert task_list[0] == t1
        assert task_list[1] == t2
        assert task_list[-1] == t3

    def test_out_of_bounds_indexing(self, llm_client, embedder):
        """Test IndexError for out of bounds access."""
        task_list = AutoList(Task, llm_client, embedder)
        task_list._data.items = [Task(title="Only", priority=1)]

        with pytest.raises(IndexError):
            _ = task_list[10]

    def test_slice_returns_new_list(self, llm_client, embedder):
        """Test slicing returns new AutoList instance."""
        task_list = AutoList(Task, llm_client, embedder)

        t1 = Task(title="First", priority=1)
        t2 = Task(title="Second", priority=2)
        t3 = Task(title="Third", priority=3)
        task_list._data.items = [t1, t2, t3]

        # Test slice
        sliced = task_list[0:2]

        assert isinstance(sliced, AutoList)
        assert sliced.item_schema == Task
        assert len(sliced) == 2
        assert sliced[0] == t1
        assert sliced[1] == t2

    def test_slice_with_step(self, llm_client, embedder):
        """Test slicing with step."""
        task_list = AutoList(Task, llm_client, embedder)

        items = [Task(title=f"Item {i}", priority=i) for i in range(5)]
        task_list._data.items = items

        sliced = task_list[::2]
        assert len(sliced) == 3


class TestAutoListSetItem:
    """Test item assignment."""

    def test_setitem_updates_item(self, llm_client, embedder):
        """Test __setitem__ replaces item at index."""
        task_list = AutoList(Task, llm_client, embedder)

        t1 = Task(title="First")
        t2 = Task(title="Second")
        task_list._data.items = [t1, t2]

        new_item = Task(title="Updated")
        task_list[0] = new_item

        assert task_list[0].title == "Updated"
        assert task_list[1] == t2

    def test_setitem_invalid_schema(self, llm_client, embedder):
        """Test that setting wrong schema raises error."""
        task_list = AutoList(Task, llm_client, embedder)
        task_list._data.items = [Task(title="Item")]

        with pytest.raises(TypeError):
            task_list[0] = Person(name="Not a Task")


class TestAutoListAddition:
    """Test list concatenation."""

    def test_list_plus_list(self, llm_client, embedder):
        """Test AutoList + AutoList merges both lists."""
        list1 = AutoList(Task, llm_client, embedder)
        list1._data.items = [Task(title="A", priority=1)]

        list2 = AutoList(Task, llm_client, embedder)
        list2._data.items = [Task(title="B", priority=2)]

        result = list1 + list2

        assert isinstance(result, AutoList)
        assert len(result) == 2
        assert result[0].title == "A"
        assert result[1].title == "B"

    def test_list_plus_model(self, llm_client, embedder):
        """Test AutoList + AutoModel appends model."""
        from hyperextract.types.model import AutoModel

        list_obj = AutoList(Task, llm_client, embedder)
        list_obj._data.items = [Task(title="Existing", priority=1)]

        model = AutoModel(Task, llm_client, embedder)
        model._data = Task(title="New Item", priority=2)

        result = list_obj + model

        assert isinstance(result, AutoList)
        assert len(result) == 2
        assert result[1].title == "New Item"


class TestAutoListDeletion:
    """Test item deletion."""

    def test_delitem(self, llm_client, embedder):
        """Test __delitem__ removes item at index."""
        task_list = AutoList(Task, llm_client, embedder)

        items = [Task(title=f"Item {i}") for i in range(3)]
        task_list._data.items = items

        del task_list[1]

        assert len(task_list) == 2
        assert task_list[0].title == "Item 0"
        assert task_list[1].title == "Item 2"


class TestAutoListLen:
    """Test length operations."""

    def test_len(self, llm_client, embedder):
        """Test __len__ returns list length."""
        task_list = AutoList(Task, llm_client, embedder)
        assert len(task_list) == 0

        task_list._data.items = [Task(title=str(i)) for i in range(5)]
        assert len(task_list) == 5
