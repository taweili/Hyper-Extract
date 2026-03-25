---
name: hyper-extract-graph-designer
description: |
  Hyper-Extract Graph Designer. Designs structure, identifiers, display, and extraction rules for graph/hypergraph/temporal/spatial types.

  ## Applicable Types
  - graph: Binary relations
  - hypergraph: Multi-entity relations
  - temporal_graph: + time dimension
  - spatial_graph: + space dimension
  - spatio_temporal_graph: + time + space

  ## Complete Output
  - output.entities
  - output.relations
  - guideline
  - identifiers
  - display
---

# Graph Designer: graph/hypergraph/temporal/spatial

## Type Confirmation

- **graph**: Simple binary relations (A→B)
- **hypergraph**: Multi-party relations (A+B+C→D)
- **temporal_graph**: Binary relations + time
- **spatial_graph**: Binary relations + space
- **spatio_temporal_graph**: Binary relations + time + space

## Part 1: Entity Design (output.entities)

### Standard Entity Fields

```yaml
entities:
  description: 'Node/entity definitions'
  fields:
    - name: name
      type: str
      description: 'Entity name (unique identifier)'
    - name: category
      type: str
      description: 'Entity type/category'
    - name: description
      type: str
      description: 'Brief description'
      required: false
      default: ''
```

### Multi-Type Node Considerations

If nodes can have multiple categories:

```yaml
    - name: category
      type: list
      description: 'Entity types (can be multiple)'
```

### Domain-Specific Fields

Add fields based on your domain:

```yaml
    - name: role
      type: str
      description: 'Role in current context'
      required: false
      default: ''
```

## Part 2: Relation Design (output.relations)

### For graph/temporal/spatial (Binary Relations)

```yaml
relations:
  description: 'Edge/relation definitions'
  fields:
    - name: source
      type: str
      description: 'Source entity name'
    - name: target
      type: str
      description: 'Target entity name'
    - name: relation_type
      type: str
      description: 'Type of relationship'
```

### Predefined Relation Types

Common types (can be customized):

| Category | Relation Types |
|----------|---------------|
| Social | owns, works_for, married_to, parent_of |
| Organizational | subsidiary_of, competitor_of, partner_with |
| Causal | causes, enables, prevents, leads_to |
| Spatial | located_at, adjacent_to, part_of |
| Temporal | preceded_by, followed_by, concurrent_with |

### For hypergraph (Multi-Entity Relations)

```yaml
relations:
  description: 'Hyperedge definitions'
  fields:
    - name: relation_type
      type: str
      description: 'Type of relationship'
    - name: participants
      type: list
      description: 'List of participating entity names'
    - name: outcome
      type: str
      description: 'Result or conclusion'
    - name: reasoning
      type: str
      description: 'Explanation or evidence'
      required: false
      default: ''
```

### For temporal_graph (Add time field on edges)

```yaml
    - name: event_date
      type: str
      description: 'When the relation occurred'
      required: false
      default: ''
```

### For spatial_graph (Add location field on edges)

```yaml
    - name: location
      type: str
      description: 'Where the relation occurred'
      required: false
      default: ''
```

## Part 3: Extraction Rules (guideline)

### Target Setting

```yaml
guideline:
  target: 'You are a [domain] expert. Extract knowledge graph from text.'
```

### Entity Extraction Rules

```yaml
  rules_for_entities:
    - 'Entity names must match exactly with text'
    - 'Each entity must have a clear category'
    - 'Only extract entities explicitly mentioned'
```

### Relation Extraction Rules

```yaml
  rules_for_relations:
    - 'Only create edges for explicitly stated relations'
    - 'source and target must reference extracted entities'
    - 'Use predefined relation types when possible'
```

### For temporal_graph (Time handling rules)

```yaml
  rules_for_time:
    - 'Observation time: {observation_time}'
    - 'Absolute dates: Keep as-is (e.g., 2024-01-01)'
    - 'Relative time: Convert to absolute (last year → previous year from observation)'
    - 'Fuzzy time: Leave empty, do not guess'
```

