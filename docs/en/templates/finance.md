# Finance Templates

Hyper-Extract provides specialized templates for financial document extraction.

## Available Templates

### Earnings Summary

Extract key financial metrics from earnings reports:

```yaml
language: en

name: Earnings Summary
type: model
tags: [finance]

description: 'Extract key financial metrics from earnings reports.'

output:
  fields:
  - name: company_name
    type: str
    description: 'Company name'
  - name: revenue
    type: str
    description: 'Revenue amount'
  - name: quarter
    type: str
    description: 'Quarter'

guideline:
  target: 'Extract key financial information.'
  rules:
    - 'Extract company name and financial data'
    - 'Use numbers from the source text'

display:
  label: '{company_name}'
```

### Risk Factors

Extract risk factors from financial documents:

```yaml
language: en

name: Risk Factor List
type: list
tags: [finance]

description: 'Extract risk factor list.'

output:
  fields:
  - name: category
    type: str
    description: 'Risk category'
  - name: description
    type: str
    description: 'Risk description'

guideline:
  target: 'Extract risk factors.'
  rules:
    - 'Extract all risk factors'
    - 'Each risk factor includes category and description'

display:
  label: '{category}'
```

### Ownership Graph

Extract ownership relationships:

```yaml
language: en

name: Ownership Graph
type: graph
tags: [finance]

description: 'Extract ownership relationships.'

output:
  entities:
    fields:
    - name: name
      type: str
      description: 'Entity name'
    - name: type
      type: str
      description: 'Entity type (company/person/organization)'
  relations:
    fields:
    - name: source
      type: str
      description: 'Owner'
    - name: target
      type: str
      description: 'Owned entity'
    - name: type
      type: str
      description: 'Relation type'

guideline:
  target: 'Extract ownership relationships.'
  rules_for_entities:
    - 'Extract companies and individuals'
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

### Event Timeline

Extract financial events and their temporal relationships:

```yaml
language: en

name: Event Timeline
type: temporal_graph
tags: [finance]

description: 'Extract financial events and their temporal relationships.'

output:
  entities:
    fields:
    - name: name
      type: str
      description: 'Event name'
    - name: type
      type: str
      description: 'Event type'
  relations:
    fields:
    - name: source
      type: str
      description: 'Source event'
    - name: target
      type: str
      description: 'Target event'
    - name: type
      type: str
      description: 'Relation type'
    - name: time
      type: str
      description: 'Time'
      required: false

guideline:
  target: 'Extract financial events and temporal relationships.'
  rules_for_entities:
    - 'Extract key financial events'
  rules_for_relations:
    - 'Extract temporal relationships between events'

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

## Usage Examples

### CLI

```bash
# Extract earnings summary
he parse earnings_report.pdf -t finance/earnings_summary -o output/

# Extract risk factors
he parse 10k_filing.txt -t finance/risk_factor_set -o output/

# Extract ownership relationships
he parse ownership.txt -t finance/ownership_graph -o output/
```

### Python API

```python
from hyperextract import Template

# Load finance template
ka = Template.create("finance/earnings_summary", "en")

# Extract from document
result = ka.parse(earnings_text)

# Access results
print(result.fields)
```

## Supported Document Types

- Annual reports
- Quarterly earnings
- 10-K/10-Q filings
- Equity research reports
- Financial news articles
- IPO prospectuses
- Supply chain analysis

## Next Steps

- [Legal Templates](legal.md)
- [Medicine Templates](medicine.md)

