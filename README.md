<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo/logo-horizontal-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/logo/logo-horizontal.svg">
  <img alt="Hyper-Extract Logo" src="docs/assets/logo/logo-horizontal.svg" width="600">
</picture>

<br/>
<br/>

**Smart Knowledge Extraction CLI**

**Transform documents into structured knowledge with one command.**

[📖 English Version](./README.md) · [中文版](./README_ZH.md)

[![PyPI Version](https://img.shields.io/pypi/v/hyperextract)](https://pypi.org/project/hyperextract/)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success)]()

<br/>

> **"Stop reading. Start understanding."**  
> *"告别文档焦虑，让信息一目了然"*

<br/>

<img src="docs/assets/hero.jpg" alt="Hero & Workflow" width="800" style="max-width: 100%;">

<br/>
</div>

Hyper-Extract is an intelligent, LLM-powered knowledge extraction and evolution framework. It radically simplifies transforming highly unstructured texts into persistent, predictable, and strongly-typed **Knowledge Abstracts**. It effortlessly extracts information into a wide spectrum of formats—ranging from simple **Collections** (Lists/Sets) and **Pydantic Models**, to complex **Knowledge Graphs**, **Hypergraphs**, and even **Spatio-Temporal Graphs**.

## 📑 Table of Contents

- [Core Features](#-core-features)
- [Quick Start](#-quick-start)
  - [CLI](#2-the-command-line-way)
  - [Python API](#-the-python-api-way)
- [The 8 Auto-Types](#-deep-dive-the-8-auto-types)
- [Architecture](#-architecture-overview)
- [Comparison](#-comparison-with-other-libraries)
- [Documentation](#-related-documentation)

## ✨ Core Features

- 🔷 **8 Auto-Types:** From basic `AutoModel`/`AutoList` to advanced `AutoGraph`, `AutoHypergraph`, and `AutoSpatioTemporalGraph`.
- 🧠 **10+ Extraction Engines:** Out-of-the-box support for cutting-edge retrieval paradigms like `GraphRAG`, `LightRAG`, `Hyper-RAG`, and `KG-Gen`.
- 📝 **Declarative YAML Templates:** Zero-code extraction definition. Includes 80+ presets across 6 domains.
- 🔄 **Incremental Evolution:** Feed new documents on the fly to continuously map out and expand the extracted knowledge.

***

## ⚡ Quick Start

### 1. Installation

**For CLI Users** (install `he` command globally):

```bash
uv tool install hyperextract
```

**For Python Developers** (use as library):

```bash
uv pip install hyperextract
```

### 2. The Command Line Way

Extract, search, and manage directly from CLI.

> By default, the CLI uses `gpt-4o-mini` and `text-embedding-3-small`.

```bash
# Configure OpenAI API Key
he config init -k YOUR_OPENAI_API_KEY

# Extract knowledge
he parse examples/en/tesla.md -t general/biography_graph -o ./output/ -l en

# Query the knowledge abstract
he search ./output/ "What are Tesla's major achievements?"

# Visualize the knowledge graph
he show ./output/

# Incrementally supplement knowledge
he feed ./output/ examples/en/tesla_question.md

# Show the updated knowledge graph
he show ./output/
```

<details>
<summary><b>🐍 The Python API Way</b> (click to expand)</summary>
<br>

### Installation

```bash
# Clone the repository
git clone https://github.com/yifanfeng97/hyper-extract.git
cd hyper-extract

# Install dependencies
uv sync
```

### Configuration

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your API key and base URL
# OPENAI_API_KEY=your-api-key
# OPENAI_BASE_URL=https://api.openai.com/v1
```

### Usage

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from hyperextract import Template

# Create a template
ka = Template.create("general/biography_graph")

# Parse a document
with open("examples/en/tesla.md", "r", encoding="utf-8") as f:
    text = f.read()
result = ka.parse(text)

# Visualize the knowledge graph
ka.show(result)

# Incrementally supplement knowledge
with open("examples/en/tesla_question.md", "r", encoding="utf-8") as f:
    new_text = f.read()
ka.feed(result, new_text)

# Show the updated knowledge graph
ka.show(result)
```

> 🔗 For complete examples, see [examples/en](./examples/en/)

</details>

<br>

**Installation Comparison:**

| Use Case | Command | Purpose |
|----------|---------|---------|
| CLI Tool | `uv tool install hyperextract` | Install `he` command globally |
| Python Library | `uv pip install hyperextract` | Use in Python code |

## 🧩 Deep Dive: The 8 Auto-Types

Our framework embraces complexity without making you write boilerplate code.

<img src="docs/assets/autotypes.jpg" alt="Knowledge Structures Matrix" width="700" style="max-width: 100%;">

### Example: AutoGraph Visualization

Here is the knowledge graph visualization after `AutoGraph` extraction:

<img src="docs/assets/en_show.jpg" alt="AutoGraph Visualization" width="600" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">

## 🛠️ Architecture Overview

Hyper-Extract follows a **three-layer architecture**:

- **Auto-Types** define the data structures for knowledge extraction. With 8 strong-typed structures (AutoModel, AutoList, AutoSet, AutoGraph, AutoHypergraph, AutoTemporalGraph, AutoSpatialGraph, AutoSpatioTemporalGraph), they serve as the output format for all extractions.

- **Methods** provide extraction algorithms built on Auto-Types. This includes Typical methods (KG-Gen, iText2KG, iText2KG*) and RAG-based methods (GraphRAG, LightRAG, Hyper-RAG, HypergraphRAG, Cog-RAG).

- **Templates** offer domain-specific configurations with ready-to-use prompts and data structures. Covering 6 domains (Finance, Legal, Medical, TCM, Industry, General) with 80+ preset templates, users can extract knowledge without dealing with Auto-Types or Methods directly.

Use via **CLI** (`he parse`, `he search`, `he show`...) or **Python API** (`Template.create()`).

<img src="docs/assets/arch.jpg" alt="Architecture" width="750" style="max-width: 100%;">

### 📚 Related Documentation

- **Preset Templates**: Browse [80+ ready-to-use templates](./hyperextract/templates/presets/) across 6 domains
- **Design Guide**: Learn how to [create custom templates](./hyperextract/templates/DESIGN_GUIDE.md)

<details>
<summary><b>📋 Template Structure Example (Graph Type)</b></summary>

Here's a complete YAML template example for **Graph** type extraction (entity-relationship extraction):

```yaml
language: en

name: Knowledge Graph
type: graph
tags: [general]

description: 'Extract entities and their relationships to construct a knowledge graph.'

output:
  entities:
    fields:
    - name: name
      type: str
      description: 'Entity name'
    - name: type
      type: str
      description: 'Entity type: e.g., person, organization, event'
    - name: description
      type: str
      description: 'Entity description'
  relations:
    fields:
    - name: source
      type: str
      description: 'Source entity'
    - name: target
      type: str
      description: 'Target entity'
    - name: type
      type: str
      description: 'Relation type: e.g., invention, collaboration, competition'
    - name: description
      type: str
      description: 'Relation description'

guideline:
  target: 'Extract entities and their relationships from the text.'
  rules_for_entities:
    - 'Extract meaningful entities'
    - 'Maintain consistent naming'
  rules_for_relations:
    - 'Create relations only when explicitly expressed in the text'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}'
```

</details>

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

## 📚 Related Documentation

- [Full Documentation](https://hyper-extract.github.io/en/) - Complete documentation site
- [中文文档](https://hyper-extract.github.io/zh/) - 中文文档
- [CLI Guide](https://hyper-extract.github.io/en/guides/cli/) - Command-line interface
- [Template Gallery](https://hyper-extract.github.io/en/reference/template-gallery/) - Available templates
- [Example Code](./examples/) - Working examples

## 🤝 Contributing & License

Contributions are welcome! Please submit Issues and PRs.
Licensed under **Apache-2.0**.
