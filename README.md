# 🔍 Hyper-Extract

> **"Stop reading. Start understanding."**

> *"告别文档焦虑，让信息一目了然"*

Transform documents into **knowledge abstracts** — with just one command.

<p align="center">
  <img alt="Python Version" src="https://img.shields.io/badge/python-3.9%2B-blue">
  <img alt="License" src="https://img.shields.io/badge/license-Apache%202.0-blue">
  <img alt="Status" src="https://img.shields.io/badge/status-active-success">
</p>

[📖 English Version](./README.md) · [中文版](./README_ZH.md)

---

## 🚀 What is Hyper-Extract?

Hyper-Extract is an intelligent, LLM-powered knowledge extraction and evolution framework. It radically simplifies transforming highly unstructured texts into persistent, predictable, and strongly-typed knowledge summaries. It effortlessly extracts information into a wide spectrum of formats—ranging from simple **Collections** (Lists/Sets) and **Pydantic Models**, to complex **Knowledge Graphs**, **Hypergraphs**, and even **Spatio-Temporal Graphs**.

![Hero & Workflow](docs/assets/hero-v2.jpg)

*A seamless pipeline from messy documents to neat structured nodes.*

---

## ✨ Core Features

- 🔷 **8 Auto-Types:** From basic `AutoModel`/`AutoList` to advanced `AutoGraph`, `AutoHypergraph`, and `AutoSpatioTemporalGraph`.
- 🧠 **10+ Extraction Engines:** Out-of-the-box support for cutting-edge retrieval paradigms like `graph_rag`, `light_rag`, and `cog_rag`.
- 📝 **Declarative YAML Templates:** Zero-code extraction definition. Includes 80+ presets across 6 domains.
- 🔄 **Incremental Evolution:** Feed new documents on the fly to continuously map out and expand the extracted knowledge.

---

## ⚡ Quick Start

### 1. Installation

```bash
uv pip install hyper-extract
```

### 2. The Command Line Way

Extract, search, and manage directly from CLI.
*(Note: By default, the CLI relies on `gpt-4o-mini` as the foundation model and `text-embedding-3-small` for embeddings to balance performance and speed.)*

```bash
he config init -k YOUR_API_KEY
he parse document.md -o ./output/ -l zh
he search ./output/ "What are the key events?"
he feed ./output/ new_document.md
```

### 3. The Python API Way

```python
from hyperextract import Template

# Load a preset YAML template
ka = Template.create("finance/event_timeline")

# Extract and auto-parse the document
result = ka.parse(annual_report_text)
# result.timeline yields beautifully parsed list of Event objects!
```

> 🔗 For detailed CLI usage, see [CLI Guide](./hyperextract/cli/README.md)

---

## 🧩 Deep Dive: The 8 Auto-Types

Our framework embraces complexity without making you write boilerplate code. 
4
![Knowledge Structures Matrix](docs/assets/8-types-v2.jpg)

| Auto-Type | Best For | Real-World Example |
|-----------|----------|--------------------|
| **Model** | Structured reports | Financial summaries |
| **List** | Ordered items | Meeting actions |
| **Set** | Deduplicated queries | Product catalogs |
| **Graph** | Binary relationships | Social networks |
| **Hypergraph** | Multi-party events | Contract disputes |
| **TemporalGraph** | Time sequencing | News timelines |
| **SpatialGraph** | Geolocation | Delivery routes |
| **SpatioTemporalGraph**| Time & Space hybrid | Historical battles |

---

## 🛠️ Architecture Overview

The system is built on a robust triad: **Auto-Types** (Multi-typed knowledge structures definition), **Templates** (Declarative extraction schema), and **Methods** (The LLM Execution strategy).

![Architecture](docs/assets/architecture-v4.png)

- **Design Guide**: [Template Design Guide](./hyperextract/templates/DESIGN_GUIDE.md)
- **Preset Templates**: [presets directory](./hyperextract/templates/presets/)

---

## 📈 Comparison with Other Libraries

| Feature | GraphRAG | LightRAG | KG-Gen | ATOM | **Hyper-Extract** |
|---------|:---:|:---:|:---:|:---:|:---:|
| Knowledge Graph | ✅ | ✅ | ✅ | ✅ | ✅ |
| Temporal Graph | ✅ | ❌ | ❌ | ✅ | ✅ |
| Spatial Graph | ❌ | ❌ | ❌ | ❌ | ✅ |
| Hypergraph | ❌ | ❌ | ❌ | ❌ | ✅ |
| Domain Templates | ❌ | ❌ | ❌ | ❌ | ✅ |
| CLI Tool | ❌ | ❌ | ❌ | ❌ | ✅ |
| Multi-language | Partial | ❌ | ❌ | ❌ | ✅ |
| Visualization | Partial | ❌ | ❌ | ❌ | ✅ |

---

## 📚 Related Documentation

| Documentation | Description |
|---------------|-------------|
| [CLI Guide](./hyperextract/cli/README.md) | Complete CLI reference |
| [Template Gallery](./hyperextract/templates/) | 38+ domain templates |
| [Example Code](./examples/) | Python API examples |
| [Full Documentation](./docs/) | Architecture & implementation |

---

## 🤝 Contributing

Contributions are welcome! Please submit Issues and PRs.

## 📄 License

Apache-2.0
