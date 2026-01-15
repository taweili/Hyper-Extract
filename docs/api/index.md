# API Reference

This section provides detailed API documentation for all Hyper-Extract classes and methods.

## Module Structure

```
hyperextract/
├── knowledge/
│   ├── base.py          # BaseAutoType abstract class
│   └── generic/
│       ├── unit.py      # AutoModel
│       ├── list.py      # AutoList
│       └── set.py       # AutoSet
```

## Quick Links

- [BaseAutoType](base.md) - Abstract base class for all knowledge patterns
- [AutoModel](unit.md) - Single-object extraction pattern
- [AutoList](list.md) - Multi-item list extraction pattern
- [AutoSet](set.md) - Unique collection with deduplication

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
from hyperextract.core import AutoModel
from pydantic import BaseModel

class MySchema(BaseModel):
    field: str

# Type-safe: knowledge.data is of type MySchema
knowledge: AutoModel[MySchema] = AutoModel(
    data_schema=MySchema,
    llm_client=llm,
    embedder=embedder
)
```

## Next: Detailed API Docs

- [BaseAutoType API](base.md)
- [AutoModel API](unit.md)  
- [AutoList API](list.md)
- [AutoSet API](set.md)
