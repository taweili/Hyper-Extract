# 🚀 Hyper-Extract

> **"Stop reading. Start understanding."**
> *"告别文档焦虑，让信息一目了然"*

**Smart Knowledge Extraction CLI — Transform documents into structured knowledge with one command.**

![Hero & Workflow](assets/hero.png)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success)]()

## What is Hyper-Extract?

Hyper-Extract is an intelligent, LLM-powered knowledge extraction and evolution framework. It radically simplifies transforming highly unstructured texts into persistent, predictable, and strongly-typed knowledge summaries. It effortlessly extracts information into a wide spectrum of formats—ranging from simple **Collections** (Lists/Sets) and **Pydantic Models**, to complex **Knowledge Graphs**, **Hypergraphs**, and even **Spatio-Temporal Graphs**.

## ✨ Core Features

- 🔷 **8 Auto-Types:** From basic `AutoModel`/`AutoList` to advanced `AutoGraph`, `AutoHypergraph`, and `AutoSpatioTemporalGraph`.
- 🧠 **10+ Extraction Engines:** Out-of-the-box support for cutting-edge retrieval paradigms like `GraphRAG`, `LightRAG`, `Hyper-RAG`, and `KG-Gen`.
- 📝 **Declarative YAML Templates:** Zero-code extraction definition. Includes 80+ presets across 6 domains.
- 🔄 **Incremental Evolution:** Feed new documents on the fly to continuously map out and expand the extracted knowledge.

## ⚡ Quick Start

### Installation

```bash
uv pip install hyper-extract
```

### The Command Line Way

```bash
# Configure OpenAI API Key
he config init -k YOUR_OPENAI_API_KEY

# Extract knowledge
he parse examples/en/tesla.md -t general/biography_graph -o ./output/ -l en

# Query the knowledge base
he search ./output/ "What are Tesla's major achievements?"

# Visualize the knowledge graph
he show ./output/

# Incrementally supplement knowledge
he feed ./output/ examples/en/tesla_question.md

# Show the updated knowledge graph
he show ./output/
```

### The Python API Way

#### Installation

```bash
# Clone the repository
git clone https://github.com/yifanfeng97/hyper-extract.git
cd hyper-extract

# Install dependencies
uv sync
```

#### Configuration

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your API key and base URL
# OPENAI_API_KEY=your-api-key
# OPENAI_BASE_URL=https://api.openai.com/v1
```

#### Usage

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from hyperextract import Template

# Create a template
ka = Template.create("general/biography_graph")

# Parse a document
with open("examples/en/tesla.md", "r") as f:
    text = f.read()
result = ka.parse(text)

# Visualize the knowledge graph
ka.show(result)

# Incrementally supplement knowledge
with open("examples/en/tesla_question.md", "r") as f:
    new_text = f.read()
ka.feed(result, new_text)

# Show the updated knowledge graph
ka.show(result)
```

## 🧩 The 8 Auto-Types

Our framework embraces complexity without making you write boilerplate code.

![Knowledge Structures Matrix](assets/autotypes.png)

| Type | Description |
|------|-------------|
| AutoModel | Pydantic model extraction |
| AutoList | List/collection extraction |
| AutoSet | Unique set extraction |
| AutoGraph | Knowledge graph extraction |
| AutoHypergraph | Hypergraph extraction |
| AutoTemporalGraph | Temporal knowledge graph |
| AutoSpatialGraph | Spatial knowledge graph |
| AutoSpatioTemporalGraph | Spatio-temporal knowledge graph |

### Example: AutoGraph Visualization

Here is the knowledge graph visualization after `AutoGraph` extraction:

![AutoGraph Visualization](assets/en_show.png)

## 🛠️ Architecture

Hyper-Extract follows a **three-layer architecture**:

- **Auto-Types** define the data structures for knowledge extraction. With 8 strong-typed structures (AutoModel, AutoList, AutoSet, AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph), they serve as the output format for all extractions.

- **Methods** provide extraction algorithms built on Auto-Types. This includes Typical methods (KG-Gen, iText2KG, iText2KG*) and RAG-based methods (GraphRAG, LightRAG, Hyper-RAG, HypergraphRAG, Cog-RAG).

- **Templates** offer domain-specific configurations with ready-to-use prompts and data structures. Covering 6 domains (Finance, Legal, Medical, TCM, Industry, General) with 80+ preset templates, users can extract knowledge without dealing with Auto-Types or Methods directly.

Use via **CLI** (`he parse`, `he search`, `he show`...) or **Python API** (`Template.create()`).

![Architecture](assets/arch.png)

## 📈 Comparison with Other Libraries

| Feature          | GraphRAG | LightRAG | KG-Gen | ATOM | **Hyper-Extract** |
| ---------------- | :------: | :------: | :----: | :--: | :---------------: |
| Knowledge Graph  |     ✅    |     ✅    |    ✅   |   ✅  |         ✅         |
| Temporal Graph   |     ✅    |     ❌    |    ❌   |   ✅  |         ✅         |
| Spatial Graph    |     ❌    |     ❌    |    ❌   |   ❌  |         ✅         |
| Hypergraph       |     ❌    |     ❌    |    ❌   |   ❌  |         ✅         |
| Domain Templates |     ❌    |     ❌    |    ❌   |   ❌  |         ✅         |
| CLI Tool         |     ✅    |     ❌    |    ❌   |   ❌  |         ✅         |
| Multi-language   |     ✅    |     ❌    |    ❌   |   ❌  |         ✅         |

## 📚 Documentation

- [Getting Started](cli/index.md) - Get up and running quickly
- [Domain Templates](templates/index.md) - Ready-to-use templates

## 🤝 Contributing & License

Contributions are welcome! Please submit Issues and PRs.
Licensed under **Apache-2.0**.
