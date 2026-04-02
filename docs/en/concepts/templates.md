# Templates

Templates define WHAT to extract using declarative YAML. They provide a powerful way to specify extraction schemas without writing code.

## Type Selection

![Knowledge Structures Matrix](../assets/autotypes.png)

Before designing a template, determine which type fits your needs:

```
Need relationships?
├─ No → Record types (model, list, set)
└─ Yes → Graph types (graph, hypergraph, temporal_graph, spatial_graph)

Record types: Direct field extraction, no entity or relation concepts
Graph types: Extract entities and their relationships
```

| Type | Description | Use Case |
|------|-------------|----------|
| `model` | Single structured object | Extract one record |
| `list` | Ordered array | Extract ranked items |
| `set` | Deduplicated collection | Extract unique entities |
| `graph` | Binary relations (A→B) | Extract entity relationships |
| `hypergraph` | Multi-entity relations | Extract multi-party events |
| `temporal_graph` | + time dimension | Extract events over time |
| `spatial_graph` | + space dimension | Extract events at locations |
| `spatio_temporal_graph` | + time + space | Extract events at locations over time |

---

## Record Types

Record types use `output.fields` to define the data structure directly. No entities or relations.

### Common Structure

```yaml
language: en

name: TemplateName
type: [model/list/set]
tags: [domain]

description: 'Template description.'

output:
  fields:
    - name: field_name
      type: str
      description: 'Field description.'
      required: false
      default: 'value'

guideline:
  target: 'Extraction target description.'
  rules:
    - 'Rule 1'
    - 'Rule 2'

display:
  label: '{field_name}'
```

### model - Single Object

Extract a single structured record.

```yaml
language: en

name: Earnings Summary
type: model
tags: [finance]

description: 'Extract key financial metrics from earnings reports.'

output:
  fields:
    - name: company_name
      type: str
      description: 'Company name.'
    - name: revenue
      type: str
      description: 'Revenue amount.'
    - name: quarter
      type: str
      description: 'Quarter.'

guideline:
  target: 'Extract key financial information.'
  rules:
    - 'Extract company name and financial data'
    - 'Use numbers from the source text'

display:
  label: '{company_name}'
```

### list - Ordered Array

Extract ordered items (rankings, sequences, bullet points).

```yaml
language: en

name: Risk Factor List
type: list
tags: [finance]

description: 'Extract risk factors in order.'

output:
  fields:
    - name: category
      type: str
      description: 'Risk category.'
    - name: description
      type: str
      description: 'Risk description.'

guideline:
  target: 'Extract risk factors.'
  rules:
    - 'Extract all risk factors'
    - 'Maintain order as they appear'

display:
  label: '{category}'
```

### set - Deduplicated Collection

Extract unique entities with automatic deduplication.

```yaml
language: en

name: Person Set
type: set
tags: [general]

description: 'Extract unique person entities.'

output:
  fields:
    - name: name
      type: str
      description: 'Person name.'
    - name: role
      type: str
      description: 'Role or position.'
      required: false

guideline:
  target: 'Extract person entities.'
  rules:
    - 'Extract all unique persons'
    - 'Apply deduplication by name'

identifiers:
  item_id: name

display:
  label: '{name}'
```

**Note**: Set type requires `identifiers.item_id` to define the deduplication key.

---

## Graph Types

Graph types extract entities and their relationships. They use `output.entities` and `output.relations`.

### Common Structure

```yaml
language: en

name: TemplateName
type: [graph/hypergraph/temporal_graph/spatial_graph]
tags: [domain]

description: 'Template description.'

output:
  entities:
    description: 'Entity description.'
    fields:
      - name: name
        type: str
        description: 'Entity name.'
      - name: type
        type: str
        description: 'Entity type.'
  relations:
    description: 'Relation description.'
    fields:
      - name: source
        type: str
      - name: target
        type: str
      - name: type
        type: str

guideline:
  target: 'Extraction target description.'
  rules_for_entities:
    - 'Rule 1'
  rules_for_relations:
    - 'Rule 2'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}'
```

### graph - Binary Relations

Extract relationships between two entities (A→B).

```yaml
language: en

name: Ownership Graph
type: graph
tags: [finance]

description: 'Extract ownership relationships.'

output:
  entities:
    fields:
      - name: name
        type: str
        description: 'Entity name.'
      - name: type
        type: str
        description: 'Entity type (company/person).'
  relations:
    fields:
      - name: source
        type: str
        description: 'Owner.'
      - name: target
        type: str
        description: 'Owned entity.'
      - name: type
        type: str
        description: 'Relation type.'

guideline:
  target: 'Extract ownership relationships.'
  rules_for_entities:
    - 'Extract companies and individuals'
    - 'Maintain consistent naming'
  rules_for_relations:
    - 'Create relations only when explicitly stated'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}'
```

### hypergraph - Multi-Entity Relations

Extract relationships involving multiple participants.

#### Simple Hypergraph (Flat List)

All participants have equal roles.

```yaml
language: en

name: Meeting Hypergraph
type: hypergraph
tags: [general]

output:
  entities:
    fields:
      - name: name
        type: str
  relations:
    fields:
      - name: topic
        type: str
        description: 'Meeting topic.'
      - name: participants
        type: list
        description: 'List of participants.'
      - name: outcome
        type: str
        description: 'Meeting outcome.'
        required: false

identifiers:
  entity_id: name
  relation_id: '{topic}'
  relation_members: participants  # STRING

display:
  entity_label: '{name}'
  relation_label: '{topic}'
```

