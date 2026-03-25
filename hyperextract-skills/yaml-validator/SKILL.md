---
name: hyper-extract-yaml-validator
description: |
  YAML Validator for Hyper-Extract. Validates configuration syntax and structure.
  Use optional after design to check for errors.
---

# YAML Validator

## Validation Workflow

1. **Syntax check**: YAML is valid
2. **Required fields**: All required fields present
3. **Type check**: Valid AutoType value
4. **Identifiers check**: Proper configuration for type
5. **Field validation**: Types and descriptions present

## Quick Validation Checklist

### All Types

```yaml
- [ ] language: zh/en
- [ ] name: PascalCase
- [ ] type: valid AutoType
- [ ] tags: lowercase array
- [ ] description: non-empty
- [ ] output: exists
- [ ] guideline: exists
```

### Graph Types

```yaml
- [ ] output.entities: exists
- [ ] output.relations: exists
- [ ] identifiers.entity_id: exists
- [ ] identifiers.relation_id: exists
- [ ] identifiers.relation_members: configured
```

### Hypergraph

```yaml
- [ ] relation_members is string OR list
- [ ] If list: all fields are type: list
```

### Temporal/Spatial

```yaml
- [ ] identifiers.time_field: configured (temporal)
- [ ] identifiers.location_field: configured (spatial)
```

## Validation Levels

| Level | Meaning | Action |
|-------|---------|--------|
| ERROR | Must fix | Won't work without fix |
| WARNING | Should fix | May affect quality |
| INFO | Reference | Recommended to follow |

## Reference Files

| Topic | Reference File |
|-------|---------------|
| Syntax validation | [rules-syntax.md](rules-syntax.md) |
| Type-specific rules | [rules-types.md](rules-types.md) |
| Identifier rules | [rules-identifiers.md](rules-identifiers.md) |
| Common errors | [patterns-errors.md](patterns-errors.md) |

## Error Message Format

```markdown
## Validation Results

### Syntax Validation
✅ PASSED

### Structure Validation
✅ PASSED
- language: ✅
- name: ✅
- type: ✅
- tags: ✅
- description: ✅
- output: ✅

### Semantic Validation
⚠️ 2 warnings
- WARNING: [message]
- WARNING: [message]

### Overall Assessment
✅ Configuration valid
```

---

See [patterns-errors.md](patterns-errors.md) for common error patterns and fixes.
