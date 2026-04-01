# Hyper-Extract

> **"Stop reading. Start understanding."**

**Transform documents into knowledge abstracts — with just one command.**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success)]()

## What is Hyper-Extract?

Hyper-Extract is an intelligent, LLM-powered knowledge extraction and evolution framework. It radically simplifies transforming highly unstructured texts into persistent, predictable, and strongly-typed knowledge summaries. It effortlessly extracts information into a wide spectrum of formats—ranging from simple **Collections** (Lists/Sets) and **Pydantic Models**, to complex **Knowledge Graphs**, **Hypergraphs**, and even **Spatio-Temporal Graphs**.

## Core Features

- 🔷 **8 Auto-Types:** From basic `AutoModel`/`AutoList` to advanced `AutoGraph`, `AutoHypergraph`, and `AutoSpatioTemporalGraph`.
- 🧠 **10+ Extraction Engines:** Out-of-the-box support for cutting-edge retrieval paradigms like `graph_rag`, `light_rag`, and `hyper_rag`.
- 📝 **Declarative YAML Templates:** Zero-code extraction definition. Includes 80+ presets across 6 domains.
- 🔄 **Incremental Evolution:** Feed new documents on the fly to continuously map out and expand the extracted knowledge.

## Quick Start

### Installation

```bash
uv pip install hyper-extract
```

### The Command Line Way

```bash
he config init -k YOUR_API_KEY
he parse document.md -o ./output/ -l zh
he search ./output/ "What are the key events?"
he feed ./output/ new_document.md
```

### The Python API Way

```python
from hyperextract import Template

# Load a preset YAML template
ka = Template.create("finance/event_timeline")

# Extract and auto-parse the document
result = ka.parse(annual_report_text)
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

## Architecture

The system is built on a robust triad: **Auto-Types** (Multi-typed structures), **Methods** (The Execution strategy), and **Templates** (Declarative schema).

## License

Licensed under **Apache-2.0**.
