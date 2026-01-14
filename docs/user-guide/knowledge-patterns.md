# Knowledge Patterns

Hyper-Extract provides three fundamental knowledge patterns, each optimized for different extraction scenarios. Understanding when to use each pattern is key to effective knowledge extraction.

---

## Overview

| Pattern | Use Case | Deduplication | Merge Strategy |
|---------|----------|---------------|----------------|
| **UnitKnowledge** | Single object per document | N/A | Field-level merge |
| **ListKnowledge** | Multiple independent items | Basic | Append |
| **SetKnowledge** | Unique collection | Automatic | Configurable |

---

## UnitKnowledge Pattern

### When to Use

Use `UnitKnowledge` when you want to extract **exactly one structured object** from a document, regardless of its length.

**Perfect for**:
- Document summaries
- Article metadata (title, author, date)
- Aggregate statistics
- Overall sentiment analysis
- Document classification

### How It Works

1. **Extraction**: Processes text in chunks, extracting a schema instance from each
2. **Merging**: Uses "first-wins" strategy - first extraction populates fields, subsequent extractions only fill missing values
3. **Result**: Single consolidated object with information from entire document

### Example: Document Metadata

```python
from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperextract.knowledge.generic import UnitKnowledge

# Define schema
class DocumentMetadata(BaseModel):
    title: str = Field(default="", description="Document title")
    author: str = Field(default="", description="Primary author")
    publication_date: str = Field(default="", description="Publication date")
    category: str = Field(default="", description="Document category")
    summary: str = Field(default="", description="Brief summary")
    word_count_estimate: int = Field(default=0, description="Approximate word count")

# Initialize
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

metadata = UnitKnowledge(
    data_schema=DocumentMetadata,
    llm_client=llm,
    embedder=embedder
)

# Extract
long_article = """
[Your long article text here...]
"""
metadata.extract(long_article)

# Access single consolidated object
print(metadata.data.title)
print(metadata.data.summary)
```

### Indexing Strategy

Each non-null field is indexed separately, allowing field-specific semantic search:

```python
metadata.build_index()

# Search across all fields
results = metadata.search("machine learning applications", k=5)
```

---

## ListKnowledge Pattern

### When to Use

Use `ListKnowledge` when you need to extract **multiple independent items** of the same type from a document.

**Perfect for**:
- Entity lists (people, organizations, locations)
- Event sequences
- Product mentions
- Citation extraction
- Task lists

### How It Works

1. **Extraction**: Processes text in chunks, extracting multiple items from each
2. **Merging**: Appends all items with basic deduplication (exact matches only)
3. **Result**: List of all extracted items

### Example: Entity Extraction

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from hyperextract.knowledge.generic import ListKnowledge

# Define item schema
class Person(BaseModel):
    name: str = Field(..., description="Person's full name")
    role: Optional[str] = Field(None, description="Their role or title")
    organization: Optional[str] = Field(None, description="Associated organization")
    context: Optional[str] = Field(None, description="Context of mention")

# Initialize
people = ListKnowledge(
    item_schema=Person,  # Note: item_schema, not data_schema
    llm_client=llm,
    embedder=embedder
)

# Extract
text = """
Dr. Sarah Johnson, the lead researcher at MIT, collaborated with 
Professor Michael Chen from Stanford University. The project manager, 
Emily Rodriguez from Google, coordinated the efforts...
"""
people.extract(text)

# Access list of items
for person in people.items:
    print(f"{person.name} - {person.role} at {person.organization}")

# Or use the property
print(f"Total people extracted: {len(people.items)}")
```

### List Operations

`ListKnowledge` supports Pythonic list operations:

```python
# Append new items
people.append(Person(name="John Doe", role="Engineer"))

# Extend with multiple items
new_people = [
    Person(name="Alice Smith", role="Designer"),
    Person(name="Bob Jones", role="Manager")
]
people.extend(new_people)

# Access by index
first_person = people[0]

# Iterate
for person in people:
    print(person.name)

# Length
count = len(people)

# Check membership
if some_person in people:
    print("Found!")
```

### Indexing Strategy

Each item in the list is indexed independently:

```python
people.build_index()

# Search returns relevant items with scores
results = people.search("researchers from MIT", k=3)
for doc, score in results:
    print(f"Match: {doc.page_content} (score: {score})")
