# Hyper-Extract

> **"Stop reading. Start understanding."**

**Transform documents into knowledge abstracts — with just one command.**

![Hero & Workflow](assets/hero.jpg)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success)]()

## What is Hyper-Extract?

Hyper-Extract is an intelligent, LLM-powered knowledge extraction and evolution framework. It radically simplifies transforming highly unstructured texts into persistent, predictable, and strongly-typed knowledge summaries. It effortlessly extracts information into a wide spectrum of formats—ranging from simple **Collections** (Lists/Sets) and **Pydantic Models**, to complex **Knowledge Graphs**, **Hypergraphs**, and even **Spatio-Temporal Graphs**.

## Core Features

- 🔷 **8 Auto-Types:** From basic `AutoModel`/`AutoList` to advanced `AutoGraph`, `AutoHypergraph`, and `AutoSpatioTemporalGraph`.
- 🧠 **10+ Extraction Engines:** Out-of-the-box support for cutting-edge retrieval paradigms like `GraphRAG`, `LightRAG`, `Hyper-RAG`, and `KG-Gen`.
- 📝 **Declarative YAML Templates:** Zero-code extraction definition. Includes 80+ presets across 6 domains.
- 🔄 **Incremental Evolution:** Feed new documents on the fly to continuously map out and expand the extracted knowledge.

## Quick Start

### Installation

```bash
uv pip install hyper-extract
```

### The Command Line Way

```bash
he config init -k <your-api-key>
he parse sample.md -t general/biography_graph -o ./output/ -l en
he search ./output/ "What are the key events?"
he feed ./output/ another_sample.md
```

### The Python API Way

```python
from hyperextract import Template

ka = Template.create("general/biography_graph")
result = ka.parse(text)
```

## Documentation

- [Getting Started](getting-started/index.md) - Get up and running quickly
- [Concepts](concepts/index.md) - Understand the core concepts
- [Guides](guides/index.md) - Step-by-step tutorials
- [Reference](reference/index.md) - API and configuration reference

## The 8 Auto-Types

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

After extraction with `AutoGraph`, you can visualize your knowledge graph:

![AutoGraph Visualization](assets/en_show.png)

## Architecture

![Architecture](assets/arch.png)

The system is built on a robust triad: **Auto-Types** (Multi-typed structures), **Methods** (The Execution strategy), and **Templates** (Declarative schema).

## License

Licensed under **Apache-2.0**.
