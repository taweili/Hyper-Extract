# Quick Start

This tutorial will walk you through extracting knowledge from a document in under 5 minutes.

## Step 1: Prepare Your Document

Let's start with a simple text document. Create a file called `document.txt`:

```text
Apple Inc. reported record quarterly revenue of $123.9 billion in Q1 2024.
CEO Tim Cook announced the company's strongest-ever iPhone sales.
The board declared a cash dividend of $0.24 per share.
Services revenue reached an all-time high of $22.3 billion.
```

## Step 2: Create an Extraction Template

Hyper-Extract uses YAML templates to define what to extract. Create `template.yaml`:

```yaml
language: en

name: Company News Summary
type: graph
tags: [finance]

description: 'Extract key financial events and entity relationships from news articles.'

output:
  entities:
    fields:
    - name: name
      type: str
      description: 'Entity name'
    - name: type
      type: str
      description: 'Entity type (company/person/event/amount)'
  relations:
    fields:
    - name: source
      type: str
      description: 'Source entity'
    - name: target
      type: str
      description: 'Target entity'
    - name: type
      type: str
      description: 'Relation type'

guideline:
  target: 'Extract entities and relationships from news articles.'
  rules_for_entities:
    - 'Extract companies, persons, amounts, etc.'
    - 'Maintain consistent naming'
  rules_for_relations:
    - 'Create relations only when explicitly expressed'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}'
```

## Step 3: Extract Knowledge (CLI)

![CLI](../assets/cli.png)

```bash
he parse document.txt -o output/ -t template.yaml
```

## Step 4: Extract Knowledge (Python API)

```python
from hyperextract import Template

# Create template from YAML
ka = Template.create("template.yaml", "en")

# Parse document
result = ka.parse("Apple Inc. reported record quarterly revenue...")

# Access results
print(result.entities)
print(result.relations)
```

## Step 5: View Results

The extracted knowledge will be saved in your output directory. You can use the search command:

```bash
he search output/ "What financial events were mentioned?"
```

**AutoGraph Visualization Example:**

![AutoGraph Visualization](../assets/en_show.png)

## Next Steps

- Learn about the [8 Auto-Types](../concepts/auto-types.md)
- Explore [Extraction Methods](../concepts/methods.md)
- Browse [Preset Templates](../concepts/templates.md)
