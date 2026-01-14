# SetKnowledge API

::: hyperextract.knowledge.generic.set.SetKnowledge
    options:
      show_root_heading: true
      show_source: true
      heading_level: 2

## Overview

`SetKnowledge` implements the unique collection pattern with automatic deduplication. It extracts items and ensures uniqueness based on a user-specified key field, with configurable merge strategies for handling duplicates.

## Class Signature

```python
class SetKnowledge(BaseKnowledge[ItemSetSchema[Item]], Generic[Item]):
    """Set Knowledge Pattern - extracts a unique collection of objects."""
```

## Key Characteristics

- **Extraction Target**: Unique collection of structured objects
- **Deduplication**: Based on `unique_key` field
- **Merge Strategy**: Configurable (keep_old/keep_new/field_merge/llm_merge)
- **Internal Storage**: Dict for O(1) lookup
- **External Interface**: List-like access via `items` property

## Initialization

```python
from hyperextract.knowledge.generic import SetKnowledge, MergeItemStrategy
from pydantic import BaseModel, Field

class Keyword(BaseModel):
    term: str = Field(..., description="Keyword or phrase")
    category: Optional[str] = Field(None, description="Category")
    importance: Optional[str] = Field(None, description="Importance level")

keywords = SetKnowledge(
    item_schema=Keyword,
    llm_client=llm,
    embedder=embedder,
    unique_key="term",  # Deduplicate by this field
    merge_strategy=MergeItemStrategy.FIELD_MERGE
)
```

### Additional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `unique_key` | `str` | Required | Field name for deduplication |
| `merge_strategy` | `MergeItemStrategy` | `KEEP_NEW` | How to handle duplicates |

## Merge Strategies

### KEEP_OLD
Keep existing item, discard new duplicate:
```python
SetKnowledge(
    ...,
    merge_strategy=MergeItemStrategy.KEEP_OLD
)
```

**Example**:
```python
# Existing: Keyword(term="AI", category="Tech", importance="High")
# New: Keyword(term="AI", category="Science", importance="Medium")
# Result: Keyword(term="AI", category="Tech", importance="High")  # Old kept
```

### KEEP_NEW (Default)
Replace existing with new:
```python
SetKnowledge(
    ...,
    merge_strategy=MergeItemStrategy.KEEP_NEW
)
```

**Example**:
```python
# Existing: Keyword(term="AI", category="Tech", importance="High")
# New: Keyword(term="AI", category="Science", importance="Medium")
# Result: Keyword(term="AI", category="Science", importance="Medium")  # New kept
```

### FIELD_MERGE
Merge fields - new fills old's None/empty fields:
```python
SetKnowledge(
    ...,
    merge_strategy=MergeItemStrategy.FIELD_MERGE
)
```

**Example**:
```python
# Existing: Keyword(term="AI", category="Tech", importance=None)
# New: Keyword(term="AI", category=None, importance="High")
# Result: Keyword(term="AI", category="Tech", importance="High")  # Combined
```

### LLM_MERGE
Use LLM to intelligently merge:
```python
SetKnowledge(
    ...,
    merge_strategy=MergeItemStrategy.LLM_MERGE
)
```

**Example**:
```python
# Existing: Keyword(term="ML", category="AI", importance="High")
# New: Keyword(term="ML", category="Data Science", importance="Critical")
# LLM decides: Keyword(term="ML", category="AI/Data Science", importance="Critical")
```

## Properties

### `items`
```python
@property
def items(self) -> List[Item]
```

Returns list of unique items:
```python
for keyword in keywords.items:
    print(f"{keyword.term}: {keyword.category}")
```

### `unique_keys`
```python
@property
def unique_keys(self) -> List[str]
```

Returns list of unique key values:
```python
all_terms = keywords.unique_keys
print(f"Unique keywords: {', '.join(all_terms)}")
```

## Methods

### `extract()`

Extracts items with automatic deduplication:

```python
text = """
Machine learning is a key AI technology. Deep learning, a subset of 
machine learning, has revolutionized AI. Neural networks are fundamental 
to deep learning. Machine learning continues to evolve.
"""

keywords.extract(text)
# "machine learning" appears twice but stored once
print(f"Extracted {len(keywords)} unique keywords")
```

### `add_item()`
```python
def add_item(self, item: Item) -> bool
```

Manually add an item, applying merge strategy if duplicate:

```python
new_keyword = Keyword(term="Python", category="Language")
added = keywords.add_item(new_keyword)
print(f"Item added: {added}")
```

**Returns**: `True` if new item added, `False` if merged with existing

### `get_item()`
```python
def get_item(self, key_value: str) -> Optional[Item]
```

Retrieve item by unique key value:

```python
ai_keyword = keywords.get_item("AI")
if ai_keyword:
    print(f"Found: {ai_keyword.category}")
```

### `remove_item()`
```python
def remove_item(self, key_value: str) -> bool
```

Remove item by unique key:

```python
removed = keywords.remove_item("obsolete_term")
print(f"Removed: {removed}")
```

### `contains()`
```python
def contains(self, key_value: str) -> bool
```

Check if key exists:

```python
if keywords.contains("Python"):
    print("Python is in the set")
```

## Set Operations

`SetKnowledge` supports mathematical set operations:

### Union (`|`)
Combine two sets:
```python
combined = keywords1 | keywords2
# All unique items from both sets
```

