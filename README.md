# Hyper-Extract 🖥️

[中文版](./README_ZH.md) · [English Version](#)

---

## The CLI-First Knowledge Extraction Engine

> Transform any document into **searchable, queryable, reasoning-enabled** structured knowledge — with just one command.

**8 Knowledge Types** · **5 Extraction Methods** · **200+ Domain Templates** · **Bilingual**


<!-- Architecture Diagram -->
![Architecture](docs/assets/fw.png)

---

## ⚡ One-Line Knowledge Extraction

```bash
# Install
uv pip install hyperextract

# Extract → Build → Query (one line at a time)
he parse report.md -o kb -t graph -l zh    # Extract knowledge
he talk kb -i                                # Interactive Q&A
he search kb "revenue growth reasons"        # Semantic search
he show kb                                   # Visualize
```

### 💻 CLI Commands

| Command | Description |
|---------|-------------|
| `he parse` | Extract knowledge from text/file |
| `he talk` | Interactive Q&A with knowledge base |
| `he search` | Semantic search |
| `he show` | Visualize knowledge graph |
| `he list` | List available templates/methods |
| `he config` | Configure LLM/Embedder |
| `he info` | Show knowledge base info |
| `he feed` | Append knowledge to existing KB |
| `he build-index` | Build vector index |

---

## "Chat solved. What's next is CLI + Knowledge Structures."

Transform LLM output from scattered text into **searchable, queryable, and reasoning-enabled** structured knowledge.

---

## ❌ Before | ✅ After

<!-- Concept Diagram -->
![Concept](./docs/assets/concept.png)

| Before | After |
| :--- | :--- |
| LLM outputs a wall of text | Structured knowledge (8 types) |
| ❌ Need Python to use | ✅ CLI-first (`he` command) |
| ❌ Only simple graph | ✅ Graph/Temporal/Spatial/Hypergraph... |
| ❌ Answer disappears | ✅ Persistent storage |
| ❌ Can't search precisely | ✅ Semantic search |
| ❌ Can't trace source | ✅ Traceable provenance |
| ❌ One language only | ✅ Bilingual (zh/en) |
| ❌ Fragmented, can't reuse | ✅ Knowledge accumulates |

---

## 🧩 8 Knowledge Structures (Not Just Simple Graphs)

> Unlike other tools that only support basic graphs, Hyper-Extract handles **complex, multi-dimensional knowledge structures**.

<!-- AutoTypes Diagram -->
![AutoTypes](./docs/assets/autotypes.png)

| Type | Icon | What it does |
| :--- | :---: | :--- |
| **AutoModel** | 📋 | Extract into a complete data model |
| **AutoList** | 📝 | Extract as a list (keywords, items) |
| **AutoSet** | 📦 | Extract and deduplicate (entity registry) |
| **AutoGraph** | 🔗 | Extract as a knowledge graph (relations) |
| **AutoTemporalGraph** | ⏱️ | Extract as timeline (events over time) |
| **AutoSpatialGraph** | 📍 | Extract as spatial graph (locations) |
| **AutoSpatioTemporalGraph** | 🌏 | Extract as spatiotemporal graph (time + space) |
| **AutoHypergraph** | 🌐 | Extract as hypergraph (multi-party relations) |

---

## 🔬 Extraction Methods Comparison

> Hyper-Extract implements **multiple** extraction methods, not just one.

| Method | Type | Graph | Temporal | Spatial | Spatiotemporal | Hypergraph |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **KG-Gen** | Graph | ✅ | ❌ | ❌ | ❌ | ❌ |
| **ATOM** | Atomic | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Graphiti** | Temporal | ❌ | ✅ | ❌ | ❌ | ❌ |
| **LightRAG** | Graph | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Hyper-RAG** | Hypergraph | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Hyper-Extract** | **All-in-One** | ✅ | ✅ | ✅ | ✅ | ✅ |

**Choose the method that fits your need, or let AutoTypes auto-select.**

---

## 🌍 12 Domains, 200+ Ready-to-Use Templates

> Pre-built templates for **different industries** — extract knowledge **right away** without designing schemas.

| Domain | Templates | Domain | Templates |
| :--- | :---: | :--- | :---: |
| 💰 Finance | 25+ | 📜 History | 12+ |
| 🏥 Medicine | 20+ | 🧬 Biology | 10+ |
| ⚖️ Legal | 15+ | 🎭 Literature | 10+ |
| 🌿 TCM | 15+ | 📰 News | 12+ |
| 🔧 Industry | 18+ | 🌾 Agriculture | 8+ |
| 🍜 Food | 8+ | 🌐 General | 20+ |

**✅ Bilingual** — Templates available in both English and Chinese

---

## 🚀 Quick Start

### Option 1: CLI (Recommended) ⚡

```bash
# Extract knowledge from document
he parse document.pdf -o my_kb -t knowledge_graph -l zh

# Chat with your knowledge
he talk my_kb -i

# Search semantically
he search my_kb "公司营收增长原因"

# Visualize knowledge graph
he show my_kb
```

### Option 2: Python API

```python
from hyperextract.utils.template_engine import Gallery, TemplateFactory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini")
embedder = OpenAIEmbeddings()

config = Gallery.get("ResearchNoteSummary")
template = TemplateFactory.create(config, llm, embedder)
result = template.parse("Apple Q3 revenue reached $94.9 billion...")

answer = template.chat("What drove the revenue growth?")
print(answer.content)
```

---

## 🔧 Architecture

<details>
<summary><strong>Technical Details</strong></summary>

```
hyperextract/
├── cli/                      # 💻 CLI Interface (he command)
│   ├── commands/            # parse, talk, search, show...
│   └── __main__.py          # Entry point
│
├── types/                    # 🧩 8 Knowledge Structures
│   ├── model.py             # AutoModel
│   ├── list.py              # AutoList
│   ├── set.py               # AutoSet
│   ├── graph.py             # AutoGraph
│   ├── hypergraph.py        # AutoHypergraph
│   ├── temporal_graph.py    # AutoTemporalGraph
│   ├── spatial_graph.py     # AutoSpatialGraph
│   └── spatio_temporal_graph.py  # AutoSpatioTemporalGraph
│
├── methods/                  # 🔬 Extraction Engines
│   ├── rag/                 # LightRAG, HyperRAG, CogRAG
│   └── typical/             # KG-Gen, ATOM (reproduced)
│
└── templates/                # 🌍 200+ Domain Templates
    ├── zh/                  # Chinese templates (25+ domains)
    └── en/                  # English templates
```

</details>

---

## 📚 Documentation & Resources

- [📖 Full Documentation](docs/)
- [💻 Examples](examples/)
- [🏷️ Template Gallery](hyperextract/templates/)

---

## 🤝 Contributing

Welcome! Please feel free to submit issues and pull requests.

---

## ⭐ Support

If you find this project helpful, please give us a ⭐ to show your support!

---

*Built with ❤️ for the AI Community*
