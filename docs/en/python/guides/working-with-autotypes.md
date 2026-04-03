# Working with Auto-Types

Extract, manipulate, and utilize structured knowledge data.

---

## What Are Auto-Types?

Auto-Types are intelligent data structures that automatically extract and organize knowledge from text. They provide:

- **Type-safe schemas** — Pydantic-based validation
- **LLM-powered extraction** — Automatic content processing
- **Built-in operations** — Search, merge, visualize
- **Serialization** — Save/load to disk

---

## The 8 Auto-Types

### Scalar Types

#### AutoModel

Single structured object extraction.

```python
from hyperextract import Template

ka = Template.create("finance/earnings_summary", "en")
result = ka.parse(report_text)

# Access fields directly
print(result.data.company_name)
print(result.data.revenue)
print(result.data.eps)
```

#### AutoList

Ordered collection extraction.

```python
from hyperextract import Template

ka = Template.create("general/base_list", "en")
result = ka.parse(text)

# Iterate over items
for item in result.data.items:
    print(item)

# Access by index
first = result.data.items[0]
```

#### AutoSet

Deduplicated collection extraction.

```python
from hyperextract import Template

ka = Template.create("general/base_set", "en")
result = ka.parse(text)

# Items are unique
for item in result.data.items:
    print(item)
```

### Graph Types

#### AutoGraph

Entity-relationship graph extraction.

```python
from hyperextract import Template

ka = Template.create("general/knowledge_graph", "en")
result = ka.parse(text)

# Access nodes
for node in result.data.nodes:
    print(f"{node.name} ({node.type})")
    print(f"  Description: {node.description}")

# Access edges
for edge in result.data.edges:
    print(f"{edge.source} --{edge.type}--> {edge.target}")
```

#### AutoHypergraph

Multi-entity relationship extraction.

```python
from hyperextract import Template

ka = Template.create("general/base_hypergraph", "en")
result = ka.parse(text)

# Hyperedges connect multiple entities
for edge in result.data.edges:
    print(f"Type: {edge.type}")
    print(f"Entities: {edge.entities}")
```

#### AutoTemporalGraph

Time-based graph extraction.

```python
from hyperextract import Template

ka = Template.create("general/base_temporal_graph", "en")
result = ka.parse(text)

# Relations include time information
for edge in result.data.edges:
    print(f"{edge.source} --{edge.type}--> {edge.target}")
    if hasattr(edge, 'time'):
        print(f"  Time: {edge.time}")
```

#### AutoSpatialGraph

Location-based graph extraction.

```python
from hyperextract import Template

ka = Template.create("general/base_spatial_graph", "en")
result = ka.parse(text)

# Nodes/edges include location
for node in result.data.nodes:
    if hasattr(node, 'location'):
        print(f"{node.name} at {node.location}")
```

#### AutoSpatioTemporalGraph

Combined time and space extraction.

```python
from hyperextract import Template

ka = Template.create("general/base_spatio_temporal_graph", "en")
result = ka.parse(text)

# Full context: who, what, when, where
for edge in result.data.edges:
    print(f"Event: {edge.type}")
    if hasattr(edge, 'time'):
        print(f"  When: {edge.time}")
    if hasattr(edge, 'location'):
        print(f"  Where: {edge.location}")
```

---

## Common Operations

### Checking if Empty

```python
if result.empty():
    print("No data extracted")
else:
    print(f"Extracted {len(result.data.nodes)} nodes")
```

### Clearing Data

```python
# Clear all data
result.clear()

# Clear only index
result.clear_index()
```

### Merging Instances

```python
# Two separate extractions
result1 = ka.parse(text1)
result2 = ka.parse(text2)

# Merge into new instance
combined = result1 + result2
```

---

## Accessing Data

### Property Access

```python
result = ka.parse(text)

# Direct property access (Pydantic model)
nodes = result.data.nodes
edges = result.data.edges

# Dictionary conversion
data_dict = result.data.model_dump()
```

### JSON Export

```python
import json

# Export to JSON
json_data = result.data.model_dump_json(indent=2)

# Save to file
with open("output.json", "w") as f:
    f.write(json_data)
```

---

## Working with Results

### Iteration Patterns

```python
# Iterate nodes
for node in result.data.nodes:
    print(f"Name: {node.name}")
    print(f"Type: {node.type}")
    if hasattr(node, 'description'):
        print(f"Description: {node.description}")

# Iterate edges with filtering
for edge in result.data.edges:
    if edge.type == "worked_with":
        print(f"{edge.source} worked with {edge.target}")
```

### Filtering

```python
# Filter nodes by type
people = [n for n in result.data.nodes if n.type == "person"]
organizations = [n for n in result.data.nodes if n.type == "organization"]

# Filter edges
inventions = [e for e in result.data.edges if "invent" in e.type.lower()]
```

### Statistics

```python
# Basic counts
node_count = len(result.data.nodes)
edge_count = len(result.data.edges)

# Type distribution
from collections import Counter
node_types = Counter(n.type for n in result.data.nodes)
edge_types = Counter(e.type for e in result.data.edges)

print(f"Nodes: {node_types}")
print(f"Edges: {edge_types}")
```

---

## Advanced Usage

### Custom Schema Access

```python
# Access the schema
schema = result.data_schema

print(schema.model_fields)  # Available fields
```

### Raw Data Access

```python
# Access internal data if needed
internal_data = result._data
```

### Type Checking

```python
from hyperextract import AutoGraph, AutoList

# Check instance type
if isinstance(result, AutoGraph):
    print("Graph extraction")
elif isinstance(result, AutoList):
    print("List extraction")
```

---

## Best Practices

1. **Check hasattr before optional fields** — Schema fields may vary
2. **Handle empty results** — Always check `empty()`
3. **Use model_dump for serialization** — Proper JSON conversion
4. **Leverage type hints** — IDE support for autocomplete

---

## See Also

- [Search and Chat](search-and-chat.md)
- [Saving and Loading](saving-loading.md)
- [Auto-Types Reference](../../concepts/autotypes.md)
