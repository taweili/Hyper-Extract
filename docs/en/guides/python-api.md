# Python API

This guide covers using Hyper-Extract in your Python applications.

## Installation

```bash
pip install hyper-extract
```

## Basic Usage

### Import and Initialize

```python
from hyperextract import Template

# Load a preset template
ka = Template.create("general/biography")

# Parse document
result = ka.parse(text)
```

### Using Custom Templates

```python
from hyperextract import Template

# Load from YAML
ka = Template.from_yaml("template.yaml")

# Parse document
result = ka.parse(document_text)

# Access results
print(result.nodes)
print(result.edges)
```

## Auto-Types

### AutoModel

```python
from hyperextract import AutoModel
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
    occupation: str

extractor = AutoModel(schema=Person)
result = extractor.parse("John is a 30-year-old engineer.")
```

### AutoList

```python
from hyperextract import AutoList

extractor = AutoList(item_type="string")
result = extractor.parse("The ingredients are flour, sugar, and eggs.")
print(result.items)  # ["flour", "sugar", "eggs"]
```

### AutoGraph

```python
from hyperextract import AutoGraph

extractor = AutoGraph(
    node_types=["Person", "Organization"],
    edge_types=["WORKS_AT"]
)
result = extractor.parse("Alice works at Google.")
```

### AutoHypergraph

```python
from hyperextract import AutoHypergraph

extractor = AutoHypergraph()
result = extractor.parse("Alice, Bob, and Carol collaborated.")
```

## Extraction Methods

### Using atom

```python
from hyperextract.methods import atom

result = atom.extract(text, schema=MySchema)
```

### Using graph_rag

```python
from hyperextract.methods import graph_rag

result = graph_rag.extract(
    text,
    node_types=["Person", "Company"],
    edge_types=["WORKS_AT"]
)
```

### Using cog_rag

```python
from hyperextract.methods import cog_rag

result = cog_rag.extract(
    text,
    task="Extract causal relationships"
)
```

## Configuration

### LLM Configuration

```python
from hyperextract import Config

config = Config(
    llm_provider="openai",
    llm_model="gpt-4o",
    api_key="your-api-key"
)

ka = Template.create("general/biography", config=config)
```

### Embedding Configuration

```python
config = Config(
    embedding_provider="openai",
    embedding_model="text-embedding-3-small"
)
```

## Working with Results

### Accessing Nodes

```python
result = ka.parse(text)

for node in result.nodes:
    print(f"{node.type}: {node.properties}")
```

### Accessing Edges

```python
for edge in result.edges:
    print(f"{edge.source} --[{edge.type}]--> {edge.target}")
```

### Serialization

```python
# Save to JSON
result.to_json("output.json")

# Save to YAML
result.to_yaml("output.yaml")

# Load from file
loaded = Result.from_json("output.json")
```

## Advanced Usage

### Custom Parsers

```python
from hyperextract import Template
from hyperextract.parsers import CustomParser

class MyParser(CustomParser):
    def parse(self, text):
        # Custom parsing logic
        return processed_result

ka = Template(parser=MyParser())
```

### Batch Processing

```python
from hyperextract import Template

ka = Template.create("general/biography")

documents = ["doc1.txt", "doc2.txt", "doc3.txt"]
results = ka.batch_parse(documents)
```

## Next Steps

- Explore [CLI](cli.md)
- Browse [Domain Templates](domain-templates/index.md)
- Check [Reference](../reference/index.md)
