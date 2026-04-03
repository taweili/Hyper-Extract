# CLI

Command-line interface for Hyper-Extract.

## Installation

```bash
uv pip install hyper-extract
```

## Quick Start

```bash
# Configure API Key
he config init -k YOUR_OPENAI_API_KEY

# Extract knowledge
he parse document.txt -t general/biography_graph -o ./output/

# Query the knowledge base
he search ./output/ "What are the key events?"

# Visualize the knowledge graph
he show ./output/
```

## Core Commands

| Command | Purpose |
|---------|---------|
| `he config init` | Configure API Key |
| `he parse` | Extract knowledge |
| `he search` | Query knowledge base |
| `he show` | Visualize graph |
| `he feed` | Incrementally supplement |
| `he list` | List templates |

## Configuration

[→ CLI Configuration Guide](./config.md)

## Detailed Guide

[→ CLI Command Details](./cli.md)

## Usage Examples

- [Finance Domain Templates](../templates/finance.md)
- [Legal Domain Templates](../templates/legal.md)
- [Medical Domain Templates](../templates/medicine.md)
