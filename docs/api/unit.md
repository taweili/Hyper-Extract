# UnitKnowledge API

::: hyperextract.knowledge.generic.unit.UnitKnowledge
    options:
      show_root_heading: true
      show_source: true
      heading_level: 2

## Overview

`UnitKnowledge` implements the single-object extraction pattern. It's designed to extract exactly one structured object per document, making it ideal for document-level information like summaries, metadata, or aggregate statistics.

## Class Signature

```python
class UnitKnowledge(BaseKnowledge[T]):
    """Unit Knowledge Pattern - extracts a single structured object from text."""
```

## Key Characteristics

- **Extraction Target**: One unique structured object per document
- **Merge Strategy**: Field-level merge - first extraction wins, subsequent fills missing fields
- **Indexing Strategy**: Each non-null field indexed independently
- **Processing**: Uses LangChain batch processing for efficient multi-chunk handling

## Initialization

Inherits all parameters from `BaseKnowledge` with same defaults.

```python
from hyperextract.knowledge.generic import UnitKnowledge
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

class DocumentMetadata(BaseModel):
    title: str = Field(default="", description="Document title")
    author: str = Field(default="", description="Author name")
    summary: str = Field(default="", description="Brief summary")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

knowledge = UnitKnowledge(
    data_schema=DocumentMetadata,
    llm_client=llm,
    embedder=embedder,
    chunk_size=2000,
    chunk_overlap=200
)
```

## Properties

### `data`
```python
@property
def data(self) -> T
```

Returns the single extracted object.

**Example**:
```python
knowledge.extract(text)
metadata = knowledge.data
print(f"Title: {metadata.title}")
print(f"Author: {metadata.author}")
```

## Methods

### `extract()`

Extracts a single object from text. For long texts:
1. Splits into overlapping chunks
2. Extracts object from each chunk in parallel
3. Merges using first-priority strategy

**Merge Behavior**:
- First extraction: Populates all fields
- Subsequent extractions: Only fill `None` or empty fields

```python
text = """
Long document spanning multiple chunks...
Title mentioned in chunk 1...
Author mentioned in chunk 2...
Summary in chunk 3...
"""

knowledge.extract(text)
# Result: Single object with title, author, and summary
```

### `build_index()`

Builds index from all non-null fields:

```python
knowledge.build_index()
# Creates one document per field:
# - Document(page_content=title, metadata={"field": "title"})
# - Document(page_content=author, metadata={"field": "author"})
# - Document(page_content=summary, metadata={"field": "summary"})
```

### `search()`

Searches across all indexed fields:

```python
results = knowledge.search("research methodology", k=5)
for doc, score in results:
    field_name = doc.metadata["field"]
    content = doc.page_content
    print(f"Field '{field_name}' matched with score {score:.3f}")
    print(f"Content: {content}")
```

## Merge Strategy Details

The `_merge_strategy` method implements field-level merging:

```python
def _merge_strategy(self, old_data: T, new_data: T) -> T:
    """Merge strategy: Keep old values, fill only None/empty fields from new."""
```

**Example**:
```python
# Chunk 1 extracts
old_data = DocumentMetadata(
    title="AI Research",
    author="",
    summary=""
)

# Chunk 2 extracts
new_data = DocumentMetadata(
    title="Different Title",  # Ignored - old has value
    author="John Smith",      # Kept - old was empty
    summary="A study..."      # Kept - old was empty
)

# Merged result
merged = DocumentMetadata(
    title="AI Research",      # From old
    author="John Smith",      # From new
    summary="A study..."      # From new
)
```

## Indexing Strategy

Each field becomes a separate document:

```python
def _build_documents_for_indexing(self) -> List[Document]:
    """Build documents from non-null fields."""
    documents = []
    for field_name, value in self._data.model_dump().items():
        if value and value != [] and value != "":
            doc = Document(
                page_content=str(value),
                metadata={"field": field_name}
            )
            documents.append(doc)
    return documents
```

## Use Cases

### Document Summary
```python
class Summary(BaseModel):
    main_topic: str = Field(default="", description="Main topic")
    key_points: List[str] = Field(default_factory=list, description="Key points")
    conclusion: str = Field(default="", description="Conclusion")

summary_knowledge = UnitKnowledge(
    data_schema=Summary,
    llm_client=llm,
    embedder=embedder
)
```

### Article Metadata
```python
class Article(BaseModel):
    title: str = Field(default="", description="Article title")
    publication_date: str = Field(default="", description="Publication date")
    author: str = Field(default="", description="Author")
    category: str = Field(default="", description="Category")

article_knowledge = UnitKnowledge(
    data_schema=Article,
    llm_client=llm,
    embedder=embedder
)
```

### Sentiment Analysis
```python
class Sentiment(BaseModel):
    overall_sentiment: str = Field(default="", description="Overall sentiment")
    positive_aspects: List[str] = Field(default_factory=list)
    negative_aspects: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, description="Confidence score")

sentiment_knowledge = UnitKnowledge(
    data_schema=Sentiment,
    llm_client=llm,
    embedder=embedder
)
```

## Best Practices

1. **Clear Field Descriptions**: LLM uses descriptions during extraction
   ```python
   title: str = Field(default="", description="Full article title including subtitle")
   ```

2. **Appropriate Defaults**: Use empty strings for text, empty lists for sequences
   ```python
   name: str = Field(default="")  # Not None
   tags: List[str] = Field(default_factory=list)  # Not None
   ```

3. **Chunk Sizing**: Adjust based on where information appears
   ```python
   # For metadata (usually at start)
   UnitKnowledge(..., chunk_size=1000, chunk_overlap=100)
   
   # For summary (may span document)
   UnitKnowledge(..., chunk_size=3000, chunk_overlap=300)
   ```

4. **Custom Prompts**: Provide domain-specific guidance
   ```python
   custom_prompt = '''
   Extract academic paper metadata. Pay special attention to:
   - Author affiliations
   - Publication venue
   - Citation count if mentioned
   '''
   
   knowledge = UnitKnowledge(
       data_schema=PaperMetadata,
       llm_client=llm,
       embedder=embedder,
       prompt=custom_prompt
   )
   ```

## Serialization

```python
# Save
knowledge.dump("./document_metadata")

# Load
loaded = UnitKnowledge.load(
    "./document_metadata",
    data_schema=DocumentMetadata,
    llm_client=llm,
    embedder=embedder
)

assert loaded.data.title == knowledge.data.title
```

## See Also

- [BaseKnowledge API](base.md) - Base class documentation
- [ListKnowledge API](list.md) - For extracting multiple items
- [SetKnowledge API](set.md) - For unique collections
- [Knowledge Patterns Guide](../user-guide/knowledge-patterns.md) - Pattern selection guide
