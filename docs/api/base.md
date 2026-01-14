# BaseKnowledge API

::: hyperextract.knowledge.base.BaseKnowledge
    options:
      show_root_heading: true
      show_source: true
      heading_level: 2

## Overview

`BaseKnowledge` is the abstract base class that provides the foundation for all knowledge extraction patterns in Hyper-Extract. It implements the core lifecycle operations: extraction, merging, indexing, evolution, and serialization.

## Class Signature

```python
class BaseKnowledge(ABC, Generic[T]):
    """Unified knowledge base class integrating extraction, storage, 
    aggregation, and evolution."""
```

Where `T` is a Pydantic `BaseModel` subclass defining your knowledge schema.

## Initialization

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data_schema` | `Type[T]` | Required | Pydantic BaseModel subclass defining knowledge structure |
| `llm_client` | `BaseChatModel` | Required | LangChain LLM client for extraction |
| `embedder` | `Embeddings` | Required | Embedding model for semantic search |
| `prompt` | `str` | `""` | Custom extraction prompt (uses default if empty) |
| `chunk_size` | `int` | `2000` | Maximum characters per text chunk |
| `chunk_overlap` | `int` | `200` | Overlapping characters between chunks |
| `max_workers` | `int` | `10` | Maximum concurrent extraction tasks |
| `show_progress` | `bool` | `True` | Whether to display progress logs |

### Example

```python
from hyperextract.knowledge.base import BaseKnowledge
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

class MySchema(BaseModel):
    title: str = Field(default="", description="Document title")
    summary: str = Field(default="", description="Brief summary")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

# Note: BaseKnowledge is abstract, use concrete implementations
# knowledge = UnitKnowledge(...)
```

## Properties

### `data`
```python
@property
def data(self) -> T
```
Returns the extracted knowledge data. Type is your specified schema `T`.

**Example**:
```python
knowledge.extract(text)
print(knowledge.data.title)
```

### `metadata`
```python
@property
def metadata(self) -> Dict[str, Any]
```
Returns metadata about the knowledge object, including creation and update timestamps.

**Example**:
```python
print(knowledge.metadata["created_at"])
print(knowledge.metadata["updated_at"])
```

## Core Methods

### `extract()`
```python
def extract(
    self,
    text: str,
    *,
    additional_info: str = "",
    merge: bool = True
) -> T
```

Extract structured knowledge from text.

**Parameters**:
- `text` (str): Source text to extract from
- `additional_info` (str): Optional context or instructions
- `merge` (bool): Whether to merge with existing data (default: True)

**Returns**: Extracted data of type `T`

**Example**:
```python
result = knowledge.extract(
    text="Long article text...",
    additional_info="Focus on technical details",
    merge=True
)
```

### `build_index()`
```python
def build_index(self, force_rebuild: bool = False) -> None
```

Build or rebuild the FAISS vector index for semantic search.

**Parameters**:
- `force_rebuild` (bool): Force rebuild even if index exists

**Example**:
```python
knowledge.build_index()  # Build if not exists
knowledge.build_index(force_rebuild=True)  # Force rebuild
```

### `search()`
```python
def search(
    self,
    query: str,
    k: int = 5,
    **kwargs
) -> List[Tuple[Document, float]]
```

Perform semantic search over indexed knowledge.

**Parameters**:
- `query` (str): Search query
- `k` (int): Number of results to return
- `**kwargs`: Additional arguments passed to FAISS

**Returns**: List of (Document, similarity_score) tuples

**Example**:
```python
results = knowledge.search("machine learning applications", k=3)
for doc, score in results:
    print(f"Score: {score:.3f}")
    print(f"Content: {doc.page_content}")
    print(f"Metadata: {doc.metadata}")
```

### `dump()`
```python
def dump(self, save_path: str | Path) -> None
```

Save knowledge to disk, including data, metadata, and index.

**Parameters**:
- `save_path` (str | Path): Directory path to save to

**Structure**:
```
save_path/
├── state.json          # Data and metadata
└── faiss_index/        # Vector index
    └── index.faiss
```

**Example**:
```python
knowledge.dump("./my_knowledge")
```

### `load()` (Class Method)
```python
@classmethod
def load(
    cls,
    load_path: str | Path,
    data_schema: Type[T],
    llm_client: BaseChatModel,
    embedder: Embeddings,
    **kwargs
) -> "BaseKnowledge[T]"
```

Load knowledge from disk.

**Parameters**:
- `load_path` (str | Path): Directory to load from
- `data_schema` (Type[T]): Schema class (must match saved data)
- `llm_client` (BaseChatModel): LLM client for future operations
- `embedder` (Embeddings): Embedder for search
- `**kwargs`: Additional initialization parameters

**Returns**: Loaded knowledge instance

**Example**:
```python
loaded = UnitKnowledge.load(
    "./my_knowledge",
    data_schema=MySchema,
    llm_client=llm,
    embedder=embedder
)
```

## Abstract Methods

Subclasses must implement these methods:

### `_default_prompt()`
```python
@staticmethod
@abstractmethod
def _default_prompt() -> str
```

Returns the default extraction prompt for the pattern.

### `_merge_strategy()`
```python
@abstractmethod
def _merge_strategy(self, old_data: T, new_data: T) -> T
```

Defines how to merge old and new extracted data.

### `_build_documents_for_indexing()`
```python
@abstractmethod
def _build_documents_for_indexing(self) -> List[Document]
```

Converts knowledge data into LangChain Documents for indexing.

## Internal Methods

### `_extract_single_chunk()`
```python
def _extract_single_chunk(
    self,
    chunk_text: str,
    additional_info: str = ""
) -> T
```

Extracts knowledge from a single text chunk. Used internally by `extract()`.

### `_extract_multi_chunk()`
```python
def _extract_multi_chunk(
    self,
    text: str,
    additional_info: str = ""
) -> T
```

Handles multi-chunk extraction with parallel processing and merging.

## Usage in Subclasses

When creating custom knowledge patterns, inherit from `BaseKnowledge`:

```python
from hyperextract.knowledge.base import BaseKnowledge, T
from typing import List
from langchain_core.documents import Document

class CustomKnowledge(BaseKnowledge[T]):
    @staticmethod
    def _default_prompt() -> str:
        return "Extract information according to schema: "
    
    def _merge_strategy(self, old_data: T, new_data: T) -> T:
        # Implement merge logic
        return new_data  # Simple replace
    
    def _build_documents_for_indexing(self) -> List[Document]:
        # Convert self._data to documents
        return [Document(page_content=str(self._data))]
```

## See Also

- [UnitKnowledge API](unit.md) - Single-object extraction
- [ListKnowledge API](list.md) - Multi-item extraction  
- [SetKnowledge API](set.md) - Unique collection extraction
