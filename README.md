# 🔍 Hyper-Extract

> **"Stop reading. Start understanding."**
>
> *"告别文档焦虑，让信息一目了然"*

Transform unstructured documents into **searchable, visual, structured knowledge** — with just one command.

[📖 English Version](./README.md) · [中文版](./README_ZH.md)

![Start](docs/assets/start.jpg)

---

## ⚡ Quick Start

```bash
pip install hyper-extract

he parse document.md -o kb
he show kb
he search kb "key insights"
```

![CLI Welcome Screen](docs/assets/cli.png)

---

## 🧩 Knowledge Structures

![8 Types](docs/assets/8-types.jpg)

8 structures for extracting different types of information:

**Scalar Types:**
| Structure | Best For | Example |
|-----------|----------|---------|
| AutoModel | Structured reports | Financial statements |
| AutoList | Key points | Meeting notes |
| AutoSet | Entity collection | Product catalog |

**Graph Types:**
| Structure | Best For | Example |
|-----------|----------|---------|
| AutoGraph | Binary relations | Social networks |
| AutoHypergraph | Multi-party events | Legal disputes |
| AutoTemporalGraph | Event sequences | News timeline |
| AutoSpatialGraph | Locations | Delivery routes |
| AutoSpatioTemporalGraph | Events in time & space | Historical battles |

### Comparison with Other Libraries

| Feature | KG-Gen | ATOM | Graphiti | LightRAG | Hyper-Extract |
|---------|--------|------|----------|----------|---------------|
| Knowledge Graph | ✅ | ✅ | ❌ | ✅ | ✅ |
| Temporal Graph | ❌ | ✅ | ✅ | ❌ | ✅ |
| Spatial Graph | ❌ | ❌ | ❌ | ❌ | ✅ |
| Hypergraph | ❌ | ❌ | ❌ | ❌ | ✅ |
| Templates | ❌ | ❌ | ❌ | ❌ | ✅ |
| CLI Tool | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 🌍 Domain Templates

![Domain](docs/assets/domain.png)

Pre-built templates for common domains:

| Domain | Templates |
|--------|-----------|
| Finance | Earnings reports, shareholder structure, risk factors |
| Legal | Contracts, case law, compliance requirements |
| Medicine | Clinical records, pharmacology, treatment plans |
| Industry | Equipment specs, incident reports, safety procedures |
| General | Meeting notes, articles, research papers |
| TCM | Herbal formulas, meridian flow, syndrome reasoning |

See [Template Gallery](hyperextract/templates/) for all templates.

---

## 📚 Documentation

- [📖 Full Documentation](docs/)
- [💻 Examples](examples/)
- [🏷️ Template Gallery](hyperextract/templates/)

