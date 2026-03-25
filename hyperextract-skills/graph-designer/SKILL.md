---
name: hyper-extract-graph-designer
description: |
  Graph Type Designer for Hyper-Extract. Generates YAML for graph/hypergraph types.
  Use after brainstorm with design draft.
---

# Graph Designer: graph/hypergraph/temporal/spatial

## Input from Brainstorm

Receive design specs from brainstorm:
- Entity types and fields
- Relation types and fields
- Hypergraph grouping strategy
- Time/location requirements

## Workflow

1. **Confirm type** based on brainstorm specs
2. **Design entities** (output.entities)
3. **Design relations** (output.relations)
4. **Configure identifiers** (identifiers)
5. **Set display** (display)
6. **Write guideline** (guideline)
7. **Review and output YAML**

## Type Confirmation

| Type | relation_members | Additional Config |
|------|-----------------|-------------------|
| graph | `{source, target}` | - |
| hypergraph (simple) | `participants` (string) | - |
| hypergraph (nested) | `[group_a, group_b]` (list) | - |
| temporal_graph | + type | `time_field` |
| spatial_graph | + type | `location_field` |
| spatio_temporal | + both | `time_field` + `location_field` |

## Output Template

```yaml
language: en

name: [TemplateName]
type: [type]
tags: [...]
description: '...'

output:
  entities:
    description: '...'
    fields:
      - name: name
        type: str
      - name: category
        type: str
  relations:
    description: '...'
    fields:
      # Type-specific fields

guideline:
  target: 'You are a [domain] expert...'
  rules_for_entities: [...]
  rules_for_relations: [...]

identifiers:
  entity_id: name
  relation_id: '...'
  relation_members: ...

display:
  entity_label: '{name} ({category})'
  relation_label: '...'
```

## Quick Config Reference

### Binary Relations (graph)

```yaml
identifiers:
  relation_members:
    source: source
    target: target
```

### Hypergraph Simple

```yaml
identifiers:
  relation_members: participants  # STRING
```

### Hypergraph Nested

```yaml
identifiers:
  relation_members: [group_a, group_b]  # LIST
```

### Temporal

```yaml
identifiers:
  time_field: event_date
```

### Spatial

```yaml
identifiers:
  location_field: location
```

## Reference Files

| Topic | Reference File |
|-------|---------------|
| Entity design patterns | [reference-entity.md](reference-entity.md) |
| Relation design patterns | [reference-relation.md](reference-relation.md) |
| Hypergraph design | [reference-hypergraph.md](reference-hypergraph.md) |
| Dimension design | [reference-dimensions.md](reference-dimensions.md) |
| Complete examples | [examples.md](examples.md) |

---

## Design Checklist

### Entities
- [ ] Entity types cover key concepts?
- [ ] Entity granularity appropriate?
- [ ] Multi-type nodes handled?
- [ ] No redundant fields?

### Relations
- [ ] Relation types semantically clear?
- [ ] source/target reference entities?
- [ ] No ambiguous relations?

### Hypergraph
- [ ] Participant count reasonable?
- [ ] Grouping strategy clear?
- [ ] Outcome defined?

### Identifiers
- [ ] entity_id references name field?
- [ ] relation_id template correct?
- [ ] relation_members configured?
- [ ] time/location_field specified?

---

See [examples.md](examples.md) for complete YAML examples.
