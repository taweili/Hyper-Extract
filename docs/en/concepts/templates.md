# Templates

Templates define WHAT to extract using declarative YAML. They provide a powerful way to specify extraction schemas without writing code.

## Template Structure

A template consists of:

1. **Metadata**: name, description, author
2. **Type**: The extraction type (Graph, List, Model, etc.)
3. **Schema**: Definition of nodes, edges, and fields

## Basic Example

```yaml
name: Event Timeline
description: Extract financial events and their temporal relations
type: TemporalGraph
schema:
  nodes:
    - type: Event
      properties:
        - name: description
          type: string
        - name: date
          type: string
  edges:
    - type: TIMELINE
      source: Event
      target: Event
      properties:
        - name: relation
          type: string
```

## Template Types

### Graph Templates

```yaml
type: Graph
schema:
  nodes:
    - type: Person
    - type: Organization
  edges:
    - type: WORKS_AT
      source: Person
      target: Organization
```

### List Templates

```yaml
type: List
schema:
  item:
    - name: ingredient
      type: string
    - name: quantity
      type: string
```

### Model Templates

```yaml
type: Model
schema:
  - name: product_name
    type: string
    required: true
  - name: price
    type: float
    required: true
```

## Property Types

| Type | Description | Example |
|------|-------------|---------|
| string | Text value | "Hello World" |
| integer | Whole number | 42 |
| float | Decimal number | 3.14 |
| boolean | True/False | true |
| date | Date value | 2024-01-15 |
| array | List of values | ["a", "b", "c"] |

## Advanced Features

### Validation Rules

```yaml
- name: email
  type: string
  pattern: "^[a-zA-Z0-9._%+-]+@[a-z]+.[a-z]{2,}$"
```

### Enumerations

```yaml
- name: status
  type: string
  enum: [pending, active, completed]
```

### Conditional Fields

```yaml
- name: end_date
  type: date
  required_if: type == "event"
```

## Preset Templates

Hyper-Extract includes 80+ preset templates across 6 domains:

### Finance
- `finance/earnings_summary`
- `finance/risk_factors`
- `finance/ownership_graph`

### Legal
- `legal/case_facts`
- `legal/contract_terms`
- `legal/compliance_requirements`

### Medicine
- `medicine/drug_interactions`
- `medicine/treatment_plan`
- `medicine/patient_history`

### TCM (Traditional Chinese Medicine)
- `tcm/herb_properties`
- `tcm/formula_composition`
- `tcm/syndrome_reasoning`

### Industry
- `industry/safety_controls`
- `industry/equipment_topology`
- `industry/operation_flow`

### General
- `general/biography`
- `general/concepts`
- `general/workflow`

## Using Templates

### CLI

```bash
he parse document.txt -t finance/earnings_summary
```

### Python API

```python
from hyperextract import Template

# Load preset
ka = Template.create("finance/earnings_summary")

# Load custom template
ka = Template.from_yaml("my_template.yaml")
```

## Next Steps

- Browse the [Template Gallery](../reference/template-gallery.md)
- Learn about [Domain Templates](../guides/domain-templates/index.md)
- Create your own templates
