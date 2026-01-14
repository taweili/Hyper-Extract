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

### 📦 Multiple Knowledge Types (Roadmap)
- ✅ **UnitKnowledge**: Universal schema-agnostic knowledge extraction
- 🚧 **EntityKnowledge**: Entity-centric extraction with attribute management
- 🚧 **RelationKnowledge**: Relationship extraction with entity linking
- 🚧 **GraphKnowledge**: Knowledge graph construction (nodes + edges)
- 🚧 **HypergraphKnowledge**: Hypergraph representation for complex multi-entity relations
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
result = knowledge.extract(article_text)
print(f"Extraction completed: {result}")

# Access extracted data
print(f"Title: {knowledge.data.title}")
print(f"Author: {knowledge.data.author}")
print(f"Key points: {knowledge.data.key_points}")
```

### 4. Semantic Search

```python
# Build vector index
knowledge.build_index()

# Search with natural language
results = knowledge.search("What are the main topics?", top_k=3)
for result in results:
    print(result)
```

### 5. Save and Load

```python
# Save to folder (includes data + FAISS index)
knowledge.dump("./output/my_knowledge")

# Load from folder
knowledge.load("./output/my_knowledge")
```

---

## 🏛️ Architecture

### Design Principles

1. **Template Method Pattern**: `BaseKnowledge` defines the extraction skeleton, subclasses customize behavior
2. **First-Priority Merge**: `model_copy(update=model_dump(exclude_none=True))` for conflict resolution
3. **Lazy Indexing**: Build FAISS indices only when needed, track with `_index_dirty` flag
4. **Type Safety**: Leverage Pydantic for runtime validation and IDE support

---

## 📚 Examples

Check out the `examples/` directory for complete working examples:

- [`generic_knowledge_demo.py`](examples/generic_knowledge_demo.py) - Full UnitKnowledge walkthrough
- More examples coming soon!

---

## 🗺️ Roadmap

### Phase 1: Foundation (Current) ✅
- [x] Abstract `BaseKnowledge` class
- [x] `UnitKnowledge` implementation
- [x] LangChain integration with structured output
- [x] FAISS vector search
- [x] Serialization (dump/load)

### Phase 2: Specialized Knowledge Types 🚧
- [ ] `EntityKnowledge` - Entity extraction with coreference resolution
- [ ] `RelationKnowledge` - Relationship extraction and linking
- [ ] `GraphKnowledge` - Full knowledge graph construction
- [ ] `HypergraphKnowledge` - Hypergraph for complex relations

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
