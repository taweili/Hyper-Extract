# 🔍 Hyper-Extract

> **"Stop reading. Start understanding."**
>
> *"告别文档焦虑，让信息一目了然"*

Transform unstructured documents into **searchable, visual, structured knowledge** — with just one command.

[📖 English Version](#) · [中文版](./README_ZH.md)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| ⚡ **CLI-First** | One command to extract knowledge from any document |
| 🎯 **8 Structures** | Knowledge Graph, Timeline, Spatial, Hypergraph... |
| 👁️ **Visual** | Interactive visualization with OntoSight |
| 🔍 **Searchable** | Semantic search across all your knowledge |
| 🌐 **Bilingual** | Full support for English and Chinese |
| 📦 **200+ Templates** | Ready-to-use domain-specific templates |

---

## ❌ Before | ✅ After

| Before | After |
|--------|-------|
| Walls of text | **Clear visual structure** |
| ❌ Hours of reading | ✅ **Instant clarity** |
| ❌ Hard to find key info | ✅ **Semantic search** |
| ❌ Can't compare docs | ✅ **Structured comparison** |
| ❌ Scattered insights | ✅ **Knowledge accumulation** |

![Before/After Demo](docs/assets/before-after-demo.jpeg)

---

## ⚡ Quick Start

### Installation

```bash
pip install hyper-extract
```

### Usage

```bash
# Extract structure from document
he parse document.pdf -o kb

# Visualize the knowledge
he show kb

# Semantic search
he search kb "key insights"

# Interactive Q&A
he talk kb -i
```

![CLI Welcome Screen](docs/assets/cli.png)

---

## 🧩 8 Knowledge Structures

**8 different structures** for different needs:

| Type | Icon | Best For | Example |
|------|------|----------|---------|
| **AutoModel** | 📋 | Structured reports | Financial statements |
| **AutoList** | 📝 | Key points | Meeting notes |
| **AutoSet** | 📦 | Entity registry | Product catalog |
| **AutoGraph** | 🔗 | Relations | Social networks |
| **AutoTemporalGraph** | ⏱️ | Event sequences | News timeline |
| **AutoSpatialGraph** | 📍 | Locations | Delivery routes |
| **AutoSpatioTemporalGraph** | 🌏 | Time + Space | Historical events |
| **AutoHypergraph** | 🌐 | Complex relations | Legal cases |

![AutoTypes Demo](docs/assets/autotypes-demo.jpeg)

---

## 🎯 Use Cases

| Domain | What You Get | Example |
|--------|--------------|---------|
| 📊 **Finance** | Extract insights from earnings reports | `he parse report.pdf -o kb -l en` |
| ⚖️ **Legal** | Structure contracts, case laws | `he parse contract.pdf -o kb -t hypergraph` |
| 🏥 **Medical** | Organize patient histories | `he parse records.pdf -o kb` |
| 📚 **Research** | Extract key findings from papers | `he parse paper.pdf -o kb` |
| 📋 **Meetings** | Transform notes into timelines | `he parse notes.md -o kb` |

![Use Cases Demo](docs/assets/use-cases-demo.jpeg)

---

## 🔧 Architecture

<details>
<summary><strong>Technical Details (Click to Expand)</strong></summary>

```
hyper-extract/
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
│   └── spatio_temporal_graph.py
│
├── methods/                  # 🔬 Extraction Engines
│   ├── rag/                 # LightRAG, HyperRAG, CogRAG
│   └── typical/             # KG-Gen, ATOM
│
└── templates/                # 🌍 200+ Domain Templates
    ├── zh/                  # Chinese templates
    └── en/                  # English templates
```

### Supported Methods

| Method | Graph | Temporal | Spatial | Hypergraph |
|--------|-------|----------|---------|------------|
| KG-Gen | ✅ | ❌ | ❌ | ❌ |
| ATOM | ✅ | ✅ | ❌ | ❌ |
| Graphiti | ❌ | ✅ | ❌ | ❌ |
| LightRAG | ✅ | ❌ | ❌ | ❌ |
| Hyper-RAG | ❌ | ❌ | ❌ | ✅ |
| **Hyper-Extract** | ✅ | ✅ | ✅ | ✅ |

</details>

---

## 📚 Documentation & Resources

- [📖 Full Documentation](docs/)
- [💻 Examples](examples/)
- [🏷️ Template Gallery](hyperextract/templates/)

---

## 🤝 Contributing & Support

Welcome! Please feel free to submit issues and pull requests.

If you find this project helpful, please give us a ⭐ to show your support!

---

*Built with ❤️ for the AI Community*
