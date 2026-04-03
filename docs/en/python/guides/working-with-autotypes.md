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

# Access entities
for entity in result.data.entities:
    print(f"{entity.name} ({entity.type})")
    print(f"  Description: {entity.description}")

# Access relations
for relation in result.data.relations:
    print(f"{relation.source} --{relation.type}--> {relation.target}")
```

#### AutoHypergraph

Multi-entity relationship extraction.

```python
from hyperextract import Template

ka = Template.create("general/base_hypergraph", "en")
result = ka.parse(text)

# Hyperedges connect multiple entities
for hyperedge in result.data.hyperedges:
    print(f"Type: {hyperedge.type}")
    print(f"Entities: {hyperedge.entities}")
```

#### AutoTemporalGraph

Time-based graph extraction.

```python
from hyperextract import Template

ka = Template.create("general/base_temporal_graph", "en")
result = ka.parse(text)

# Relations include time information
for relation in result.data.relations:
    print(f"{relation.source} --{relation.type}--> {relation.target}")
    if hasattr(relation, 'time'):
        print(f"  Time: {relation.time}")
```

#### AutoSpatialGraph

Location-based graph extraction.

```python
from hyperextract import Template

ka = Template.create("general/base_spatial_graph", "en")
result = ka.parse(text)

# Entities/relation include location
for entity in result.data.entities:
    if hasattr(entity, 'location'):
        print(f"{entity.name} at {entity.location}")
```

#### AutoSpatioTemporalGraph

Combined time and space extraction.

```python
from hyperextract import Template

ka = Template.create("general/base_spatio_temporal_graph", "en")
result = ka.parse(text)

# Full context: who, what, when, where
for relation in result.data.relations:
    print(f"Event: {relation.type}")
    if hasattr(relation, 'time'):
        print(f"  When: {relation.time}")
    if hasattr(relation, 'location'):
        print(f"  Where: {relation.location}")
```

---

## Common Operations

### Checking if Empty

```python
if result.empty():
    print("No data extracted")
else:
    print(f"Extracted {len(result.data.entities)} entities")
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
entities = result.data.entities
relations = result.data.relations

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
# Iterate entities
for entity in result.data.entities:
    print(f"Name: {entity.name}")
    print(f"Type: {entity.type}")
    if hasattr(entity, 'description'):
        print(f"Description: {entity.description}")

# Iterate relations with filtering
for relation in result.data.relations:
    if relation.type == "worked_with":
        print(f"{relation.source} worked with {relation.target}")
```

### Filtering

```python
# Filter entities by type
people = [e for e in result.data.entities if e.type == "person"]
organizations = [e for e in result.data.entities if e.type == "organization"]

# Filter relations
inventions = [r for r in result.data.relations if "invent" in r.type.lower()]
```

### Statistics

```python
# Basic counts
entity_count = len(result.data.entities)
relation_count = len(result.data.relations)

# Type distribution
from collections import Counter
entity_types = Counter(e.type for e in result.data.entities)
relation_types = Counter(r.type for r in result.data.relations)

print(f"Entities: {entity_types}")
print(f"Relations: {relation_types}")
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
