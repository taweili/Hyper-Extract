# Concepts

This section explains the core concepts behind Hyper-Extract.

## What's in This Section

- [Auto-Types](auto-types.md) - The 8 data structures for knowledge representation
- [Extraction Methods](methods.md) - The 10+ engines for knowledge extraction
- [Templates](templates.md) - Declarative YAML schemas for extraction

## Core Concepts

### Auto-Types

Hyper-Extract provides 8 auto-types, ranging from simple collections to complex graphs:

| Type | Use Case |
|------|----------|
| AutoModel | Structured data extraction |
| AutoList | List/collection extraction |
| AutoSet | Unique item extraction |
| AutoGraph | Knowledge graph extraction |
| AutoHypergraph | Complex relationship extraction |
| AutoTemporalGraph | Time-aware knowledge graphs |
| AutoSpatialGraph | Location-aware knowledge graphs |
| AutoSpatioTemporalGraph | Time and location aware graphs |

### Extraction Methods

Choose the right method for your extraction task:

| Method | Best For |
|--------|----------|
| atom | Simple, direct extraction |
| graph_rag | Graph-based retrieval |
| light_rag | Lightweight retrieval |
| hyper_rag | Hypergraph extraction |
| cog_rag | Cognitive retrieval |

### Templates

Templates define WHAT to extract using declarative YAML. They provide:

- Type-safe schemas
- Validation rules
- Custom extraction logic

## Learn More

- [Auto-Types](auto-types.md) - Deep dive into each type
- [Methods](methods.md) - Compare extraction methods
- [Templates](templates.md) - Create custom templates
