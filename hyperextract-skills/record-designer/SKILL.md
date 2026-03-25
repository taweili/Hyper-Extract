---
name: hyper-extract-record-designer
description: |
  Hyper-Extract Record Designer. Designs structure, identifiers, display, and extraction rules for model/list/set types.

  ## Applicable Types
  - model: Single object
  - list: Object list
  - set: Deduplicated set

  ## Complete Output
  - output.fields
  - guideline (target + rules)
  - identifiers.item_id (set only)
  - display.label
---

# Record Designer: model/list/set

## Type Confirmation

- **model**: Extract a single complete object
- **list**: Extract list of homogeneous objects
- **set**: Extract deduplicated set of objects

## Part 1: Field Design (output.fields)

### Field Definition Template

```yaml
output:
  description: 'Output structure description'
  fields:
    - name: field_name        # snake_case, must be unique
      type: str/int/float/list # data type
      description: 'What this field means'
      required: true/false     # is this mandatory?
      default: 'value'         # default when missing
```

### Field Type Guidelines

| Type | Use When | Example |
|------|----------|---------|
| str | Text values | names, descriptions |
| int | Whole numbers | counts, years |
| float | Decimal numbers | prices, percentages |
| list | Multiple values | tags, categories |

### Usually Needed Fields

- At minimum, most records need a `name` or `title` field

### Optional Fields

- description: Brief explanation
- category: Type or classification
- Domain-specific fields

## Part 2: Extraction Rules (guideline)

### Target Setting

```yaml
guideline:
  target: 'You are a [domain] expert. Extract [goal] from text.'
```

### Rules for Records

```yaml
  rules:
    - 'Rule 1: What to extract'
    - 'Rule 2: How to handle edge cases'
    - 'Rule 3: Quality standards'
```

### Rule Writing Guidelines

1. Be specific about what to extract
2. Include edge case handling
3. Set quality standards
4. Prioritize important rules first

## Part 3: Identifier Rules (identifiers)

### For set types, configure deduplication:

```yaml
identifiers:
  item_id: field_name  # Deduplicate based on this field
```

### For model/list types:

Usually not needed, or use empty:

```yaml
identifiers: {}
```

## Part 4: Display Configuration (display)

```yaml
display:
  label: '{field_name}'  # How to display each record
```

### Label Template Syntax

- `{field_name}`: Insert field value
- Example: `'{company_name}'` → "Acme Corp"

## Design Checklist

- [ ] All fields have clear semantic meaning?
- [ ] Field types are appropriate (str/int/float/list)?
- [ ] Required vs optional is reasonable?
- [ ] Default values are safe/meaningful?
- [ ] For set: item_id can uniquely identify records?
- [ ] Display label references correct fields?

## Complete Output Example

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

guideline:
  target: 'You are a financial analyst. Extract key metrics from earnings calls.'
  rules:
    - 'Extract revenue in the format shown in text (including currency)'
    - 'Use N/A if revenue is not mentioned'
    - 'Extract quarter as Q1/Q2/Q3/Q4 format'

display:
  label: '{company_name} - {quarter}'
```

## Next Steps

After record design:
1. Review with user
2. Optional: yaml-validator
3. Optional: multilingual
