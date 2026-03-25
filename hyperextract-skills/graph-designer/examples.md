# Graph Type Examples

Complete YAML examples for graph types. See [SKILL.md](SKILL.md) for workflow.

---

## Example 1: Corporate Ownership (graph)

```yaml
language: en
name: CorporateOwnershipGraph
type: graph
tags: [finance, corporate]
description: 'Extract company ownership and control relationships'

output:
  entities:
    description: 'Company and person entities'
    fields:
      - name: name
        type: str
        description: 'Entity name'
      - name: category
        type: str
        description: 'Company or Person'
  relations:
    description: 'Ownership and control relationships'
    fields:
      - name: source
        type: str
      - name: target
        type: str
      - name: relation_type
        type: str
      - name: percentage
        type: str
        required: false

guideline:
  target: 'You are a corporate analysis expert. Extract company relationships.'
  rules_for_entities:
    - 'Extract company and person entities only'
    - 'Category must be Company or Person'
  rules_for_relations:
    - 'Only extract ownership and control relationships'
    - 'Common types: owns, controls, invested_in, subsidiary_of'

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

---

## Example 2: Battle Analysis (hypergraph nested)

```yaml
language: en
name: BattleAnalysis
type: hypergraph
tags: [history, military]
description: 'Extract historical battle information'

output:
  entities:
    description: 'Historical figures and factions'
    fields:
      - name: name
        type: str
  relations:
    description: 'Battle events with participants'
    fields:
      - name: battle_name
        type: str
      - name: attackers
        type: list
        description: 'Attacking side'
      - name: defenders
        type: list
        description: 'Defending side'
      - name: commanders
        type: list
        description: 'Key commanders'
        required: false
      - name: outcome
        type: str
      - name: year
        type: str
        required: false

guideline:
  target: 'You are a military history expert. Extract battle information.'
  rules_for_entities:
    - 'Extract all mentioned figures and factions'
  rules_for_relations:
    - 'Identify attackers and defenders clearly'
    - 'Include key commanders if mentioned'

identifiers:
  entity_id: name
  relation_id: '{battle_name}'
  relation_members: [attackers, defenders, commanders]

display:
  entity_label: '{name}'
  relation_label: '{battle_name}: {outcome}'
```

---

## Example 3: Meeting Records (spatio_temporal_graph)

```yaml
language: en
name: MeetingRecords
type: spatio_temporal_graph
tags: [business, collaboration]
description: 'Extract meeting information'

output:
  entities:
    description: 'People and organizations'
    fields:
      - name: name
        type: str
  relations:
    description: 'Meeting events'
    fields:
      - name: meeting_title
        type: str
      - name: attendees
        type: list
      - name: meeting_date
        type: str
      - name: location
        type: str
        required: false
      - name: summary
        type: str
        required: false

guideline:
  target: 'You are a business analyst. Extract meeting information.'
  rules_for_entities:
    - 'Extract all mentioned participants'
  rules_for_relations:
    - 'Extract time and location if mentioned'
  rules_for_time:
    - 'Use ISO format when possible'
  rules_for_location:
    - 'Keep structured locations as-is'

identifiers:
  entity_id: name
  relation_id: '{meeting_title}|{meeting_date}'
  relation_members: attendees
  time_field: meeting_date
  location_field: location

display:
  entity_label: '{name}'
  relation_label: '{meeting_title} @ {meeting_date}'
```

---

## Quick Reference

| Type | Example | Key Config |
|------|---------|------------|
| graph | Corporate ownership | source/target |
| hypergraph (simple) | Contract clauses | participants string |
| hypergraph (nested) | Battle analysis | [groups] list |
| temporal_graph | Career timeline | + time_field |
| spatial_graph | Purchase locations | + location_field |
| spatio_temporal | Meeting records | + time + location |
