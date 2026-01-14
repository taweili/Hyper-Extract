# Getting Started

This guide will walk you through the basics of using Hyper-Extract to extract structured knowledge from unstructured text.

## Installation

### Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** installed
- An **OpenAI API key** (or access to a compatible LLM provider)
- Basic understanding of Python and Pydantic

### Setting Up Your Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/hyper-extract.git
   cd hyper-extract
   ```

2. **Install dependencies** (recommended: use `uv`):
   ```bash
   uv sync
   ```

   Or with pip:
   ```bash
   pip install -e .
   ```

3. **Configure your API key**:
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your-api-key-here
   ```

## Core Concepts

### Knowledge Schema

A **knowledge schema** is a Pydantic model that defines the structure of information you want to extract. It should include:

- Field names and types
- Default values
- Descriptive annotations (used by the LLM during extraction)

Example:
```python
from pydantic import BaseModel, Field
from typing import List

class BookReview(BaseModel):
    """Schema for book review extraction"""
    title: str = Field(default="", description="Book title")
    author: str = Field(default="", description="Author name")
    rating: float = Field(default=0.0, description="Rating out of 5")
    pros: List[str] = Field(default_factory=list, description="Positive aspects")
    cons: List[str] = Field(default_factory=list, description="Negative aspects")
    recommendation: str = Field(default="", description="Final recommendation")
```

### Knowledge Container

A **knowledge container** is an instance of a knowledge pattern class (e.g., `UnitKnowledge`, `ListKnowledge`, `SetKnowledge`) that manages extraction, storage, and retrieval of structured knowledge.

### Extraction Pipeline

The extraction pipeline automatically:

1. **Chunks** long texts into manageable pieces
2. **Extracts** structured data from each chunk in parallel
3. **Merges** results according to the pattern's merge strategy
4. **Indexes** the data for semantic search

## Basic Usage Example

### Step 1: Define Your Schema

```python
from pydantic import BaseModel, Field
from typing import List

class ResearchPaper(BaseModel):
    """Research paper metadata extraction"""
    title: str = Field(default="", description="Paper title")
    authors: List[str] = Field(default_factory=list, description="Author names")
    abstract: str = Field(default="", description="Paper abstract")
    keywords: List[str] = Field(default_factory=list, description="Keywords")
    methodology: str = Field(default="", description="Research methodology")
    findings: List[str] = Field(default_factory=list, description="Key findings")
    conclusion: str = Field(default="", description="Main conclusion")
```

### Step 2: Initialize LLM and Embedder

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Initialize models
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0  # Use 0 for consistent extraction
)
embedder = OpenAIEmbeddings(model="text-embedding-3-small")
```

### Step 3: Create Knowledge Container

```python
from hyperextract.knowledge.generic import UnitKnowledge

# Create container
paper_knowledge = UnitKnowledge(
    data_schema=ResearchPaper,
    llm_client=llm,
    embedder=embedder,
    chunk_size=2000,  # Characters per chunk
    chunk_overlap=200  # Overlap between chunks
)
```

### Step 4: Extract Knowledge

```python
# Your source text
paper_text = """
Title: Deep Learning for Natural Language Processing

Authors: John Smith, Jane Doe, Bob Johnson

Abstract: This paper presents a comprehensive study on applying 
deep learning techniques to natural language processing tasks...

[... rest of the paper ...]
"""

# Extract knowledge
paper_knowledge.extract(paper_text)

# Access extracted data
print(paper_knowledge.data.title)
print(paper_knowledge.data.authors)
print(paper_knowledge.data.abstract)
```

### Step 5: Semantic Search

```python
# Build search index
paper_knowledge.build_index()

# Search for specific information
results = paper_knowledge.search(
    "What methodology was used?",
    k=3  # Top 3 results
)

# Display results
for doc, score in results:
    print(f"Relevance: {score:.3f}")
    print(f"Content: {doc.page_content}")
    print(f"Metadata: {doc.metadata}")
    print("---")
```

### Step 6: Save and Load

```python
# Save knowledge to disk
paper_knowledge.dump("./paper_knowledge")

# Later, load it back
loaded_knowledge = UnitKnowledge.load(
    "./paper_knowledge",
    data_schema=ResearchPaper,
    llm_client=llm,
    embedder=embedder
)

# Knowledge is fully restored
print(loaded_knowledge.data)
```

## Working with Long Documents

Hyper-Extract automatically handles long documents by:

1. **Splitting** text into overlapping chunks
2. **Processing** chunks in parallel for efficiency
3. **Merging** extracted information intelligently

You can control chunking behavior:

```python
knowledge = UnitKnowledge(
    data_schema=YourSchema,
    llm_client=llm,
    embedder=embedder,
    chunk_size=3000,      # Larger chunks for more context
    chunk_overlap=300,    # More overlap to avoid missing information
    max_workers=5         # Control parallelism
)
```

## Error Handling

Always wrap extraction in try-except blocks:

```python
try:
    knowledge.extract(text)
except Exception as e:
    print(f"Extraction failed: {e}")
    # Handle error appropriately
```

## Next Steps

- Learn about different [Knowledge Patterns](knowledge-patterns.md)
- Explore the [API Reference](../api/base.md)
- Check out the [examples](https://github.com/your-username/hyper-extract/tree/main/examples) folder

## Tips for Better Extraction

1. **Clear Descriptions**: Write detailed field descriptions in your schema - the LLM uses these
2. **Appropriate Defaults**: Set sensible default values for optional fields
3. **Type Hints**: Use proper Python type hints for better extraction accuracy
4. **Chunk Size**: Adjust based on your document structure (2000-4000 chars works well)
5. **Temperature**: Use 0 for consistent extraction, higher for creative tasks
