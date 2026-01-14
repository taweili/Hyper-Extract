# API Reference

This section provides detailed API documentation for all Hyper-Extract classes and methods.

## Module Structure

```
hyperextract/
├── knowledge/
│   ├── base.py          # BaseKnowledge abstract class
│   └── generic/
│       ├── unit.py      # UnitKnowledge
│       ├── list.py      # ListKnowledge
│       └── set.py       # SetKnowledge
```

## Quick Links

- [BaseKnowledge](base.md) - Abstract base class for all knowledge patterns
- [UnitKnowledge](unit.md) - Single-object extraction pattern
- [ListKnowledge](list.md) - Multi-item list extraction pattern
- [SetKnowledge](set.md) - Unique collection with deduplication

## Common Patterns

### Initialization

All knowledge classes share a common initialization pattern:

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

knowledge = PatternClass(
    data_schema=YourSchema,  # or item_schema for List/Set
    llm_client=llm,
    embedder=embedder,
    chunk_size=2000,
    chunk_overlap=200
)
```

### Core Methods

Every knowledge class implements these methods:

| Method | Description | Returns |
|--------|-------------|---------|
| `extract(text)` | Extract knowledge from text | None (updates internal state) |
| `build_index()` | Build FAISS vector index | None |
| `search(query, k)` | Semantic search | List of (Document, score) tuples |
| `dump(path)` | Save to disk | None |
| `load(path, ...)` | Load from disk | Knowledge instance |

### Type Hints

All classes are fully typed with Python generics:

```python
from hyperextract.knowledge.generic import UnitKnowledge
from pydantic import BaseModel

class MySchema(BaseModel):
    field: str

# Type-safe: knowledge.data is of type MySchema
knowledge: UnitKnowledge[MySchema] = UnitKnowledge(
    data_schema=MySchema,
    llm_client=llm,
    embedder=embedder
)
```

## Next: Detailed API Docs

- [BaseKnowledge API](base.md)
- [UnitKnowledge API](unit.md)  
- [ListKnowledge API](list.md)
- [SetKnowledge API](set.md)
