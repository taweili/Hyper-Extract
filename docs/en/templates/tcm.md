# TCM Templates

Hyper-Extract provides specialized templates for Traditional Chinese Medicine (TCM) document extraction.

## Available Templates

### Herb Properties

Extract properties of medicinal herbs:

```yaml
language: en

name: Herb Properties
type: model
tags: [tcm]

description: 'Extract herb property information.'

output:
  fields:
  - name: herb_name
    type: str
    description: 'Herb name'
  - name: properties
    type: str
    description: 'Properties'
  - name: channels
    type: str
    description: 'Meridian channels'
  - name: indications
    type: str
    description: 'Indications'

guideline:
  target: 'Extract herb properties.'
  rules:
    - 'Extract herb name and properties'
    - 'Keep original expressions'

display:
  label: '{herb_name}'
```

### Formula Composition

Extract herbal formula composition:

```yaml
language: en

name: Formula Composition List
type: list
tags: [tcm]

description: 'Extract formula composition.'

output:
  fields:
  - name: herb_name
    type: str
    description: 'Herb name'
  - name: dosage
    type: str
    description: 'Dosage'
  - name: role
    type: str
    description: 'Role (jun/chen/zuo/shi)'
    required: false

guideline:
  target: 'Extract formula composition.'
  rules:
    - 'Extract all herbs in the formula'
    - 'Record dosage and role'

display:
  label: '{herb_name}'
```

### Meridian Graph

Extract meridian relationships:

```yaml
language: en

name: Meridian Relationship Graph
type: graph
tags: [tcm]

description: 'Extract meridian relationships.'

output:
  entities:
    fields:
    - name: name
      type: str
      description: 'Entity name (herb/meridian)'
    - name: type
      type: str
      description: 'Type'
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
  target: 'Extract meridian relationships.'
  rules_for_entities:
    - 'Extract herbs and meridians'
  rules_for_relations:
    - 'Extract relationships of herbs entering meridians'

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

### Syndrome Reasoning

Extract syndrome diagnosis and reasoning:

```yaml
language: en

name: Syndrome Reasoning Hypergraph
type: hypergraph
tags: [tcm]

description: 'Extract syndrome diagnosis and reasoning.'

output:
  entities:
    fields:
    - name: name
      type: str
      description: 'Entity name'
    - name: type
      type: str
      description: 'Type (syndrome/symptom/treatment)'
  relations:
    fields:
    - name: syndrome
      type: str
      description: 'Syndrome name'
    - name: symptoms
      type: list
      description: 'Related symptoms'
    - name: treatment
      type: str
      description: 'Treatment method'
      required: false

guideline:
  target: 'Extract syndrome diagnosis and reasoning.'
  rules_for_entities:
    - 'Extract syndromes and symptoms'
  rules_for_relations:
    - 'Extract relationships between syndrome and symptoms/treatment'

identifiers:
  entity_id: name
  relation_id: '{syndrome}'
  relation_members: symptoms

display:
  entity_label: '{name}'
  relation_label: '{syndrome}'
```

## Usage Examples

### CLI

```bash
# Extract herb properties
he parse herbal_compendium.txt -t tcm/herb_property -o output/

# Extract formula composition
he parse prescription.txt -t tcm/formula_composition -o output/

# Extract meridian relationships
he parse meridian.txt -t tcm/meridian_graph -o output/
```

### Python API

```python
from hyperextract import Template

# Load TCM template
ka = Template.create("tcm/herb_property", "en")

# Extract from document
result = ka.parse(herbal_text)

# Access results
print(result.fields)
```

## Supported Document Types

- Herbal compendiums
- Prescription forms
- Medical case records
- Meridian treatises
- Formula pharmacopoeias

## Next Steps

- [Medicine Templates](medicine.md)
- [Finance Templates](finance.md)

