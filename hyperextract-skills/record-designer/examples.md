# Record Type Examples

Complete YAML examples for record types. See [SKILL.md](SKILL.md) for workflow.

---

## Example 1: Earnings Call Summary (model)

```yaml
language: en
name: EarningsCallSummary
type: model
tags: [finance]
description: 'Extract key financial metrics from earnings call transcripts'

output:
  description: 'Earnings call summary'
  fields:
    - name: company_name
      type: str
      description: 'Company name'
      required: true
      default: ''
    - name: revenue
      type: str
      description: 'Revenue amount'
      required: false
      default: 'N/A'
    - name: quarter
      type: str
      description: 'Fiscal quarter'
      required: true
      default: ''
    - name: key_highlights
      type: list
      description: 'Key highlights from the call'
      required: false

guideline:
  target: 'You are a financial analyst. Extract key metrics from earnings calls.'
  rules:
    - 'Extract revenue in the format shown in text (including currency)'
    - 'Use N/A if revenue is not mentioned'
    - 'Extract quarter as Q1/Q2/Q3/Q4 format'

display:
  label: '{company_name} - {quarter}'
```

---

## Example 2: Product Features (list)

```yaml
language: en
name: ProductFeatures
type: list
tags: [product, features]
description: 'Extract product features'

output:
  description: 'Product feature list'
  fields:
    - name: order
      type: int
      description: 'Feature order'
    - name: feature
      type: str
      description: 'Feature name'
    - name: description
      type: str
      description: 'Feature description'
      required: false

guideline:
  target: 'You are a product analyst. Extract product features.'
  rules:
    - 'Extract features in order they appear'
    - 'Include brief description if available'

display:
  label: '{order}. {feature}'
```

---

## Example 3: Entity Registry (set)

```yaml
language: en
name: EntityRegistry
type: set
tags: [entity, registry]
description: 'Extract and deduplicate entity mentions'

output:
  description: 'Entity registry'
  fields:
    - name: name
      type: str
      description: 'Entity name'
    - name: category
      type: str
      description: 'Entity type'
    - name: source
      type: str
      description: 'Source document'
      required: false

guideline:
  target: 'You are a knowledge engineer. Extract entities and deduplicate.'
  rules:
    - 'Extract all mentioned entities'
    - 'Deduplicate by name'
    - 'Keep first occurrence of each entity'

identifiers:
  item_id: name

display:
  label: '{name} ({category})'
```

---

## Quick Reference

| Type | Example | Key Config |
|------|---------|------------|
| model | Earnings summary | No identifiers |
| list | Feature list | No identifiers, order field |
| set | Entity registry | item_id required |
