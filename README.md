# Hyper-Extract: From Text to Actionable Knowledge Structures 🚀

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

**Hyper-Extract** is a next-generation knowledge extraction framework designed to transform unstructured text into **searchable, queryable, and actionable** structured knowledge.

Unlike traditional extraction tools that only output static data, Hyper-Extract automatically converts extracted structures (Lists, Graphs, Hypergraphs) into an interactive knowledge base. You can directly chat with the structure, perform precise semantic searches, and realize "Extraction as an Application."

[中文版自述文件 (README_ZH.md)](README_ZH.md)

---

## 🌟 Key Highlights

- **📂 Universal Structure Support**:
  - **Foundational**: List, Set, General Knowledge Graph.
  - **Dynamics**: Temporal Graph (time-series events), Spatial Graph (geographical topology), Spatio-Temporal Graph.
  - **Complex Relations**: Hypergraph (N-ary relations), perfect for modeling group interactions and holistic context.
- **💬 Actionable Knowledge (RAG 2.0)**:
  - Extraction is just the beginning. Hyper-Extract automatically builds vector indices for every extracted entity and relationship.
  - **Chat with Structure**: Query your graph or list directly to get answers backed by structured logic.
- **🛠️ Production-Ready SOTA Algorithms**:
  - Built-in implementations of cutting-edge extraction and RAG paradigms: `Auto-Gen`, `Hyper-RAG`, `Light-RAG`, `GraphRAG`, `CogRAG`, and more.
- **🎭 Massive Domain Templates**:
  - 20+ out-of-the-box templates covering: Finance, Medicine, Law, Gaming, Agriculture, Cybersecurity, Physics, Literature, etc.

---

## 🚀 Quick Start

### Installation

```bash
pip install hyperextract
```

### Build an "Intelligent Knowledge Graph" in 3 Steps

Hyper-Extract makes complex extraction and interaction dead simple:

```python
from pydantic import BaseModel, Field
from hyperextract.types import AutoGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 1. Define your world view (Schema)
class entity(BaseModel):
    name: str = Field(description="Name of the entity")
    type: str = Field(description="Category, e.g., Person, Company, Location")

class edge(BaseModel):
    source: str = Field(description="Source entity name")
    target: str = Field(description="Target entity name")
    relation: str = Field(description="The relationship between them")

# 2. Initialize and Build from Text
llm = ChatOpenAI(model="gpt-4o")
embedder = OpenAIEmbeddings()

graph_kb = AutoGraph(
    node_schema=entity,
    edge_schema=edge,
    # Unique key extractors for deduplication and linking
    node_key_extractor=lambda x: x.name,
    edge_key_extractor=lambda x: f"{x.source}_{x.relation}_{x.target}",
    nodes_in_edge_extractor=lambda x: (x.source, x.target),
    llm_client=llm, 
    embedder=embedder
)

text = "Apple Inc. was founded by Steve Jobs in California, and it is the maker of the iPhone."
graph_kb.feed_text(text) # Extract knowledge
graph_kb.build_index() # Build vector index for Q&A

# 3. Chat with the Structure (Actionable!)
answer = graph_kb.chat("What is the relationship between Jobs and Apple?")
print(answer.content)
```

---

## 🎨 Domain Templates

The `hyperextract/templates` directory provides a wealth of domain-specific definitions that you can import directly without writing prompts from scratch:

| Category | Templates | Description |
| :--- | :--- | :--- |
| **General** | `General`, `IText2KG` | Versatile extraction for most daily knowledge. |
| **Science** | `Physics`, `Chemistry`, `Biology` | Capture experiments, elements, and reactions. |
| **Industry** | `Finance`, `Legal`, `Cybersecurity` | Extract compliance, risks, and entity webs. |
| **Entertainment** | `Game`, `Movie`, `Music` | Perfect for story plots and character networks. |
| ... | | 20+ more domains in the [templates folder](hyperextract/templates) |

---

## 🏗️ Core Components

- **`hyperextract.types`**: Core AutoTypes data structures (AutoModel, AutoGraph, AutoHypergraph, etc.).
- **`hyperextract.methods`**: Extraction algorithms and RAG strategies (Hyper-RAG, Cog-RAG, iText2KG, etc.).
- **`hyperextract.utils`**: Essential utilities for logging and merging strategies.

---

## 📚 Implemented Algorithms & Paper Demos

- **Auto-Graph**: Schema-adaptive graph extraction.
- **Hyper-RAG**: Retrieval Augmented Generation via Hypergraphs.
- **Light-RAG**: Lightweight and efficient graph retrieval.
- **IText2KG / IText2KG-Star**: Iterative Knowledge Graph generation.
- **CogRAG**: Cognition-driven hierarchical retrieval.

---

## 🤝 Contributing

We welcome Issues and Pull Requests!

- **License**: [MIT LICENSE](LICENSE)
- **Support**: If you find this project helpful, please give us a ⭐️!