### For spatial_graph (Location handling rules)

```yaml
  rules_for_location:
    - 'Observation location: {observation_location}'
    - 'Structured locations: Keep as-is (e.g., Beijing, China)'
    - 'Fuzzy locations: Use observation_location (here → observation)'
    - 'Coordinates: Keep as-is'
```

## Part 4: Identifier Rules (identifiers)

### For binary relations (graph/temporal/spatial)

```yaml
identifiers:
  entity_id: name
  relation_id: '{source}|{relation_type}|{target}'
  relation_members:
    source: source
    target: target
```

### For hypergraph

The `relation_members` is a **string** pointing to the participants field name (type: list).

```yaml
identifiers:
  entity_id: name
  relation_id: '{ruleType}|{action}'
  relation_members: participants  # STRING, points to list field
```

### For complex cases (relation_members as list)

When a relation involves multiple sources of participants:

```yaml
identifiers:
  entity_id: name
  relation_id: '{relation_type}'
  relation_members: [source_participants, target_participants]
```

The system will unpack the lists and use the combined set as members.

### For temporal_graph (Add time identifier)

```yaml
  time_field: event_date
```

### For spatial_graph (Add location identifier)

```yaml
  location_field: location
```

### Identifier Template Syntax

- `{field_name}`: Insert field value
- `{source}`: Source entity name
- `{relation_type}`: Relation type
- `{target}`: Target entity name

## Part 5: Display Configuration (display)

### For binary relations

```yaml
display:
  entity_label: '{name} ({category})'
  relation_label: '{relation_type}'
```

### For hypergraph

```yaml
display:
  entity_label: '{name} ({category})'
  relation_label: '[{ruleType}] {outcome}'
```

## Design Checklist

### Entities
- [ ] Entity types cover key concepts?
- [ ] Entity granularity appropriate?
- [ ] Multi-type nodes handled correctly?
- [ ] No redundant fields?

### Relations
- [ ] Relation types semantically clear?
- [ ] source/target reference defined entities?
- [ ] No ambiguous relations?

### Hypergraph Specific
- [ ] Participant count reasonable?
- [ ] Outcome clearly defined?
- [ ] Reasoning/evidence needed?

### Identifiers
- [ ] entity_id references name field?
- [ ] relation_id template correct?
- [ ] relation_members configured correctly (string for hypergraph)?
- [ ] time_field/location_field specified for temporal/spatial?

## Complete Output Example

```yaml
language: en

name: CompanyRelationshipGraph
type: graph
tags: [finance, corporate]
description: 'Extract company ownership and relationship graphs'

output:
  entities:
    description: 'Company and person entities'
    fields:
      - name: name
        type: str
        description: 'Entity name'
      - name: category
        type: str
        description: 'Entity type: Company, Person'
      - name: description
        type: str
        description: 'Brief description'
        required: false
        default: ''
  relations:
    description: 'Ownership and control relationships'
    fields:
      - name: source
        type: str
        description: 'Source entity'
      - name: target
        type: str
        description: 'Target entity'
      - name: relation_type
        type: str
        description: 'owns, controls, invested_in'

guideline:
  target: 'You are a corporate analysis expert. Extract company relationships.'
  rules_for_entities:
    - 'Extract company and person entities only'
    - 'Category must be Company or Person'
    - 'Names must match text exactly'
  rules_for_relations:
    - 'Only extract ownership and control relationships'
    - 'Common types: owns, controls, invested_in, subsidiary_of'
    - 'source and target must be extracted entities'

identifiers:
  entity_id: name
  relation_id: '{source}|{relation_type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name} ({category})'
  relation_label: '{relation_type}'
```

## Next Steps

After graph design:
1. Review with user
2. Optional: yaml-validator
3. Optional: multilingual
