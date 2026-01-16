# Hyper-Extract 🧠✨

> **An Intelligent, LLM-Powered Knowledge Extraction Framework**
>
> Transform unstructured text into structured Auto containers with the power of Large Language Models.

---

## 🎯 Vision

**Hyper-Extract** provides a powerful framework for intelligent knowledge extraction. Rather than treating data structures as passive containers, we empower them with **LLM-driven intelligence** to actively extract, merge, and index knowledge from unstructured text.

Every Auto container in Hyper-Extract follows a unified lifecycle:

1. **Extract** - Intelligent extraction from text with automatic chunking and merging
2. **Merge** - Automatic aggregation with configurable merge strategies
3. **Index** - Semantic vector search capabilities
4. **Serialize** - Persist and reload knowledge with full fidelity

---

## ✨ Key Features

### 🤖 LLM-Native Design
- **Deep LangChain Integration**: Every container is initialized with LLM and embedder instances
- **Structured Output**: Leverage `with_structured_output` for type-safe Pydantic schema extraction
- **Intelligent Merging**: First-priority merge strategy for chunk-based extraction

### 🏗️ Unified Architecture
- **Abstract Base Class**: `BaseAutoType[T]` provides consistent interface across all knowledge types
- **Generic Type Support**: Full Python typing with `Generic[T]` for schema flexibility
- **Lifecycle Management**: Standardized `extract` → `merge` → `search` → `dump/load` pipeline

### 🔍 Semantic Search
- **FAISS Integration**: Fast vector similarity search for knowledge retrieval
- **Automatic Indexing**: Build and maintain indices with lazy loading and dirty tracking
- **Field-Level Search**: Search across all schema fields with metadata preservation

### 📦 Multiple Knowledge Types (Roadmap)
- ✅ **AutoModel**: Universal schema-agnostic knowledge extraction
- ✅ **AutoList**: Collection-based extraction for lists of items
- ✅ **AutoSet**: Unique collection with automatic deduplication
- 🚧 **AutoGraph**: Knowledge graph construction (nodes + edges)
- 🚧 **AutoHypergraph**: Hypergraph representation for complex multi-entity relations
- 🚧 **ExtractionExperience**: Meta-learning from extraction patterns

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
pip install -r requirements.txt
```

---

## 🚀 Quick Start

### 1. Define Your Knowledge Schema

```python
from pydantic import BaseModel, Field
from typing import List

class ArticleSchema(BaseModel):
    """Schema for article knowledge extraction"""
    title: str = Field(default="", description="Article title")
    author: str = Field(default="", description="Author name")
    summary: str = Field(default="", description="Article summary")
    key_points: List[str] = Field(default_factory=list, description="Key points")
    topics: List[str] = Field(default_factory=list, description="Topic tags")
```

### 2. Initialize Auto Container

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperextract import AutoModel

# Initialize LLM and embedder
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

# Create Auto container
a_article = AutoModel(
    data_schema=ArticleSchema,
    llm_client=llm,
    embedder=embedder,
    chunk_size=2000,  # Auto-split long texts
    max_workers=5,    # Concurrent processing
    show_progress=True
)
```

### 3. Extract Knowledge from Text

```python
article_text = """
Title: The Future of AI
Author: Dr. Jane Smith

Artificial intelligence is transforming industries...
[Your long article text here]
"""

# Extract with automatic chunking and merging
result = a_article.extract(article_text)
print(f"Extraction completed: {result}")

# Access extracted data
print(f"Title: {a_article.data.title}")
print(f"Author: {a_article.data.author}")
print(f"Key points: {a_article.data.key_points}")
```

### 4. Semantic Search

```python
# Build vector index
a_article.build_index()

# Search with natural language
results = a_article.search("What are the main topics?", top_k=3)
for result in results:
    print(result)
```

### 5. Save and Load

```python
# Save to folder (includes data + FAISS index)
a_article.dump("./output/my_article")

# Load from folder
a_article.load("./output/my_article")
```

---

## 🏛️ Architecture

### Design Principles

1. **Template Method Pattern**: `BaseAutoType` defines the extraction skeleton, subclasses customize behavior
2. **First-Priority Merge**: `model_copy(update=model_dump(exclude_none=True))` for conflict resolution
3. **Lazy Indexing**: Build FAISS indices only when needed, track with `_index_dirty` flag
4. **Type Safety**: Leverage Pydantic for runtime validation and IDE support

---

## 📚 Examples

Check out the `examples/` directory for complete working examples:

- [`auto_model_demo.py`](examples/auto_model_demo.py) - Full AutoModel walkthrough
- More examples coming soon!

---

## 🗺️ Roadmap

### Phase 1: Foundation (Current) ✅
- [x] Abstract `BaseAutoType` class
- [x] `AutoModel` implementation
- [x] LangChain integration with structured output
- [x] FAISS vector search
- [x] Serialization (dump/load)

### Phase 2: Specialized Knowledge Types 🚧
- [ ] `AutoGraph` - Full knowledge graph construction
- [ ] `AutoHypergraph` - Hypergraph for complex relations
- [ ] `AutoTree` - Hierarchical tree structures

### Phase 3: Evolution & Learning 🔮
- [ ] `evolve()` implementation with reasoning
- [ ] Extraction experience learning
- [ ] Confidence scoring and quality metrics
- [ ] Active learning for schema refinement

### Phase 4: Advanced Features 🚀
- [ ] Multi-modal extraction (images, tables, PDFs)
- [ ] Incremental updates and versioning
- [ ] Distributed processing for massive datasets
- [ ] Integration with graph databases (Neo4j, NetworkX)

---

## 🤝 Contributing

We welcome contributions! Whether it's:

- 🐛 Bug reports and fixes
- 💡 Feature suggestions
- 📖 Documentation improvements
- 🧪 New knowledge type implementations

Please open an issue or submit a PR. Check out our [contributing guidelines](CONTRIBUTING.md) (coming soon).

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain) for LLM orchestration
- Powered by [Pydantic](https://github.com/pydantic/pydantic) for data validation
- Vector search by [FAISS](https://github.com/facebookresearch/faiss)
- Inspired by the vision of self-evolving knowledge systems

---

## 📬 Contact

- **GitHub Issues**: [Create an issue](https://github.com/yifanfeng97/hyper-extract/issues)
- **Email**: evanfeng97@gmail.com

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

*Building the future of intelligent knowledge extraction, one container at a time.*

</div>
