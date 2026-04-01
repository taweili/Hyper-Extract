# Auto-Types

Hyper-Extract provides 8 auto-types for representing knowledge. Each type is optimized for specific extraction scenarios.

## Overview

| Type | Module | Description |
|------|--------|-------------|
| AutoModel | `hyperextract.types.model` | Pydantic model extraction |
| AutoList | `hyperextract.types.list` | List/collection extraction |
| AutoSet | `hyperextract.types.set` | Unique set extraction |
| AutoGraph | `hyperextract.types.graph` | Knowledge graph extraction |
| AutoHypergraph | `hyperextract.types.hypergraph` | Hypergraph extraction |
| AutoTemporalGraph | `hyperextract.types.temporal_graph` | Temporal knowledge graph |
| AutoSpatialGraph | `hyperextract.types.spatial_graph` | Spatial knowledge graph |
| AutoSpatioTemporalGraph | `hyperextract.types.spatio_temporal_graph` | Spatio-temporal graph |

## Usage Examples

### AutoModel

Extract structured data into Pydantic models:

```python
from hyperextract import AutoModel
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
    occupation: str

extractor = AutoModel(schema=Person)
result = extractor.parse("John Smith is a 35-year-old software engineer.")
```

### AutoList

Extract lists of items:

```python
from hyperextract import AutoList

extractor = AutoList(item_type="string")
result = extractor.parse("The ingredients are flour, sugar, eggs, and milk.")
# result: ["flour", "sugar", "eggs", "milk"]
```

### AutoGraph

Extract knowledge graphs:

```python
from hyperextract import AutoGraph

extractor = AutoGraph(node_types=["Person", "Company"], edge_types=["WORKS_AT"])
result = extractor.parse("Alice works at Google.")
# result: Graph with nodes and edges
```

### AutoHypergraph

Extract hypergraphs (edges connecting multiple nodes):

```python
from hyperextract import AutoHypergraph

extractor = AutoHypergraph()
result = extractor.parse("Alice, Bob, and Carol collaborated on Project X.")
```

### AutoTemporalGraph

Extract graphs with temporal information:

```python
from hyperextract import AutoTemporalGraph

extractor = AutoTemporalGraph()
result = extractor.parse("On Monday, Alice joined Google. On Tuesday, she started working.")
```

## Choosing the Right Type

### When to Use AutoModel
- Need structured, validated output
- Working with well-defined schemas
- Want Pydantic validation

### When to Use AutoList
- Extracting collections of items
- Order matters
- Simple item extraction

### When to Use AutoSet
- Need unique items only
- Don't care about order
- Deduplication required

### When to Use AutoGraph
- Complex relationships between entities
- Knowledge graphs
- Network analysis

### When to Use AutoHypergraph
- Many-to-many relationships
- Group entities together
- Complex network structures

### When to Use Temporal/Spatial Variants
- Time-aware: Use `AutoTemporalGraph`
- Location-aware: Use `AutoSpatialGraph`
- Both: Use `AutoSpatioTemporalGraph`

## Next Steps

- Learn about [Extraction Methods](methods.md)
- Explore [Templates](templates.md)
