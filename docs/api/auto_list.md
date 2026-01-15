# AutoList API

::: hyperextract.core.list.AutoList
    options:
      show_root_heading: true
      show_source: true
      heading_level: 2

## Overview

`AutoList` implements the multi-item list extraction pattern. It extracts multiple independent objects of the same type from a document, suitable for entity lists, events, citations, and more.

## Class Signature

```python
class AutoList(BaseAutoType[ItemListSchema[Item]], Generic[Item]):
    """List Knowledge Pattern - extracts a collection of objects from text."""
```

## Key Characteristics

- **Extraction Target**: A collection of structured objects
- **Merge Strategy**: Append with basic deduplication (exact matches)
- **Indexing Strategy**: Each item indexed independently
- **Container**: Uses `ItemListSchema[Item]` wrapper

## Initialization

```python
from hyperextract.core import AutoList
from pydantic import BaseModel, Field
from typing import Optional

class Person(BaseModel):
    name: str = Field(..., description="Person's full name")
    role: Optional[str] = Field(None, description="Role or title")
    organization: Optional[str] = Field(None, description="Organization")

people = AutoList(
    item_schema=Person,  # Note: item_schema, not data_schema!
    llm_client=llm,
    embedder=embedder
)
```

## Properties

### `items`
```python
@property
def items(self) -> List[Item]
```

Returns the list of extracted items.

```python
people.extract(text)
for person in people.items:
    print(f"{person.name} - {person.role}")
```

### `data`
```python
@property
def data(self) -> ItemListSchema[Item]
```

Returns the container wrapper with `.items` attribute.

```python
container = people.data
print(len(container.items))
```

## List Operations

`AutoList` supports Pythonic list operations:

### Indexing
```python
first = people[0]
last = people[-1]
slice_items = people[1:3]
```

### Iteration
```python
for person in people:
    print(person.name)
```

### Length
```python
count = len(people)
```

### Membership
```python
if some_person in people:
    print("Found!")
```

### Append
```python
people.append(Person(name="John Doe", role="Engineer"))
```

### Extend
```python
new_people = [
    Person(name="Alice", role="Designer"),
    Person(name="Bob", role="Manager")
]
people.extend(new_people)
```

### Clear
```python
people.clear()  # Remove all items
```

## Methods

### `extract()`

Extracts multiple items from text:

```python
text = """
Dr. Sarah Johnson leads the research team at MIT.
Professor Michael Chen from Stanford collaborated on the project.
Emily Rodriguez from Google coordinated the efforts.
"""

people.extract(text)
print(f"Extracted {len(people)} people")

for person in people:
    print(f"- {person.name}: {person.role} at {person.organization}")
```

**Multi-chunk behavior**:
- Each chunk extracts multiple items
- All items are appended together
- Basic deduplication removes exact duplicates

### `build_index()`

Indexes each item separately:

```python
people.build_index()
# Creates one document per item with all fields serialized
```

### `search()`

Searches across all items:

```python
results = people.search("researchers from MIT", k=3)
for doc, score in results:
    # doc.page_content contains serialized item
    # doc.metadata contains item index
    print(f"Match (score {score:.3f}): {doc.page_content}")
```

## Merge Strategy

Appends new items with basic deduplication:

```python
def _merge_strategy(
    self,
    old_data: ItemListSchema[Item],
    new_data: ItemListSchema[Item]
) -> ItemListSchema[Item]:
    """Append new items, removing exact duplicates."""
```

**Example**:
```python
# Old items
[Person(name="Alice", role="Engineer")]

# New items (from next chunk)
[Person(name="Bob", role="Designer"), 
 Person(name="Alice", role="Engineer")]  # Duplicate

# Merged result
[Person(name="Alice", role="Engineer"),
 Person(name="Bob", role="Designer")]
```

## Indexing Strategy

```python
def _build_documents_for_indexing(self) -> List[Document]:
    """Build one document per item."""
    return [
        Document(
            page_content=item.model_dump_json(),
            metadata={"item_index": i}
        )
        for i, item in enumerate(self.items)
    ]
```

## Use Cases

### Entity Extraction
```python
class Entity(BaseModel):
    name: str = Field(..., description="Entity name")
    type: str = Field(..., description="Entity type (person/org/location)")
    context: str = Field(default="", description="Surrounding context")

entities = AutoList(
    item_schema=Entity,
    llm_client=llm,
    embedder=embedder
)
```

### Event Extraction
```python
class Event(BaseModel):
    date: str = Field(..., description="Event date")
    description: str = Field(..., description="What happened")
    participants: List[str] = Field(default_factory=list)
    location: Optional[str] = None

events = AutoList(
    item_schema=Event,
    llm_client=llm,
    embedder=embedder
)
```

### Citation Extraction
```python
class Citation(BaseModel):
    authors: List[str] = Field(..., description="Author names")
    title: str = Field(..., description="Paper title")
    year: Optional[int] = None
    venue: Optional[str] = None

citations = AutoList(
    item_schema=Citation,
    llm_client=llm,
    embedder=embedder
)
```

## Advanced Usage

### Custom Deduplication

Subclass to implement custom deduplication:

```python
class SmartAutoList(AutoList[Item]):
    def _merge_strategy(self, old_data, new_data):
        # Custom deduplication logic
        existing_names = {item.name for item in old_data.items}
        unique_new = [
            item for item in new_data.items
            if item.name not in existing_names
        ]
        old_data.items.extend(unique_new)
        return old_data
```

### Filtering

```python
# Filter items after extraction
engineers = [p for p in people if p.role == "Engineer"]
mit_people = [p for p in people if "MIT" in (p.organization or "")]
```

### Sorting

```python
# Sort by field
sorted_people = sorted(people.items, key=lambda p: p.name)

# Sort by multiple fields
from operator import attrgetter
sorted_people = sorted(people.items, key=attrgetter('organization', 'name'))
```

## Best Practices

1. **Required vs Optional Fields**:
   ```python
   class Item(BaseModel):
       name: str = Field(..., description="Required field")  # Must have value
       details: Optional[str] = Field(None, description="Optional field")
   ```

2. **Field Descriptions**: Help LLM understand what to extract
   ```python
   date: str = Field(..., description="Date in YYYY-MM-DD format")
   ```

3. **List Fields**: Use `default_factory=list`
   ```python
   tags: List[str] = Field(default_factory=list, description="Tags")
   ```

4. **Chunk Size**: Smaller chunks for dense information
   ```python
   # For entity-rich text
   AutoList(..., chunk_size=1500, chunk_overlap=150)
   ```

## Serialization

```python
# Save
people.dump("./a_people")

# Load
loaded = AutoList.load(
    "./a_people",
    item_schema=Person,
    llm_client=llm,
    embedder=embedder
)

assert len(loaded) == len(people)
```

## Comparison with AutoSet

| Feature | AutoList | AutoSet |
|---------|---------------|--------------|
| Duplicates | Allowed (basic dedup) | Prevented (by unique_key) |
| Merge | Simple append | Configurable strategies |
| Use Case | Order matters, simple lists | Uniqueness required |

**When to use List vs Set**:
- Use **List** when: Order is important, items might legitimately appear multiple times
- Use **Set** when: Uniqueness is critical, need smart deduplication

## See Also

- [AutoSet API](set.md) - Unique collection with deduplication
- [BaseAutoType API](base.md) - Base class documentation
- [Knowledge Patterns Guide](../user-guide/knowledge-patterns.md) - Pattern selection