### Intersection (`&`)
Common items:
```python
common = keywords1 & keywords2
# Only items present in both sets
```

### Difference (`-`)
Items in first but not second:
```python
unique_to_first = keywords1 - keywords2
# Items only in keywords1
```

### Symmetric Difference (`^`)
Items in either but not both:
```python
exclusive = keywords1 ^ keywords2
# Items in one set but not the other
```

### Example:
```python
tech_keywords = SetKnowledge(item_schema=Keyword, ...)
science_keywords = SetKnowledge(item_schema=Keyword, ...)

# Extract from different sources
tech_keywords.extract(tech_article)
science_keywords.extract(science_article)

# Find common keywords
common = tech_keywords & science_keywords
print(f"Keywords in both: {[k.term for k in common.items]}")

# Find tech-specific keywords
tech_only = tech_keywords - science_keywords
print(f"Tech-specific: {[k.term for k in tech_only.items]}")
```

## Indexing and Search

```python
keywords.build_index()

results = keywords.search("artificial intelligence topics", k=5)
for doc, score in results:
    print(f"Match (score {score:.3f}): {doc.page_content}")
```

## Use Cases

### Unique Entities
```python
class Entity(BaseModel):
    name: str = Field(..., description="Entity name")
    type: str = Field(..., description="Entity type")
    description: Optional[str] = None

entities = SetKnowledge(
    item_schema=Entity,
    llm_client=llm,
    embedder=embedder,
    unique_key="name",
    merge_strategy=MergeItemStrategy.FIELD_MERGE
)
```

### Topic Modeling
```python
class Topic(BaseModel):
    topic: str = Field(..., description="Topic name")
    subtopics: List[str] = Field(default_factory=list)
    relevance: Optional[str] = None

topics = SetKnowledge(
    item_schema=Topic,
    llm_client=llm,
    embedder=embedder,
    unique_key="topic",
    merge_strategy=MergeItemStrategy.LLM_MERGE  # Smart merging
)
```

### Skills Extraction
```python
class Skill(BaseModel):
    skill_name: str = Field(..., description="Skill name")
    proficiency: Optional[str] = None
    years_experience: Optional[int] = None

skills = SetKnowledge(
    item_schema=Skill,
    llm_client=llm,
    embedder=embedder,
    unique_key="skill_name",
    merge_strategy=MergeItemStrategy.KEEP_NEW  # Latest info
)
```

## Advanced Usage

### Custom Merge Logic

For complex merging, use `LLM_MERGE` or subclass:

```python
class SmartSetKnowledge(SetKnowledge[Item]):
    def _merge_items_llm(self, old_item: Item, new_item: Item) -> Item:
        # Custom LLM prompt for merging
        custom_prompt = f'''
        Intelligently merge these two items:
        Old: {old_item.model_dump_json()}
        New: {new_item.model_dump_json()}
        
        Rules:
        - Prefer more detailed information
        - Combine complementary fields
        - Resolve conflicts logically
        '''
        # Use your LLM to merge
        ...
```

### Filtering and Transformation

```python
# Filter by field
important = [k for k in keywords if k.importance == "High"]

# Group by category
from collections import defaultdict
by_category = defaultdict(list)
for k in keywords.items:
    by_category[k.category].append(k)

# Transform
terms_only = [k.term for k in keywords.items]
```

## Best Practices

1. **Choose Unique Key Carefully**:
   ```python
   # Good: Natural unique identifier
   unique_key="email"  # For people
   unique_key="isbn"   # For books
   
   # Careful: May have false duplicates
   unique_key="name"   # "John Smith" appears twice
   ```

2. **Merge Strategy Selection**:
   - `KEEP_OLD`: When first mention is most authoritative
   - `KEEP_NEW`: When latest information is better
   - `FIELD_MERGE`: When information is complementary
   - `LLM_MERGE`: When conflicts need intelligent resolution

3. **Performance Considerations**:
   ```python
   # LLM_MERGE is slower (makes LLM calls)
   SetKnowledge(..., merge_strategy=MergeItemStrategy.LLM_MERGE)
   
   # For large datasets, consider FIELD_MERGE or KEEP_NEW
   ```

4. **Unique Key Validation**:
   ```python
   # Ensure unique_key field exists and is required
   class Item(BaseModel):
       id: str = Field(..., description="Unique ID")  # Required!
       ...
   
   knowledge = SetKnowledge(..., unique_key="id")
   ```

## Serialization

```python
# Save
keywords.dump("./keywords_set")

# Load (preserves uniqueness)
loaded = SetKnowledge.load(
    "./keywords_set",
    item_schema=Keyword,
    llm_client=llm,
    embedder=embedder,
    unique_key="term",  # Must specify again
    merge_strategy=MergeItemStrategy.FIELD_MERGE
)
```

## Comparison

| Feature | ListKnowledge | SetKnowledge |
|---------|---------------|--------------|
| Duplicates | Allowed | Prevented by unique_key |
| Merge Strategies | Simple append | 4 configurable strategies |
| Storage | List | Dict (O(1) lookup) |
| Set Operations | No | Yes (∪, ∩, -, ⊕) |
| Use Case | Simple collections | Unique items, deduplication |

## See Also

- [ListKnowledge API](list.md) - Multi-item list extraction
- [BaseKnowledge API](base.md) - Base class documentation
- [Knowledge Patterns Guide](../user-guide/knowledge-patterns.md) - Pattern selection guide
