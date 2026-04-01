# Medicine Templates

Hyper-Extract provides specialized templates for medical document extraction.

## Available Templates

### Drug Interactions

Extract drug interaction information:

```yaml
name: drug_interactions
type: Graph
schema:
  nodes:
    - type: Drug
    - type: Interaction
  edges:
    - type: INTERACTS_WITH
    - type: CAUSES
```

### Treatment Plan

Extract treatment plan details:

```yaml
name: treatment_plan
type: TemporalGraph
schema:
  nodes:
    - type: Treatment
    - type: Medication
    - type: Procedure
  edges:
    - type: INCLUDES
    - type: SCHEDULED_FOR
```

### Patient History

Extract patient medical history:

```yaml
name: patient_history
type: TemporalGraph
schema:
  nodes:
    - type: Condition
    - type: Treatment
    - type: Medication
  edges:
    - type: DIAGNOSED_ON
    - type: TREATED_WITH
```

## Usage Examples

### CLI

```bash
# Extract drug interactions
he parse clinical_note.txt -t medicine/drug_interactions -o output/

# Extract treatment plan
he parse discharge_summary.pdf -t medicine/treatment_plan -o output/
```

### Python API

```python
from hyperextract import Template

# Load medicine template
ka = Template.create("medicine/drug_interactions")

# Extract from document
result = ka.parse(clinical_text)

# Access drug information
for drug in result.get_nodes("Drug"):
    print(f"Drug: {drug.name}")
```

## Supported Document Types

- Clinical guidelines
- Discharge summaries
- Package inserts
- Pathology reports
- Medical textbooks
- Clinical notes

## Next Steps

- [TCM Templates](tcm.md)
- [Finance Templates](finance.md)
- [Template Gallery](../../reference/template-gallery.md)
