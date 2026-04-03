# Python API

## Installation

```bash
pip install hyperextract
```

## Configuration

Set up your API key using dotenv:

```python
from dotenv import load_dotenv
load_dotenv()
```

Create a `.env` file:
```bash
OPENAI_API_KEY=your-api-key
```

## Quick Start

```python
from hyperextract import Template

ka = Template.create("general/biography_graph", "en")
result = ka.parse(document_text)
```

---

## AutoTypes

AutoTypes define the **output data structure** for knowledge extraction. There are 8 types:

### AutoModel - Structured Data

Extract structured summaries with AutoModel:

```python
from pydantic import BaseModel, Field
from hyperextract import AutoModel
from langchain_openai import ChatOpenAI

class BiographySummary(BaseModel):
    title: str = Field(description="Title of the biography")
    subject: str = Field(description="Main subject name")
    summary: str = Field(description="Brief summary")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

model = AutoModel(
    data_schema=BiographySummary,
    llm_client=llm,
)
model.feed_text(text)
print(model.data.title)
```

### AutoList - List Data

Extract lists of items:

```python
from hyperextract.types import AutoList

llm = ChatOpenAI(model="gpt-4o-mini")
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

lst = AutoList[str](
    item_schema=str,
    llm_client=llm,
    embedder=embedder,
)
lst.feed_text(text)
print(lst.items)  # List of extracted items
```

### AutoSet - Deduplicated List

Extract unique items (deduplicated):

```python
from hyperextract.types import AutoSet

s = AutoSet[str](
    item_schema=str,
    llm_client=llm,
    embedder=embedder,
)
s.feed_text(text)
print(s.items)  # Deduplicated list
```

### AutoGraph - Knowledge Graph

Extract entities and relationships:

```python
from pydantic import BaseModel, Field
from hyperextract.types import AutoGraph

class Entity(BaseModel):
    name: str = Field(description="Entity name")
    type: str = Field(description="Entity type")

class Relation(BaseModel):
    source: str = Field(description="Source entity")
    target: str = Field(description="Target entity")
    type: str = Field(description="Relation type")

graph = AutoGraph[Entity, Relation](
    node_schema=Entity,
    edge_schema=Relation,
    node_key_extractor=lambda x: x.name,
    edge_key_extractor=lambda x: f"{x.source}-{x.type}-{x.target}",
    llm_client=llm,
    embedder=embedder,
)
graph.feed_text(text)
print(f"Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}")
```

### AutoHypergraph - Hypergraph

For multi-entity relationships (n-ary relations):

```python
from hyperextract.types import AutoHypergraph
# See examples/en/autotypes/hypergraph_demo.py
```

### AutoTemporalGraph - Temporal Graph

For time-based relationships:

```python
from hyperextract.types import AutoTemporalGraph
# See examples/en/autotypes/temporal_graph_demo.py
```

### AutoSpatialGraph - Spatial Graph

For location-based relationships:

```python
from hyperextract.types import AutoSpatialGraph
# See examples/en/autotypes/spatial_graph_demo.py
```

### AutoSpatioTemporalGraph - Spatio-Temporal Graph

For both time and location:

```python
from hyperextract.types import AutoSpatioTemporalGraph
# See examples/en/autotypes/spatio_temporal_graph_demo.py
```

---

## Methods vs Templates

Hyper-Extract provides two ways to extract knowledge:

### Methods (Low-level)

Methods give you **full control** over the extraction process. Use them when you need:
- Custom extraction logic
- Specific algorithm tuning
- Advanced use cases

```python
from hyperextract.methods.typical import KG_Gen

ka = KG_Gen(llm_client=llm, embedder=embedder)
ka.feed_text(text)
result = ka.chat("What are the main achievements?")
```

Available Methods:
- **Typical**: KG_Gen, iText2KG, iText2KG*
- **RAG-Based**: GraphRAG, LightRAG, HyperRAG, HypergraphRAG, CogRAG

### Templates (High-level)

Templates are **pre-configured** schemas for common use cases. Use them when you want:
- Quick results
- Domain-specific extraction
- Zero-code setup

```python
from hyperextract import Template

ka = Template.create("finance/earnings_summary", "en")
result = ka.parse(text)
```

### When to Use Which?

| Scenario | Recommendation |
|----------|----------------|
| Quick prototyping | Templates |
| Domain-specific extraction | Templates |
| Custom extraction logic | Methods |
| Real-time interaction | Methods |
| Batch processing | Both work |

---

## Advanced Usage

### Batch Processing

```python
from hyperextract import Template

ka = Template.create("general/biography_graph", "en")
documents = ["doc1.txt", "doc2.txt", "doc3.txt"]

results = []
for doc in documents:
    with open(doc) as f:
        result = ka.parse(f.read())
        results.append(result)
```

### Incremental Supplement (feed)

```python
ka = Template.create("general/biography_graph", "en")
result = ka.parse(text1)

# Add more knowledge
ka.feed(result, text2)
```

### Knowledge Q&A (chat)

```python
ka.build_index()
answer = ka.chat("What are the key events?")
print(answer.content)
```

### Error Handling

```python
from hyperextract import Template

try:
    ka = Template.create("template_name", "en")
    result = ka.parse(text)
except Exception as e:
    print(f"Error: {e}")
    # Handle error
```

### Result Export

```python
# Export to JSON
json_output = result.to_json()

# Export to Dict
dict_output = result.to_dict()

# Export to Triples
triples = result.to_triples()
```

---

## Next Steps

- [Preset Templates](../templates/index.md)
- [Domain Templates](../templates/index.md)
- [Explore Examples](https://github.com/yifanfeng97/hyper-extract/tree/main/examples/en)
