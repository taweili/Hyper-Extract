# Python SDK

Python API for Hyper-Extract.

## Installation

```bash
pip install hyper-extract
```

## Quick Start

```python
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from hyperextract import Template

# Create a template
ka = Template.create("general/biography_graph", "en")

# Parse a document
with open("examples/en/tesla.md", "r") as f:
    text = f.read()
result = ka.parse(text)

# Access results
print(result.entities)
print(result.relations)
```

## Core APIs

| API | Purpose |
|-----|---------|
| `Template.create()` | Create template instance |
| `ka.parse()` | Parse document |
| `ka.feed()` | Incrementally supplement |
| `ka.search()` | Query knowledge base |

## Configuration

[→ Python SDK Configuration Guide](./config.md)

## Detailed Guide

[→ Python API Details](./python-api.md)

## Usage Examples

- [Finance Domain Templates](../templates/finance.md)
- [Legal Domain Templates](../templates/legal.md)
- [Medical Domain Templates](../templates/medicine.md)
