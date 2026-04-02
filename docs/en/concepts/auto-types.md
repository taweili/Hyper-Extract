# AutoTypes

Hyper-Extract uses auto types to determine extraction patterns, supporting 8 types in total.

## Type Overview

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

## Selection Decision Tree

```
Need relationships?
├─ No → Record types
│   ├─ Single object → model
│   ├─ Ordered list → list
│   └─ Deduplicated set → set
└─ Yes → Graph types
    ├─ Binary relations (A→B) → graph
    └─ Multi-entity relations (A+B+C→D) → hypergraph

+ time dimension → temporal_graph
+ space dimension → spatial_graph
+ both → spatio_temporal_graph
```

## Detailed Usage

### Model

Used for extracting a single structured object.

```python
from hyperextract import Template

ka = Template.create("finance/earnings_summary", "en")
result = ka.parse(text)

print(result.fields["company_name"])
print(result.fields["revenue"])
```

### List

Used for extracting an ordered list.

```python
from hyperextract import Template

ka = Template.create("finance/risk_factor_set", "en")
result = ka.parse(text)

for item in result.fields:
    print(item)
```

### Set

Used for extracting a deduplicated set.

```python
from hyperextract import Template

ka = Template.create("general/entity_registry", "en")
result = ka.parse(text)

for entity in result.fields:
    print(entity)
```

### Graph

Used for extracting binary relations.

```python
from hyperextract import Template

ka = Template.create("finance/ownership_graph", "en")
result = ka.parse(text)

for entity in result.entities:
    print(f"{entity['name']} ({entity['type']})")

for relation in result.relations:
    print(f"{relation['source']} --[{relation['type']}]--> {relation['target']}")
```

### Hypergraph

Used for extracting multi-entity relations.

```python
from hyperextract import Template

ka = Template.create("tcm/formula_composition", "en")
result = ka.parse(text)

for relation in result.relations:
    print(f"Formula: {relation['formula_name']}")
    print(f"Herbs: {relation['herbs']}")
```

### Temporal Graph

Used for extracting temporal relations.

```python
from hyperextract import Template

ka = Template.create("finance/event_timeline", "en")
result = ka.parse(text)

for relation in result.relations:
    print(f"{relation['source']} --[{relation['type']}]--> {relation['target']} @ {relation['time']}")
```

## Next Steps

- Learn about [Templates](./templates.md)
- Browse [Preset Templates](./templates.md)
- Explore [Domain Templates](../guides/domain-templates/index.md)
