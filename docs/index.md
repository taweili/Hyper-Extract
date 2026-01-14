# Hyper-Extract 🧠✨

> **An Intelligent, LLM-Powered Knowledge Extraction & Evolution Framework**
>
> Transform unstructured text into structured, evolving knowledge containers with the power of Large Language Models.

---

## 🎯 Vision

**Hyper-Extract** reimagines knowledge extraction as an intelligent, self-evolving process. Rather than treating data structures as passive containers, we empower them with **LLM-driven intelligence** to actively extract, merge, evolve, and index knowledge from unstructured text.

Every knowledge container in Hyper-Extract follows a unified lifecycle:

1. **Extract** - Intelligent extraction from text with automatic chunking and merging
2. **Evolve** - Self-refinement through reasoning, pruning, and optimization
3. **Index** - Semantic vector search capabilities
4. **Serialize** - Persist and reload knowledge with full fidelity

---

## ✨ Key Features

### 🤖 LLM-Native Design
- **Deep LangChain Integration**: Every container is initialized with LLM and embedder instances
- **Structured Output**: Leverage `with_structured_output` for type-safe Pydantic schema extraction
- **Intelligent Merging**: First-priority merge strategy for chunk-based extraction

### 🏗️ Unified Architecture
- **Abstract Base Class**: `BaseKnowledge[T]` provides consistent interface across all knowledge types
- **Generic Type Support**: Full Python typing with `Generic[T]` for schema flexibility
- **Lifecycle Management**: Standardized `extract` → `merge` → `evolve` → `search` → `dump/load` pipeline

### 🔍 Semantic Search
- **FAISS Integration**: Fast vector similarity search for knowledge retrieval
- **Automatic Indexing**: Build and maintain indices with lazy loading and dirty tracking
- **Field-Level Search**: Search across all schema fields with metadata preservation

### 📦 Knowledge Patterns

#### ✅ Implemented
- **UnitKnowledge**: Single-object extraction for document-level information (summaries, metadata)
- **ListKnowledge**: Collection-based extraction for entities, events, and structured lists
- **SetKnowledge**: Unique collection with automatic deduplication and intelligent merge strategies

#### 🚧 In Development
- **EntityKnowledge**: Entity-centric extraction with attribute management
- **RelationKnowledge**: Relationship extraction with entity linking
- **GraphKnowledge**: Knowledge graph construction (nodes + edges)
- **HypergraphKnowledge**: Hypergraph representation for complex multi-entity relations

---

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- OpenAI API key (or compatible LLM provider)

### Install with uv (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-username/hyper-extract.git
cd hyper-extract

# Install dependencies with uv
uv sync
```

### Install with pip
```bash
pip install -e .
```

---

## 🚀 Quick Start

### 1. Define Your Knowledge Schema

```python
from pydantic import BaseModel, Field
from typing import List

class ArticleKnowledge(BaseModel):
    """Schema for article knowledge extraction"""
    title: str = Field(default="", description="Article title")
    author: str = Field(default="", description="Author name")
    summary: str = Field(default="", description="Article summary")
    key_points: List[str] = Field(default_factory=list, description="Key points")
    topics: List[str] = Field(default_factory=list, description="Topic tags")
```

### 2. Initialize Knowledge Container

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperextract.knowledge.generic import UnitKnowledge

# Initialize LLM and embedder
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

# Create knowledge container
knowledge = UnitKnowledge(
    data_schema=ArticleKnowledge,
    llm_client=llm,
    embedder=embedder
)
```

### 3. Extract Knowledge

```python
# Extract from text
text = """
'Introduction to Deep Learning' is a comprehensive textbook 
written by Professor Li Ming...
"""

knowledge.extract(text)
print(knowledge.data)  # Access extracted structured knowledge
```

### 4. Semantic Search

```python
# Build index
knowledge.build_index()

# Search for relevant content
results = knowledge.search("applications of deep learning", k=3)
for doc, score in results:
    print(f"Score: {score}, Content: {doc.page_content}")
```

### 5. Persistence

```python
# Save to disk
knowledge.dump("./my_knowledge")

# Load
loaded_knowledge = UnitKnowledge.load(
    "./my_knowledge",
    data_schema=ArticleKnowledge,
    llm_client=llm,
    embedder=embedder
)
```

---

## 📚 Documentation

- **[Getting Started](user-guide/getting-started.md)** - Detailed tutorial and setup guide
- **[Knowledge Patterns](user-guide/knowledge-patterns.md)** - Understanding different extraction patterns
- **[API Reference](api/base.md)** - Complete API documentation

---

## 🤝 Contributing

Contributions are welcome! Please see our contributing guidelines for details.

---

## 📄 License

This project is licensed under the MIT License.
