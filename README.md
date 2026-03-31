# 🔍 Hyper-Extract

> **"Stop reading. Start understanding."**

> *"告别文档焦虑，让信息一目了然"*

Transform documents into **knowledge abstracts** — with just one command.

![Hero](docs/assets/hero-v2.jpg)

[📖 English Version](./README.md) · [中文版](./README_ZH.md)

---

## ✨ Features

- 🔷 **Knowledge Structures** — Model, List, Set, Graph, Hypergraph, TemporalGraph, SpatialGraph, SpatioTemporalGraph
- 💻 **Interactive CLI** — Extract, build, and interact with knowledge abstracts
- ⚡ **Incremental Updates** — Continuously update knowledge abstracts with new questions

---

## ⚡ Quick Start

### Install with uv

```bash
uv pip install hyper-extract
```

### CLI Usage

```bash
he config init -k YOUR_API_KEY
he parse document.md -o ./output/ -l zh
he search ./output/ "What are the key events?"
he feed ./output/ new_document.md
he show ./output/
```

<details>
<summary>🐍 Python API</summary>

```python
from hyperextract import Template

ka = Template.create("finance/event_timeline")
result = ka.parse(annual_report_text)
# result.timeline = [Event("Q1 revenue", "2024-01"), ...]
```

</details>

> 🔗 For detailed CLI usage, see [CLI Guide](./hyperextract/cli/README.md)

---

## 📖 Knowledge Abstraction

> From simple structured data to complex spatio-temporal graphs — **10+ extraction methods**, covering **6 domains**, with **80+ templates**.

<details>
<summary>🔧 8 Knowledge Structures</summary>

| Type | Best For | Example |
|------|----------|---------|
| AutoModel | Structured reports | Financial summaries |
| AutoList | Ordered lists | Meeting notes |
| AutoSet | Deduplicated collections | Product catalogs |
| AutoGraph | Binary relations | Social networks |
| AutoHypergraph | Multi-party events | Contract disputes |
| AutoTemporalGraph | Temporal relations | News timelines |
| AutoSpatialGraph | Spatial relations | Delivery routes |
| AutoSpatioTemporalGraph | Events in time & space | Historical battles |

</details>

<details>
<summary>🔍 Extraction Methods (10+)</summary>

| Method | Type | Description |
|--------|------|-------------|
| graph_rag | graph | Graph-RAG + community detection |
| light_rag | graph | Lightweight entity-relation extraction |
| hyper_rag | hypergraph | Hypergraph for multi-entity relations |
| cog_rag | graph | Cognitive retrieval augmentation |
| itext2kg | graph | High-quality triple extraction |
| kg_gen | graph | Structured knowledge generation |
| atom | graph | Temporal graph + evidence attribution |

</details>

<details>
<summary>🌍 Domain Templates (6 Domains / 38+ Templates)</summary>

Templates are written in YAML to define extraction targets and output structure.
- **Design Guide**: [Template Design Guide](./hyperextract/templates/DESIGN_GUIDE.md)
- **Preset Templates**: [presets directory](./hyperextract/templates/presets/)

| Domain | Templates | Typical Scenarios |
|--------|-----------|-------------------|
| General | 13 | Workflow, Biography, Concept maps |
| Finance | 5 | Earnings reports, Risk factors |
| Medicine | 5 | Clinical records, Drug interactions |
| TCM | 5 | Formula composition, Meridian flow |
| Industry | 5 | Equipment topology, Failure analysis |
| Legal | 5 | Contract clauses, Case citations |

</details>

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
