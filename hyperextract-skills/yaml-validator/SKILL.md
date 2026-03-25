---
name: hyper-extract-yaml-validator
description: |
  Hyper-Extract YAML Validator. Checks configuration completeness, correctness, and best practices.

  ## Validation Levels
  - ERROR: Must fix, otherwise won't work
  - WARNING: Should fix, may affect quality
  - INFO: Reference info, recommended to follow
---

# YAML Validator

## Validation Checklist

### 1. Required Fields

- [ ] language
- [ ] name
- [ ] type (one of 8 valid types)
- [ ] tags
- [ ] description
- [ ] output
- [ ] guideline

### 2. Type-Specific Validation

#### Record Types

```yaml
output:
  description: '...'      # ✓ Exists
  fields:                 # ✓ Exists
    - name: ...           # ✓ Each field has name
      type: ...          # ✓ Has type
      description: ...   # ✓ Has description
```

#### Graph Types

```yaml
output:
  entities:               # ✓ Exists
    description: '...'
    fields:
      - name: name
      - name: category
  relations:              # ✓ Exists
    description: '...'
    fields:
      - name: source     # ✓ Binary relations
      - name: target     # ✓ OR
      - name: participants  # ✓ Hypergraph
```

#### Temporal Graph

```yaml
identifiers:
  time_field: '...'       # ✓ Must exist
```

#### Spatial Graph

```yaml
identifiers:
  location_field: '...'   # ✓ Must exist
```

### 3. Field Value Validation

| Field | Valid Values | Common Errors |
|-------|-------------|---------------|
| type | model, list, set, graph, hypergraph, temporal_graph, spatial_graph, spatio_temporal_graph | Typo: "graphh" |
| language | Single: zh/en; Multi: [zh, en] | Non-standard: "chinese" |
| extraction_mode | one_stage, two_stage | Typo: "two-stage" |

### 4. Naming Conventions

- [ ] name: PascalCase (e.g., EarningsCallSummary)
- [ ] tags: lowercase (e.g., [finance, medicine])
- [ ] field names: snake_case (e.g., company_name)
- [ ] relation_type: Usually Chinese (e.g., 拥有, 影响)

### 5. Identifiers Configuration

#### Binary Relations

```yaml
identifiers:
  entity_id: name              # ✓ References entity field
  relation_id: '{source}|...' # ✓ Template syntax correct
  relation_members:           # ✓ Map correctly
    source: source
    target: target
```

#### Hypergraph

```yaml
identifiers:
  entity_id: name
  relation_id: '{ruleType}|{action}'
  relation_members: participants  # ✓ STRING, not dict
```

#### Complex (relation_members as list)

```yaml
identifiers:
  entity_id: name
  relation_id: '{relation_type}'
  relation_members: [field1, field2]  # ✓ List of field names
```

## Error Messages

### Missing Required Field

```
ERROR: Missing required field 'output'
Fix: Add output field definition
```

### Invalid Type Value

```
ERROR: type value 'graphh' is not valid
Valid values: model, list, set, graph, hypergraph, temporal_graph, spatial_graph, spatio_temporal_graph
Fix: Correct to 'graph'
```

### Missing Identifiers

```
ERROR: graph type requires identifiers.relation_members
Fix: Add relation_members configuration
```

## Output Format

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
- WARNING: 'company_name' field description too brief
- WARNING: Missing options.extraction_mode, recommend 'two_stage'

### Best Practices
⚠️ 1 suggestion
- INFO: Consider adding identifiers for better deduplication

### Overall Assessment
✅ Configuration valid, ready for Hyper-Extract

## Fix Suggestions

1. Add extraction_mode: 'two_stage' to options
2. Expand 'company_name' description to be more specific
```
