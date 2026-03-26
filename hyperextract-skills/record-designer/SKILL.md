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

## Cases by Type

**Important**: Load only the case matching user's selected type.

| Type | Case File |
|------|-----------|
| model | [cases/earnings-summary.yaml](cases/earnings-summary.yaml) |
| list | [cases/product-features.yaml](cases/product-features.yaml) |
| set | [cases/entity-registry.yaml](cases/entity-registry.yaml) |

## Reference Files

**Important**: Check these files only when needed for the specific design task.

| Topic | When to Check |
|-------|--------------|
| [references/field.md](references/field.md) | When designing output.fields |
| [references/identifier.md](references/identifier.md) | For set type only |

## Design Checklist

- [ ] All fields have clear semantic meaning?
- [ ] Field types are appropriate (str/int/float/list)?
- [ ] Required vs optional is reasonable?
- [ ] Default values are safe/meaningful?
- [ ] For set: item_id can uniquely identify records?
- [ ] Display label references correct fields?
