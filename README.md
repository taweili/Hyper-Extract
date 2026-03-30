# 🔍 Hyper-Extract

> **"Stop reading. Start understanding."**

> *"告别文档焦虑，让信息一目了然"*

Transform documents into **knowledge abstracts** — with just one command.

![Hero](docs/assets/hero-v2.jpg)

[📖 English Version](./README.md) · [中文版](./README_ZH.md)

---

## ⚡ Quick Start

```bash
pip install hyper-extract

he config init -k YOUR_API_KEY

he parse document.md -o ./knowledge_abstract/ -l zh
```

> 🔗 For detailed usage, see [CLI Guide](./hyperextract/cli/README.md)

---

## ✨ Key Features

| 🤖 8 Knowledge Types | 🌍 38+ Domain Templates | 💻 Interactive CLI | 🔍 Semantic Search |
|:---:|:---:|:---:|:---:|
| From lists to spatio-temporal graphs | Finance, Medical, Legal ready-to-use | One command for full workflow | FAISS vector similarity |

> 🔗 Learn more about [8 Knowledge Types](#knowledge-types) | [Domain Templates](#domain-templates)

---

## 📊 Knowledge Types

![8 Types](docs/assets/8-types-v2.jpg)

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

> 🔗 See [Full Type Documentation](./hyperextract/types/) | [Template Design Guide](./hyperextract/templates/DESIGN_GUIDE.md)

---

## 🌍 Domain Templates

![Domains](docs/assets/domains-v2.png)

| Domain | Templates | Typical Scenarios |
|--------|-----------|-------------------|
| General | 13 | Workflow, Biography, Concept maps |
| Finance | 5 | Earnings reports, Risk factors |
| Medicine | 5 | Clinical records, Drug interactions |
| TCM | 5 | Formula composition, Meridian flow |
| Industry | 5 | Equipment topology, Failure analysis |
| Legal | 5 | Contract clauses, Case citations |

> 🔗 See [Full Template Gallery](./hyperextract/templates/) | [Template Design Guide](./hyperextract/templates/DESIGN_GUIDE.md)

---

## 🎯 Python API Examples

```python
from hyperextract import Template

ka = Template.create("finance/earnings_summary")
result = ka.parse(financial_report_text)
# result.operating_revenue = "100 billion RMB"
```

> 🔗 See more [Example Code](./examples/)

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

## 💻 CLI Reference

### Parse Documents

```bash
he parse document.md -o ./knowledge_abstract/ -l zh
he parse earnings.md -o ./finance_report/ -t finance/earnings_summary -l zh
```

### Search & Chat

```bash
he search ./finance_report/ "What was the revenue growth?"
he talk ./finance_report/ -i  # Interactive mode
```

### Visualize

```bash
he show ./finance_report/  # Graph visualization
he info ./finance_report/  # Show statistics
```

> 🔗 For full CLI documentation, see [CLI Guide](./hyperextract/cli/README.md)

---

## 🤝 Contributing

Contributions are welcome! Please submit Issues and PRs.

## 📄 License

Apache-2.0

---

## 📚 Related Documentation

| Documentation | Description |
|---------------|-------------|
| [CLI Guide](./hyperextract/cli/README.md) | Complete CLI reference |
| [Template Gallery](./hyperextract/templates/) | 38+ domain templates |
| [Example Code](./examples/) | Python API examples |
| [Full Documentation](./docs/) | Architecture & implementation |