```

---

## SetKnowledge Pattern

### When to Use

Use `SetKnowledge` when you need a **unique collection** with automatic deduplication based on a key field.

**Perfect for**:
- Keywords/tags (deduplicated by term)
- Unique entities (deduplicated by ID or name)
- Topic modeling (unique topics)
- Skill extraction (unique skills)
- Location mentions (unique places)

### How It Works

1. **Extraction**: Processes text in chunks, extracting multiple items
2. **Deduplication**: Uses specified `unique_key` field to identify duplicates
3. **Merging**: Configurable strategy (keep_old, keep_new, field_merge, llm_merge)
4. **Result**: Unique collection with smart duplicate handling

### Example: Keyword Extraction with Deduplication

```python
from pydantic import BaseModel, Field
from typing import Optional
from hyperextract.knowledge.generic import SetKnowledge, MergeItemStrategy

# Define item schema with unique key
class Keyword(BaseModel):
    term: str = Field(..., description="The keyword or phrase")
    category: Optional[str] = Field(None, description="Keyword category")
    importance: Optional[str] = Field(None, description="Importance level")
    context: Optional[str] = Field(None, description="Usage context")

# Initialize with unique_key
keywords = SetKnowledge(
    item_schema=Keyword,
    llm_client=llm,
    embedder=embedder,
    unique_key="term",  # Deduplicate by term
    merge_strategy=MergeItemStrategy.FIELD_MERGE  # Fill missing fields
)

# Extract
text = """
Machine learning is a key technology. Deep learning, a subset of 
machine learning, has revolutionized AI. Neural networks are fundamental 
to deep learning...
"""
keywords.extract(text)

# Access unique items
for kw in keywords.items:
    print(f"{kw.term}: {kw.category} ({kw.importance})")
```

### Merge Strategies

#### 1. KEEP_OLD
Keeps existing item, discards new duplicate:
```python
keywords = SetKnowledge(
    item_schema=Keyword,
    llm_client=llm,
    embedder=embedder,
    unique_key="term",
    merge_strategy=MergeItemStrategy.KEEP_OLD
)
```

#### 2. KEEP_NEW (Default)
Replaces existing item with new one:
```python
merge_strategy=MergeItemStrategy.KEEP_NEW
```

#### 3. FIELD_MERGE
Merges fields - new values fill old's None/empty fields:
```python
merge_strategy=MergeItemStrategy.FIELD_MERGE
```

#### 4. LLM_MERGE
Uses LLM to intelligently merge both items:
```python
merge_strategy=MergeItemStrategy.LLM_MERGE
```

### Set Operations

`SetKnowledge` supports set operations:

```python
# Union: combine two sets
combined = keywords1 | keywords2

# Intersection: common items
common = keywords1 & keywords2

# Difference: items in first but not second
unique = keywords1 - keywords2

# Symmetric difference: items in either but not both
exclusive = keywords1 ^ keywords2
```

### Indexing Strategy

Like ListKnowledge, each unique item is indexed:

```python
keywords.build_index()
results = keywords.search("AI technologies", k=5)
```

---

## Choosing the Right Pattern

### Decision Tree

```
Is it a single object per document?
├─ Yes → Use UnitKnowledge
└─ No → Are duplicates acceptable?
    ├─ Yes → Use ListKnowledge
    └─ No → Use SetKnowledge (specify unique_key)
```

### Examples by Domain

**News Article Processing**:
- `UnitKnowledge`: Article metadata, summary
- `ListKnowledge`: All mentioned events
- `SetKnowledge`: Unique entities, locations

**Research Paper Analysis**:
- `UnitKnowledge`: Paper metadata, abstract
- `ListKnowledge`: All citations
- `SetKnowledge`: Unique keywords, methodologies

**Customer Reviews**:
- `UnitKnowledge`: Overall sentiment, rating
- `ListKnowledge`: All complaints/praises
- `SetKnowledge`: Unique features mentioned

---

## Advanced: Custom Patterns

You can create custom patterns by subclassing `BaseKnowledge`:

```python
from hyperextract.knowledge.base import BaseKnowledge

class MyCustomPattern(BaseKnowledge[MySchema]):
    def _merge_strategy(self, old_data, new_data):
        # Implement custom merge logic
        pass
    
    def _build_documents_for_indexing(self):
        # Implement custom indexing logic
        pass
```

---

## Next Steps

- Explore [API Reference](../api/base.md) for detailed method documentation
- Check [Getting Started](getting-started.md) for setup instructions
- Review [examples](https://github.com/your-username/hyper-extract/tree/main/examples) for complete code samples
