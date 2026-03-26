# Type-Specific Validation Rules

Type-specific validation for YAML configurations. See [SKILL.md](SKILL.md) for workflow.

---

## Record Types (model/list/set)

```yaml
output:
  description: '...'      # ✓ Exists
  fields:                 # ✓ Exists
    - name: ...           # ✓ Each field has name
      type: ...          # ✓ Has type
      description: ...   # ✓ Has description
```

### model

- No identifiers needed
- Single output structure

### list

- No identifiers needed
- Ordered items

### set

- identifiers.item_id required
- Deduplication key

---

## Graph Types

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

### graph

- Binary relations (source/target)
- identifiers with {source, target}

### hypergraph

- Multi-entity relations
- identifiers.relation_members: string OR list

### temporal_graph

- identifiers.time_field required

### spatial_graph

- identifiers.location_field required

### spatio_temporal_graph

- Both time_field and location_field required

---

## Field Value Validation

| Field | Valid Values | Common Errors |
|-------|-------------|---------------|
| type | 8 valid types | Typo: "graphh" |
| language | zh/en or [zh, en] | Non-standard: "chinese" |
| extraction_mode | one_stage, two_stage | Typo: "two-stage" |
