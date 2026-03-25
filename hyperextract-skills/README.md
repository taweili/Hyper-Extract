# Hyper-Extract Skills

Knowledge template design skills for Hyper-Extract.

## Skills Overview

| Skill | Purpose |
|-------|---------|
| Root | Entry point for template design |
| brainstorm | Requirements exploration and type discussion |
| record-designer | Design model/list/set structures |
| graph-designer | Design graph/hypergraph/etc structures |
| yaml-validator | Validate YAML configurations |
| multilingual | Convert to multi-language support |

## Installation

### Claude Code

Copy the `hyperextract-skills` folder to your Claude Code skills directory:

```bash
cp -r hyperextract-skills ~/.claude/skills/
```

Or use the plugin command:

```bash
/plugin install hyperextract-skills
```

### Trae

Copy the `hyperextract-skills` folder to your Trae skills directory:

```bash
cp -r hyperextract-skills ~/.trae/skills/
```

## Usage

### Quick Start

1. Start with the brainstorm skill to explore your requirements
2. Based on the recommended type, use either record-designer or graph-designer
3. Optionally validate with yaml-validator
4. Optionally convert to multilingual

### Example Workflow

```
You: I want to extract key information from financial reports

Assistant (using brainstorm):
Let's explore your requirements...

You: I need to extract company name, revenue, and quarter from earnings calls

Assistant (using brainstorm):
Based on your description, I recommend: model type

Assistant (using record-designer):
Let's design the fields for your model...
```

## Supported Types

### Record Types
- **model**: Single structured object
- **list**: List of homogeneous objects
- **set**: Deduplicated object set

### Graph Types
- **graph**: Binary relation graph
- **hypergraph**: Multi-entity relation hypergraph
- **temporal_graph**: Temporal graph with time dimension
- **spatial_graph**: Spatial graph with location dimension
- **spatio_temporal_graph**: Combined temporal and spatial

## Directory Structure

```
hyperextract-skills/
├── SKILL.md                    # Root skill
├── brainstorm/
│   └── SKILL.md               # Requirements exploration
├── record-designer/
│   └── SKILL.md               # Record type design
├── graph-designer/
│   └── SKILL.md               # Graph type design
├── yaml-validator/
│   └── SKILL.md               # YAML validation
├── multilingual/
│   └── SKILL.md               # Multi-language conversion
└── examples/                  # Example templates
    ├── model/
    ├── list/
    ├── set/
    ├── graph/
    ├── hypergraph/
    ├── temporal_graph/
    ├── spatial_graph/
    └── spatio_temporal_graph/
```

## License

Apache 2.0
