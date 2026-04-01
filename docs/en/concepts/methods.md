# Extraction Methods

Hyper-Extract provides multiple extraction methods, each optimized for different use cases.

## Available Methods

### Basic Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| atom | Direct extraction | Simple, straightforward extraction |
| kg_gen | Knowledge graph generation | Structured knowledge extraction |

### RAG-Based Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| graph_rag | Graph-based RAG | Complex relationship extraction |
| light_rag | Lightweight RAG | Fast, efficient extraction |
| hyper_rag | Hypergraph RAG | Multi-entity relationships |
| hypergraph_rag | Advanced hypergraph | Complex network analysis |
| cog_rag | Cognitive RAG | Reasoning-based extraction |

### Specialized Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| itext2kg | Text to knowledge graph | Document conversion |
| itext2kg_star | Enhanced text-to-kg | Advanced document processing |

## Method Comparison

### Speed

```
fast: atom > light_rag > kg_gen > graph_rag
slow: hyper_rag > cog_rag > hypergraph_rag
```

### Accuracy

```
high: cog_rag > graph_rag > hypergraph_rag > hyper_rag
medium: kg_gen > itext2kg > light_rag > atom
```

### Use Case Matrix

| Task | Recommended Method |
|------|-------------------|
| Simple extraction | atom |
| Fast prototyping | light_rag |
| Knowledge graphs | graph_rag |
| Complex relationships | hyper_rag |
| Reasoning tasks | cog_rag |
| Document conversion | itext2kg |

## Usage Examples

### Using atom Method

```python
from hyperextract.methods import atom

result = atom.extract(text, schema=MySchema)
```

### Using graph_rag Method

```python
from hyperextract.methods import graph_rag

result = graph_rag.extract(
    text,
    node_types=["Person", "Organization"],
    edge_types=["WORKS_AT", "KNOWS"]
)
```

### Using cog_rag Method

```python
from hyperextract.methods import cog_rag

result = cog_rag.extract(
    text,
    task="Extract causal relationships"
)
```

## Method Selection Guide

### Quick Decision Tree

```
Is your task simple?
├── Yes → Use atom
└── No → Does it require reasoning?
    ├── Yes → Use cog_rag
    └── No → Do you need graphs?
        ├── Yes → graph_rag or hyper_rag
        └── No → Use light_rag
```

## Advanced Configuration

Each method supports custom configuration:

```python
result = graph_rag.extract(
    text,
    max_nodes=100,
    max_edges=200,
    temperature=0.0,
    confidence_threshold=0.8
)
```

## Next Steps

- Explore [Templates](templates.md)
- See [CLI Reference](../reference/cli-reference.md)
- Browse [Examples](../guides/index.md)
