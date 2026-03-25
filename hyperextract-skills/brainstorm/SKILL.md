---
name: hyper-extract-brainstorm
description: |
  Hyper-Extract Requirements Brainstorming Assistant. Explore user requirements and discuss detailed design for each type.

  ## What We Explore
  - Input: Source, domain, structure
  - Output: What to extract, how to use
  - Type-specific discussions:
    * Record types: Item structure, field design, deduplication
    * Graph types: Entity types, relation types, multi-type nodes
    * Hypergraph: Participant types, outcome structure, reasoning needs
    * Temporal/spatial: Time/location on edges, format handling, observation reference

  ## Output
  1. Requirements summary
  2. Recommended type
  3. Type-specific design specs
---

# Brainstorm: Requirements Exploration

## Phase 1: Input & Output

**Input**: Source, domain, structure level, length
**Output**: What to extract and how to use

## Phase 2: Type Determination

- "Complete summary" → **model**
- "List of items" → **list**
- "Deduplicated entities" → **set**
- "Relationships between entities" → **graph**
- "Multi-party relationships" → **hypergraph**
- "Events with time" → **temporal_graph**
- "Events with location" → **spatial_graph**
- "Events with time + location" → **spatio_temporal_graph**

## Phase 3: Type-Specific Discussion

### Record Types (model/list/set)

- Item structure and fields
- For set: deduplication field
- For list: nested structure, order

### Graph Types

1. **Entity types**: What entities to extract?
2. **Entity fields**: name, category, description?
3. **Relation types**: What relationships?
4. **Relation fields**: Binary or complex?

### Hypergraph

- Participants: Who/what participates?
- Outcome: What result/conclusion?
- Reasoning: Evidence needed?

### Dimension Evolution (temporal/spatial)

After basic graph design, discuss:

**Time dimension?**
- Does the relation have time? (e.g., "A bought from B on date X")
- Is time on node (birth_date) or edge (event_date)?
- If time needs to be a relation dimension → upgrade to **temporal_graph**
- Extract time to edge, add `time_field` in identifiers

**Location dimension?**
- Does the relation have location? (e.g., "A bought from B at location Y")
- Is location on node (hq) or edge (transaction location)?
- If location needs to be a relation dimension → upgrade to **spatial_graph**
- Extract location to edge, add `location_field` in identifiers

**Both?**
- Need both time and location → **spatio_temporal_graph**

## Output Format

```markdown
## Requirements Summary
- Input: ...
- Output: ...
- Quality: ...

## Type Recommendation
**Type**: [type]
**Confidence**: High/Medium/Low

## Design Specs
[Based on type discussion]
```