#### Nested Hypergraph (Semantic Groups)

Participants have distinct semantic roles.

```yaml
language: en

name: Battle Analysis
type: hypergraph
tags: [history]

output:
  entities:
    fields:
      - name: name
        type: str
  relations:
    fields:
      - name: battle_name
        type: str
      - name: attackers
        type: list
        description: 'Attacking parties.'
      - name: defenders
        type: list
        description: 'Defending parties.'
      - name: outcome
        type: str

identifiers:
  entity_id: name
  relation_id: '{battle_name}'
  relation_members: [attackers, defenders]  # LIST

display:
  entity_label: '{name}'
  relation_label: '{battle_name}'
```

### temporal_graph - With Time Dimension

Add time dimension to graph relationships.

```yaml
language: en

name: Event Timeline
type: temporal_graph
tags: [general]

output:
  entities:
    fields:
      - name: name
        type: str
        description: 'Event name.'
      - name: type
        type: str
        description: 'Event type.'
  relations:
    fields:
      - name: source
        type: str
      - name: target
        type: str
      - name: type
        type: str
      - name: time
        type: str
        description: 'When the relation occurred.'
        required: false

guideline:
  target: 'Extract events and temporal relationships.'
  rules_for_entities:
    - 'Extract key events'
  rules_for_relations:
    - 'Extract temporal relationships'
  rules_for_time:
    - 'Record when events occurred'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}|{time}'
  relation_members:
    source: source
    target: target
  time_field: time

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}@{time}'
```

### spatial_graph - With Space Dimension

Add location dimension to graph relationships.

```yaml
language: en

name: Spatial Graph
type: spatial_graph
tags: [general]

output:
  entities:
    fields:
      - name: name
        type: str
      - name: type
        type: str
  relations:
    fields:
      - name: source
        type: str
      - name: target
        type: str
      - name: type
        type: str
      - name: location
        type: str
        description: 'Where the relation occurred.'
        required: false

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}|{location}'
  relation_members:
    source: source
    target: target
  location_field: location

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}@{location}'
```

### spatio_temporal_graph - Time + Space

Combine time and location dimensions.

```yaml
identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}|{location}|{time}'
  relation_members:
    source: source
    target: target
  time_field: time
  location_field: location

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}@{location}({time})'
```

---

## Field Types

| Type | Description | Example |
|------|-------------|---------|
| `str` | String | "Hello World" |
| `int` | Integer | 42 |
| `float` | Float | 3.14 |
| `bool` | Boolean | true |
| `list` | List | ["a", "b", "c"] |

---

## Display Configuration

| Type | entity_label | relation_label |
|------|--------------|----------------|
| graph | `{name} ({type})` | `{type}` |
| hypergraph | `{name}` | `{event_name}` |
| temporal_graph | `{name} ({type})` | `{type}@{time}` |
| spatial_graph | `{name} ({type})` | `{type}@{location}` |
| spatio_temporal_graph | `{name} ({type})` | `{type}@{location}({time})` |

---

## Schema vs Guideline

| Schema Defines (WHAT) | Guideline Defines (HOW TO DO WELL) |
|----------------------|----------------------------------|
| Field names | Extraction strategy |
| Field types | Quality requirements |
| Field descriptions | Creation conditions |
| Required/optional | Common mistakes to avoid |

**Important**: Guideline should NOT repeat schema definitions.

---

## Preset Templates

Hyper-Extract includes 80+ preset templates across 6 domains:

### Finance
- `finance/earnings_summary` (model)
- `finance/risk_factor_set` (set)
- `finance/ownership_graph` (graph)
- `finance/event_timeline` (temporal_graph)

### Legal
- `legal/case_fact_timeline` (temporal_graph)
- `legal/case_citation` (graph)
- `legal/contract_obligation` (list)

### Medicine
- `medicine/drug_interaction` (graph)
- `medicine/treatment_map` (temporal_graph)
- `medicine/discharge_instruction` (list)

### TCM
- `tcm/herb_property` (model)
- `tcm/formula_composition` (list)
- `tcm/meridian_graph` (graph)

### Industry
- `industry/safety_control` (list)
- `industry/equipment_topology` (graph)
- `industry/failure_case` (temporal_graph)

### General
- `general/graph` (graph)
- `general/list` (list)
- `general/model` (model)
- `general/set` (set)
- `general/biography_graph` (spatio_temporal_graph)

---

## Using Templates

### CLI

```bash
# Use preset template
he parse document.txt -t finance/ownership_graph -o output/

# Use custom template
he parse document.txt -t template.yaml -o output/
```

### Python API

```python
from hyperextract import Template

# Load preset template
ka = Template.create("finance/ownership_graph", "en")

# Load from YAML
ka = Template.create("template.yaml", "en")

# Parse document
result = ka.parse(document_text)
```

---

## Next Steps

- Browse the [Template Gallery](../../reference/template-gallery.md)
- Learn about [Domain Templates](../guides/domain-templates/index.md)
- Create your own templates
- Read the [Design Guide](https://github.com/hyper-extract/hyper-extract/blob/main/hyperextract/templates/DESIGN_GUIDE.md)
