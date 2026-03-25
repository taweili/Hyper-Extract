---
name: hyper-extract
description: |
  Hyper-Extract Knowledge Template Design Assistant. Helps users design YAML configuration templates through natural language dialogue.

  ## Supported Types (8 AutoTypes)
  ### Record Types
  - model: Single structured object
  - list: List of homogeneous objects
  - set: Deduplicated object set
  ### Graph Types
  - graph: Binary relation graph
  - hypergraph: Multi-entity relation hypergraph
  - temporal_graph: Temporal graph with time dimension
  - spatial_graph: Spatial graph with location dimension
  - spatio_temporal_graph: Combined temporal and spatial

  ## Workflow
  1. brainstorm: Explore requirements, discuss type details
  2. record-designer OR graph-designer: Design structure + rules
  3. yaml-validator: Validate configuration (optional)
  4. multilingual: Multi-language conversion (optional)
---

# Hyper-Extract Knowledge Template Design Assistant

## How to Use

### Mode 1: Start from Requirements
Describe your scenario, we'll explore together to clarify needs and determine the type.

### Mode 2: Start from Type
Already know the type? Jump directly to the designer.

### Mode 3: Start from Example
Have a reference template? We'll analyze and adapt it.

## Sub-Skills

| Skill | Purpose |
|-------|---------|
| brainstorm | Deep discussion about requirements and type-specific details |
| record-designer | Design model/list/set structures |
| graph-designer | Design graph/hypergraph/etc structures |
| yaml-validator | Validate YAML correctness |
| multilingual | Multi-language support |

## Calling Sub-Skills

```
[Invoke brainstorm]
User description: [description]
Current understanding: [if any]

[Invoke record-designer]
Type: [model/list/set]
Requirements: [from brainstorm]

[Invoke graph-designer]
Type: [graph/hypergraph/temporal_graph/spatial_graph/spatio_temporal_graph]
Requirements: [from brainstorm]

[Invoke yaml-validator]
YAML: [configuration]
Scope: [all/syntax/semantics]

[Invoke multilingual]
Language: [target language]
```
