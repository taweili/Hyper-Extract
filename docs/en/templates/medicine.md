# Medical Templates

Medical text analysis and extraction.

---

## Overview

Medical templates are designed for extracting clinical information from medical texts.

**Disclaimer**: These templates are for research and analysis purposes only. Not for clinical decision-making without professional review.

---

## Templates

### anatomy_graph

**Type**: graph

**Purpose**: Extract anatomical structures and relationships

**Best for**:
- Anatomy textbooks
- Surgical reports
- Medical education materials

**Entities**:
- Body parts
- Organs
- Systems
- Structures

**Relations**:
- `part_of` — Anatomical hierarchy
- `connected_to` — Structural connections
- `supplies` — Blood/nerve supply

**Example:**
```bash
he parse anatomy.md -t medicine/anatomy_graph -l en
```

---

### discharge_instruction

**Type**: model

**Purpose**: Extract discharge summary information

**Best for**:
- Discharge summaries
- Transfer notes
- After-visit summaries

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `diagnosis` | str | Primary diagnosis |
| `procedures` | list[str] | Procedures performed |
| `medications` | list[str] | Prescribed medications |
| `follow_up` | str | Follow-up instructions |
| `warnings` | list[str] | Warning signs |

**Example:**
```bash
he parse discharge.md -t medicine/discharge_instruction -l en
```

**Python:**
```python
ka = Template.create("medicine/discharge_instruction", "en")
summary = ka.parse(discharge_text)

print(f"Diagnosis: {summary.data.diagnosis}")
print(f"Follow-up: {summary.data.follow_up}")
```

---

### drug_interaction

**Type**: graph

**Purpose**: Extract drug interactions and relationships

**Best for**:
- Drug databases
- Pharmacy references
- Medication reconciliation

**Entities**:
- Drugs
- Drug classes
- Effects

**Relations**:
- `interacts_with` — Drug interactions
- `contraindicated_with` — Contraindications
- `synergizes_with` — Synergistic effects

**Example:**
```bash
he parse drug_ref.md -t medicine/drug_interaction -l en
```

---

### hospital_timeline

**Type**: temporal_graph

**Purpose**: Extract hospital stay timeline

**Best for**:
- Hospital course notes
- Progress notes
- Transfer summaries

**Features**:
- Admission/discharge dates
- Procedures and events
- Timeline visualization

**Example:**
```bash
he parse hospital_notes.md -t medicine/hospital_timeline -l en
```

---

### treatment_map

**Type**: graph

**Purpose**: Extract treatment protocols and pathways

**Best for**:
- Treatment guidelines
- Care pathways
- Protocol documents

**Example:**
```bash
he parse protocol.md -t medicine/treatment_map -l en
```

---

## Use Cases

### Discharge Summary Analysis

```python
from hyperextract import Template

ka = Template.create("medicine/discharge_instruction", "en")
discharges = []

for file in discharge_files:
    summary = ka.parse(file.read_text())
    discharges.append(summary.data)

# Analyze common diagnoses
from collections import Counter
diagnoses = Counter(d.diagnosis for d in discharges)
print(diagnoses.most_common(10))
```

### Drug Interaction Network

```python
ka = Template.create("medicine/drug_interaction", "en")
network = ka.parse(drug_database)

# Find interactions for specific drug
drug = "Warfarin"
interactions = [
    r for r in network.data.relations
    if r.source == drug or r.target == drug
]

for i in interactions:
    print(f"{i.source} {i.type} {i.target}")
```

### Anatomy Education

```python
ka = Template.create("medicine/anatomy_graph", "en")
anatomy = ka.parse(textbook_chapter)

# Visualize
anatomy.show()

# Search
anatomy.build_index()
results = anatomy.search("nerves in hand")
```

---

## Tips

1. **discharge_instruction for summaries** — Quick extraction of key discharge info
2. **drug_interaction for safety** — Build interaction checking tools
3. **anatomy_graph for education** — Create interactive anatomy maps
4. **hospital_timeline for courses** — Track patient journeys

---

## Data Privacy

When working with medical data:
- Ensure HIPAA compliance
- De-identify data before processing
- Use secure environments
- Follow institutional policies

---

## See Also

- [Browse All Templates](browse.md)
- [TCM Templates](tcm.md)
