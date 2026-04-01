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
name: Company News Summary
description: Extract key financial events from news articles
type: TemporalGraph
schema:
  nodes:
    - type: Company
      properties:
        - name: name
          type: string
        - name: ticker
          type: string
    - type: FinancialEvent
      properties:
        - name: description
          type: string
        - name: amount
          type: number
        - name: category
          type: string
  edges:
    - type: ANNOUNCED
      source: Company
      target: FinancialEvent
```

## Step 3: Extract Knowledge (CLI)

```bash
he parse document.txt -o output/ -t template.yaml
```

## Step 4: Extract Knowledge (Python API)

```python
from hyperextract import Template

# Create template from YAML
ka = Template.from_yaml("template.yaml")

# Parse document
result = ka.parse("Apple Inc. reported record quarterly revenue...")

# Access results
print(result.nodes)
print(result.edges)
```

## Step 5: View Results

The extracted knowledge will be saved in your output directory. You can use the search command:

```bash
he search output/ "What financial events were mentioned?"
```

## Next Steps

- Learn about the [8 Auto-Types](../concepts/auto-types.md)
- Explore [Extraction Methods](../concepts/methods.md)
- Browse [Preset Templates](../concepts/templates.md)
