# Hyper-Extract: The Knowledge Engine for Vertical AI Agents 🧠🚀

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

**Hyper-Extract** is a next-generation framework designed to transform massive, unstructured domain documents into **searchable, queryable, and actionable** knowledge structures. 

Stop treating your documents as dead text chunks. With Hyper-Extract, every PDF, report, and manual becomes a live, structured brain for your AI Agents.

[中文版 (README_ZH.md)](README_ZH.md) | [Domain Samples](examples/)

---

## 🌟 Why Hyper-Extract?

Traditional RAG often fails in professional domains because it loses the **logical structure** of knowledge. Hyper-Extract solves this by providing a unique **3-Layer Architecture**:

### 🧱 Layer 1: Knowledge Primitives (`hyperextract.types`)
The "DNA" of knowledge. We provide specialized "AutoType" structures categorized into four levels of complexity:

| Level | Primitives | Core Logic | Best For |
| :--- | :--- | :--- | :--- |
| **Scalar & Doc** | `AutoModel` | Many chunks -> **One** consistent object | Research reports, Infoboxes, Summaries |
| **Collections** | `AutoList`, `AutoSet` | Many independent or unique items | Entity registries, Event logs, Glossaries |
| **Graphs** | `AutoGraph`, `AutoHypergraph` | Pairwise or N-ary (Hyper-edge) relations | Knowledge Graphs, Complex causality reasoning |
| **Context-Aware** | `AutoTemporalGraph`, `AutoSpatialGraph`, `AutoSpatioTemporalGraph` | Resolves relative time/space context | Timelines, History, IoT |

### ⚙️ Layer 2: Extraction Engines (`hyperextract.methods`)
The "Brain" of the framework. Built-in SOTA algorithms that turn primitives into power:
- **Light-RAG / GraphRAG**: High-efficiency retrieval over graph structures.
- **Hyper-RAG**: Reasoning via complex hyper-relations.
- **CogRAG**: Cognition-driven hierarchical extraction.

### 🧠 Layer 3: 12+ Domain Expert Templates (`hyperextract.templates`)
The "Expertise" you need. Out-of-the-box schemas and prompts for vertical industries:
- **Finance, Medicine, Law, TCM, Industry, History, Biology, Literature, Travel, News, Agriculture, Food.**

---

## 🎭 Transform Your Domain in Minutes

"From static files to an intelligent agent engine."

| Your Domain | From Static Docs ... | To Actionable Agents 🤖 |
| :--- | :--- | :--- |
| **💰 Finance** | Annual reports, prospectuses | **Investment Analyst Agent** (Reasoning over valuation logic) |
| **🏥 Medicine** | Clinical guidelines, patient records | **Diagnostic Assistant Agent** (Mapping symptoms to pathways) |
| **⚖️ Legal** | Contracts, court rulings | **Compliance Auditor Agent** (Extracting obligations & risks) |
| **🔧 Industry** | Maintenance logs, specs | **Ops Expert Agent** (Connecting failure modes to root causes) |
| **📜 History** | Chronicles, biographies | **Historian Agent** (Reconstructing event timelines) |

---

## 🚀 Quick Start: Build an "Askable" Knowledge Base

```python
from hyperextract.types import AutoGraph
from hyperextract.templates.en.finance import ResearchNoteSummary
from langchain_openai import ChatOpenAI

# 1. Load an industry-expert template
llm = ChatOpenAI(model="gpt-4o-mini")
kb = AutoGraph.from_template(ResearchNoteSummary, llm_client=llm)

# 2. Feed your domain text (Extraction happens automatically!)
text = "Apple's valuation is driven by its services growth and iPhone 16 cycle..."
kb.feed_text(text)

# 3. Chat with the Structure (Actionable Insight)
answer = kb.chat("What are the core drivers of Apple's valuation?")
print(answer.content)
```


---

## 🎨 Domain Templates

The `hyperextract/templates` directory provides a wealth of domain-specific definitions that you can import directly without writing prompts from scratch:

| Category | Templates | Description |
| :--- | :--- | :--- |
| **General** | `General`, `IText2KG` | Versatile extraction for most daily knowledge. |
| **Science** | `Physics`, `Chemistry`, `Biology` | Capture experiments, elements, and reactions. |
| **Industry** | `Finance`, `Legal` | Extract compliance, risks, and entity webs. |
| **Entertainment** | `Game`, `Movie`, `Food` | Perfect for story plots, character networks, and recipes. |
| ... | | 15+ domains in the [templates folder](hyperextract/templates) |

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
