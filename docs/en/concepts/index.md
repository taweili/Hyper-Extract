# Core Concepts

## Overview

Hyper-Extract is a knowledge extraction framework that extracts structured knowledge from various documents. This section introduces core concepts to help you understand how the system works.

## Core Concepts

### Template

Templates use YAML to define what to extract, providing a declarative way to specify extraction schemas without writing code.

Learn more: [Templates](./templates.md)

### AutoType

Hyper-Extract supports 8 auto types, each designed for different extraction scenarios:

| Type | Description | Use Case |
|------|-------------|----------|
| `model` | Single structured object | Extract single record |
| `list` | Ordered list | Extract ranked items |
| `set` | Deduplicated set | Extract unique entities |
| `graph` | Binary relation graph | Extract entity relations |
| `hypergraph` | Multi-entity relation | Extract multi-party relations |
| `temporal_graph` | Temporal graph | Add time dimension |
| `spatial_graph` | Spatial graph | Add space dimension |
| `spatio_temporal_graph` | Spatio-temporal graph | Add both time and space |

Learn more: [AutoTypes](./auto-types.md)

### Methods

Hyper-Extract supports multiple extraction methods:

- **Local Models**: Use locally deployed models
- **API Models**: Use cloud APIs (e.g., OpenAI, Claude)
- **Hybrid Mode**: Combine multiple methods

Learn more: [Methods](./methods.md)

## Quick Start

1. [Installation](../getting-started/installation.md)
2. [Quick Start Tutorial](../getting-started/quickstart.md)
3. [Template Design](./templates.md)

## Next Steps

- Browse the [Template Gallery](../reference/template-gallery.md)
- Explore [Domain Templates](../guides/domain-templates/index.md)
- Learn the [Python API](../guides/python-api.md)
