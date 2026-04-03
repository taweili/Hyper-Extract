# Medicine Templates

Hyper-Extract provides specialized templates for medical document extraction.

## Available Templates

### Drug Interactions

Extract drug interaction information:

```yaml
language: en

name: Drug Interaction Graph
type: graph
tags: [medicine]

description: 'Extract drug interaction information.'

output:
  entities:
    fields:
    - name: name
      type: str
      description: 'Drug name'
    - name: type
      type: str
      description: 'Drug type'
  relations:
    fields:
    - name: source
      type: str
      description: 'Source drug'
    - name: target
      type: str
      description: 'Target drug'
    - name: type
      type: str
      description: 'Interaction type'

guideline:
  target: 'Extract drug interactions.'
  rules_for_entities:
    - 'Extract drug names'
  rules_for_relations:
    - 'Extract interactions between drugs'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name}'
  relation_label: '{type}'
```

### Treatment Plan

Extract treatment plan details:

```yaml
language: en

name: Treatment Plan Timeline
type: temporal_graph
tags: [medicine]

description: 'Extract treatment plan details.'

output:
  entities:
    fields:
    - name: name
      type: str
      description: 'Entity name'
    - name: type
      type: str
      description: 'Type (treatment/medication/procedure)'
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
    - name: time
      type: str
      description: 'Time'
      required: false

guideline:
  target: 'Extract treatment plan.'
  rules_for_entities:
    - 'Extract treatment plans and medications'
  rules_for_relations:
    - 'Extract treatment steps'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}|{time}'
  relation_members:
    source: source
    target: target
  time_field: time

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}@{time}'
```

### Anatomy Graph

Extract anatomy structure relationships:

```yaml
language: en

name: Anatomy Structure Graph
type: graph
tags: [medicine]

description: 'Extract anatomy structure relationships.'

output:
  entities:
    fields:
    - name: name
      type: str
      description: 'Anatomy structure name'
    - name: type
      type: str
      description: 'Structure type'
  relations:
    fields:
    - name: source
      type: str
      description: 'Source structure'
    - name: target
      type: str
      description: 'Target structure'
    - name: type
      type: str
      description: 'Relation type'

guideline:
  target: 'Extract anatomy structure relationships.'
  rules_for_entities:
    - 'Extract anatomy structures'
  rules_for_relations:
    - 'Extract relationships between structures'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name}'
  relation_label: '{type}'
```

## Usage Examples

### CLI

```bash
# Extract drug interactions
he parse clinical_note.txt -t medicine/drug_interaction -o output/

# Extract treatment plan
he parse discharge_summary.pdf -t medicine/treatment_map -o output/
```

### Python API

```python
from hyperextract import Template

# Load medicine template
ka = Template.create("medicine/drug_interaction", "en")

# Extract from document
result = ka.parse(clinical_text)

# Access results
print(result.entities)
```

## Supported Document Types

- Clinical guidelines
- Discharge summaries
- Package inserts
- Pathology reports
- Medical textbooks
- Clinical notes

## Next Steps

- [TCM Templates](tcm.md)
- [Finance Templates](finance.md)

