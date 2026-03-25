---
name: hyper-extract-record-designer
description: |
  Record Type Designer for Hyper-Extract. Generates YAML for model/list/set types.
  Use after brainstorm with design draft.
---

# Record Designer: model/list/set

## Input from Brainstorm

Receive design specs from brainstorm:
- What fields to extract
- Field types and requirements
- Deduplication needs (for set)

## Workflow

1. **Confirm type** (model/list/set)
2. **Design fields** (output.fields)
3. **Configure identifiers** (identifiers.item_id for set)
4. **Set display** (display.label)
5. **Write guideline** (guideline)
6. **Review and output YAML**

## Type Confirmation

| Type | Identifiers | Use Case |
|------|-------------|----------|
| model | Not needed | Single object |
| list | Not needed | Ordered items |
| set | `item_id` required | Deduplicated entities |

## Output Template

```yaml
language: en

name: [TemplateName]
type: [model/list/set]
tags: [...]
description: '...'

output:
  description: '...'
  fields:
    - name: field_name
      type: str/int/float/list
      description: '...'
      required: true/false
      default: '...'

guideline:
  target: 'You are a [domain] expert...'
  rules: [...]

identifiers: {}  # Or item_id for set

display:
  label: '{field_name}'
```

## Type-Specific Output

### model

```yaml
type: model
identifiers: {}  # Not needed
```

### list

```yaml
type: list
identifiers: {}  # Not needed
```

### set

```yaml
type: set
identifiers:
  item_id: [deduplication field]
```

## Reference Files

| Topic | Reference File |
|-------|---------------|
| Field design patterns | [reference-field.md](reference-field.md) |
| Identifier configuration | [reference-identifier.md](reference-identifier.md) |
| Complete examples | [examples.md](examples.md) |

## Design Checklist

- [ ] All fields have clear semantic meaning?
- [ ] Field types are appropriate (str/int/float/list)?
- [ ] Required vs optional is reasonable?
- [ ] Default values are safe/meaningful?
- [ ] For set: item_id can uniquely identify records?
- [ ] Display label references correct fields?

---

See [examples.md](examples.md) for complete YAML examples.
