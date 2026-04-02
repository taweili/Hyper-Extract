# Legal Templates

Hyper-Extract provides specialized templates for legal document extraction.

## Available Templates

### Case Facts

Extract facts from court judgments:

```yaml
language: en

name: Case Fact Timeline
type: temporal_graph
tags: [legal]

description: 'Extract case facts from court judgments.'

output:
  entities:
    fields:
    - name: name
      type: str
      description: 'Entity name'
    - name: type
      type: str
      description: 'Entity type (party/event/fact)'
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
  target: 'Extract case facts.'
  rules_for_entities:
    - 'Extract parties and events'
  rules_for_relations:
    - 'Extract fact relationships'

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

### Contract Terms

Extract contract obligations:

```yaml
language: en

name: Contract Terms List
type: list
tags: [legal]

description: 'Extract contract terms.'

output:
  fields:
  - name: clause_type
    type: str
    description: 'Clause type'
  - name: parties
    type: str
    description: 'Parties involved'
  - name: obligations
    type: str
    description: 'Obligation content'

guideline:
  target: 'Extract contract terms.'
  rules:
    - 'Extract all contract terms'
    - 'Each term includes type, parties, and obligations'

display:
  label: '{clause_type}'
```

### Compliance Requirements

Extract compliance requirements:

```yaml
language: en

name: Compliance Requirements List
type: list
tags: [legal]

description: 'Extract compliance requirements.'

output:
  fields:
  - name: regulation
    type: str
    description: 'Regulation name'
  - name: requirement
    type: str
    description: 'Compliance requirement'
  - name: deadline
    type: str
    description: 'Deadline'
    required: false

guideline:
  target: 'Extract compliance requirements.'
  rules:
    - 'Extract all compliance requirements'

display:
  label: '{regulation}'
```

### Case Citation

Extract case citation relationships:

```yaml
language: en

name: Case Citation Graph
type: graph
tags: [legal]

description: 'Extract case citation relationships.'

output:
  entities:
    fields:
    - name: name
      type: str
      description: 'Case name'
    - name: type
      type: str
      description: 'Case type'
  relations:
    fields:
    - name: source
      type: str
      description: 'Citing case'
    - name: target
      type: str
      description: 'Cited case'
    - name: type
      type: str
      description: 'Citation type'

guideline:
  target: 'Extract case citation relationships.'
  rules_for_entities:
    - 'Extract case names'
  rules_for_relations:
    - 'Extract citation relationships between cases'

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
# Extract case facts
he parse judgment.txt -t legal/case_fact_timeline -o output/

# Extract contract terms
he parse contract.pdf -t legal/contract_obligation -o output/

# Extract compliance requirements
he parse compliance.txt -t legal/compliance_list -o output/
```

### Python API

```python
from hyperextract import Template

# Load legal template
ka = Template.create("legal/case_fact_timeline", "en")

# Extract from document
result = ka.parse(judgment_text)

# Access results
print(result.entities)
```

## Supported Document Types

- Court judgments
- Legal contracts
- Compliance filings
- Legal treatises
- Regulatory documents

## Next Steps

- [Finance Templates](finance.md)
- [Medicine Templates](medicine.md)
- [Template Gallery](../../reference/template-gallery.md)
