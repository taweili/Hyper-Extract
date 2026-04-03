# AutoTypes

AutoTypes define the **output data structure** for knowledge extraction. There are 8 types:

## Record Types

### AutoModel

Structured data extraction with Pydantic models.

```python
from pydantic import BaseModel, Field
from hyperextract import AutoModel

class Summary(BaseModel):
    title: str = Field(description="Title")
    summary: str = Field(description="Summary")

model = AutoModel(data_schema=Summary, llm_client=llm)
```

### AutoList

Extract lists of items.

```python
from hyperextract.types import AutoList

lst = AutoList[str](item_schema=str, llm_client=llm)
lst.feed_text(text)
```

### AutoSet

Extract unique items (deduplicated).

```python
from hyperextract.types import AutoSet

s = AutoSet[str](item_schema=str, llm_client=llm)
s.feed_text(text)
```

## Graph Types

### AutoGraph

Entity-relationship extraction.

```python
from hyperextract.types import AutoGraph

graph = AutoGraph(node_schema=Entity, edge_schema=Relation, llm_client=llm)
graph.feed_text(text)
```

### AutoHypergraph

Multi-entity relationships (n-ary relations).

```python
from hyperextract.types import AutoHypergraph
```

### AutoTemporalGraph

Time-based relationships.

```python
from hyperextract.types import AutoTemporalGraph
```

### AutoSpatialGraph

Location-based relationships.

```python
from hyperextract.types import AutoSpatialGraph
```

### AutoSpatioTemporalGraph

Both time and location.

```python
from hyperextract.types import AutoSpatioTemporalGraph
```

## Quick Links

- [Domain Templates](../templates/index.md) - Ready-to-use templates
