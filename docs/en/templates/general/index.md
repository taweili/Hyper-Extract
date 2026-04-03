# General Templates

Base types and common extraction tasks.

---

## Overview

General templates provide fundamental extraction capabilities suitable for a wide range of documents.

---

## Base Types

### base_model

**Purpose**: Basic structured data extraction

**Output**: Single structured object

**Use for**: Simple summaries, form-like data

**Example:**
```bash
he parse doc.md -t general/base_model -l en
```

**Output Schema**:
```python
{
    "field1": "value1",
    "field2": "value2"
}
```

---

### base_list

**Purpose**: Ordered collection extraction

**Output**: List of items

**Use for**: Sequences, rankings

**Example:**
```bash
he parse doc.md -t general/base_list -l en
```

**Output Schema**:
```python
{
    "items": ["item1", "item2", "item3"]
}
```

---

### base_set

**Purpose**: Unique collection extraction

**Output**: Set of unique items

**Use for**: Tags, categories, keywords

**Example:**
```bash
he parse doc.md -t general/base_set -l en
```

**Output Schema**:
```python
{
    "items": {"unique1", "unique2", "unique3"}
}
```

---

### base_graph

**Purpose**: Basic entity-relationship extraction

**Output**: Graph with entities and relations

**Use for**: Knowledge graphs, networks

**Example:**
```bash
he parse doc.md -t general/base_graph -l en
```

**Output Schema**:
```python
{
    "entities": [
        {"name": "Entity1", "type": "type1"},
        {"name": "Entity2", "type": "type2"}
    ],
    "relations": [
        {"source": "Entity1", "target": "Entity2", "type": "relates_to"}
    ]
}
```

---

## Specialized Templates

### biography_graph

**Type**: temporal_graph

**Purpose**: Extract person's life events and timeline

**Best for**: Biographies, profiles, memoirs

**Example Use:**
```bash
he parse tesla_bio.md -t general/biography_graph -l en
```

**Features**:
- Extracts people, places, events
- Captures temporal relationships
- Timeline visualization

**Example Output**:
```python
{
    "entities": [
        {"name": "Nikola Tesla", "type": "person"},
        {"name": "AC Motor", "type": "invention"}
    ],
    "relations": [
        {
            "source": "Nikola Tesla",
            "target": "AC Motor",
            "type": "invented",
            "time": "1888"
        }
    ]
}
```

---

### concept_graph

**Type**: graph

**Purpose**: Extract concepts and their relationships

**Best for**: Research papers, technical documents, articles

**Example Use:**
```bash
he parse paper.md -t general/concept_graph -l en
```

**Features**:
- Concept identification
- Relationship mapping
- Hierarchical structures

---

### doc_structure

**Type**: model

**Purpose**: Extract document structure and outline

**Best for**: Long documents, reports, books

**Example Use:**
```bash
he parse report.md -t general/doc_structure -l en
```

**Features**:
- Section identification
- Heading hierarchy
- Key points per section

---

### workflow_graph

**Type**: graph

**Purpose**: Extract process workflows

**Best for**: Procedures, processes, workflows

**Example Use:**
```bash
he parse procedure.md -t general/workflow_graph -l en
```

**Features**:
- Step identification
- Flow relationships
- Decision points

---

## When to Use General Templates

### Use When:
- Document doesn't fit specific domain
- Need basic extraction
- Exploring/document type unknown
- Building custom workflows

### Don't Use When:
- Domain-specific template available (use that instead)
- Need specialized fields (create custom template)

---

## Examples

### Example 1: Simple Summary

```python
from hyperextract import Template

ka = Template.create("general/base_model", "en")
result = ka.parse("""
Meeting Notes:
Date: January 15, 2024
Attendees: Alice, Bob, Carol
Topic: Q1 Planning
Decision: Launch product in March
""")

print(result.data)
```

### Example 2: Biography Analysis

```python
ka = Template.create("general/biography_graph", "en")
result = ka.parse(biography_text)

# Visualize life events
result.show()

# Ask questions
result.build_index()
response = result.chat("What were the major achievements?")
print(response.content)
```

### Example 3: Research Paper

```python
ka = Template.create("general/concept_graph", "en")
result = ka.parse(paper_text)

# Get concept map
for entity in result.data.entities:
    print(f"Concept: {entity.name}")

for relation in result.data.relations:
    print(f"{relation.source} → {relation.target}")
```

---

## See Also

- [Browse All Templates](../browse.md)
- [How to Choose](../how-to-choose.md)
- [Auto-Types](../../concepts/autotypes.md)
