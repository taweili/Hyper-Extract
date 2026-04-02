# Python API

Hyper-Extract provides a Python API for programmatic extraction.

## Installation

```bash
pip install hyperextract
```

## Basic Usage

### Load Preset Template

```python
from hyperextract import Template

# Load preset template
ka = Template.create("general/graph", "en")

# Parse document
result = ka.parse(document_text)

# Access results
print(result.entities)
print(result.relations)
```

### Load Custom Template

```python
from hyperextract import Template

# Load from YAML file
ka = Template.create("template.yaml", "en")

# Load from string
yaml_content = """
language: en
name: Custom Template
type: graph
tags: [custom]
description: '...'
output:
  entities:
    fields:
    - name: name
      type: str
      description: 'Name'
  relations:
    fields:
    - name: source
      type: str
      description: 'Source'
    - name: target
      type: str
      description: 'Target'
    - name: type
      type: str
      description: 'Type'
guideline:
  target: '...'
identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target
"""

ka = Template.create(yaml_content, "en")
```

### Batch Processing

```python
from hyperextract import Template

ka = Template.create("general/graph", "en")

documents = ["Document 1 content...", "Document 2 content...", "Document 3 content..."]

results = []
for doc in documents:
    result = ka.parse(doc)
    results.append(result)
```

### Export Results

```python
from hyperextract import Template

ka = Template.create("general/graph", "en")
result = ka.parse(document_text)

# Export to JSON
json_output = result.to_json()

# Export to Dict
dict_output = result.to_dict()

# Export to triples
triples = result.to_triples()
```

## Template Creation

### Create New Template

```python
from hyperextract import Template

template = Template.create("template.yaml", "en")
```

### Save Template

```python
from hyperextract import Template

ka = Template.create("general/graph", "en")
ka.save("my_template.yaml")
```

## Configuration Options

### Set Language

```python
from hyperextract import Template

# Single language
ka = Template.create("general/graph", "en")

# Multiple languages
ka = Template.create("general/graph", ["zh", "en"])
```

### Set Model

```python
from hyperextract import Template

# Use specified model
ka = Template.create("general/graph", "en", model="gpt-4")

# Use local model
ka = Template.create("general/graph", "en", model="local-model")
```

## Error Handling

```python
from hyperextract import Template

try:
    ka = Template.create("template.yaml", "en")
    result = ka.parse(document_text)
except Exception as e:
    print(f"Extraction failed: {e}")
```

## Next Steps

- Browse [Preset Templates](../concepts/templates.md)
- Explore [Domain Templates](./domain-templates/index.md)
