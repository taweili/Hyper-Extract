# Template Library

Browse and choose from 80+ domain-specific extraction templates.

---

## What Are Templates?

Templates are pre-configured extraction setups that combine:
- **Auto-Type** — Output data structure
- **Prompts** — Optimized for specific domains
- **Schema** — Field definitions for your use case
- **Guidelines** — Extraction rules

---

## Template Categories

<div class="grid cards" markdown>

-   :material-folder:{ .lg .middle } __General__

    ---

    Base types and common extraction tasks
    
    - Biography graphs
    - Knowledge graphs
    - Concept extraction
    
    [:octicons-arrow-right-24: Browse](general/index.md)

-   :material-chart-line:{ .lg .middle } __Finance__

    ---

    Financial document analysis
    
    - Earnings summaries
    - Risk factors
    - Ownership structures
    
    [:octicons-arrow-right-24: Browse](finance.md)

-   :material-scale-balance:{ .lg .middle } __Legal__

    ---

    Legal document processing
    
    - Contract obligations
    - Case citations
    - Compliance lists
    
    [:octicons-arrow-right-24: Browse](legal.md)

-   :material-hospital:{ .lg .middle } __Medical__

    ---

    Medical text analysis
    
    - Anatomy graphs
    - Drug interactions
    - Treatment plans
    
    [:octicons-arrow-right-24: Browse](medicine.md)

-   :material-leaf:{ .lg .middle } __TCM__

    ---

    Traditional Chinese Medicine
    
    - Herb properties
    - Formula composition
    - Meridian graphs
    
    [:octicons-arrow-right-24: Browse](tcm.md)

-   :material-factory:{ .lg .middle } __Industry__

    ---

    Industrial documentation
    
    - Equipment topology
    - Safety controls
    - Operation flows
    
    [:octicons-arrow-right-24: Browse](industry.md)

</div>

---

## Quick Selection Guide

| I want to extract... | Use Template |
|---------------------|--------------|
| Person's life story | `general/biography_graph` |
| Research paper concepts | `general/concept_graph` |
| Company earnings | `finance/earnings_summary` |
| Contract terms | `legal/contract_obligation` |
| Medical symptoms | `medicine/symptom_list` |
| Chinese herbs | `tcm/herb_property` |
| Equipment specs | `industry/equipment_topology` |

---

## How to Choose

### By Document Type

| Document | Template Category |
|----------|-------------------|
| Biographies, profiles | General |
| Financial reports, 10-K | Finance |
| Contracts, legal briefs | Legal |
| Medical records, papers | Medical |
| TCM texts, prescriptions | TCM |
| Manuals, procedures | Industry |

### By Output Type

| Need | Auto-Type | Example Templates |
|------|-----------|-------------------|
| Summary report | AutoModel | `earnings_summary`, `discharge_instruction` |
| List of items | AutoList | `compliance_list`, `symptom_list` |
| Unique items | AutoSet | `risk_factor_set`, `defined_term_set` |
| Network/Graph | AutoGraph | `knowledge_graph`, `ownership_graph` |
| Timeline | AutoTemporalGraph | `event_timeline`, `biography_graph` |

→ [Complete Selection Guide](how-to-choose.md)

---

## Using Templates

### CLI

```bash
# List available
he list template

# Use a template
he parse doc.md -t general/biography_graph -o ./out/ -l en
```

### Python

```python
from hyperextract import Template

# Create from preset
ka = Template.create("general/biography_graph", "en")

# List all
all_templates = Template.list()

# Filter by domain
finance = Template.list(filter_by_tag="finance")
```

---

## Template Properties

Each template has:

- **Name** — Unique identifier
- **Type** — Auto-Type (graph, list, model, etc.)
- **Tags** — Domain categorization
- **Languages** — Supported languages (zh, en)
- **Description** — What it extracts

### Viewing Template Details

```python
from hyperextract import Template

# Get template info
cfg = Template.get("general/biography_graph")

print(cfg.name)           # biography_graph
print(cfg.type)           # temporal_graph
print(cfg.tags)           # ['general', 'biography']
print(cfg.description)    # Description text
```

---

## Browse All Templates

→ [Complete Template Browser](browse.md)

---

## Creating Custom Templates

Need something specific? Create your own template:

→ [Custom Templates Guide](../python/guides/custom-templates.md)

---

## Template Format Reference

Learn about the YAML structure:

→ [Template Format](../concepts/templates-format.md)
