# TCM Templates

Hyper-Extract provides specialized templates for Traditional Chinese Medicine (TCM) document extraction.

## Available Templates

### Herb Properties

Extract properties of medicinal herbs:

```yaml
name: herb_properties
type: Model
schema:
  - name: herb_name
    type: string
  - name: properties
    type: array
  - name: channels
    type: array
  - name: indications
    type: array
```

### Formula Composition

Extract herbal formula composition:

```yaml
name: formula_composition
type: List
schema:
  item:
    - name: herb_name
      type: string
    - name: dosage
      type: string
    - name: role
      type: string
```

### Meridian Graph

Extract meridian relationships:

```yaml
name: meridian_graph
type: Graph
schema:
  nodes:
    - type: Herb
    - type: Meridian
  edges:
    - type: ENTERS
```

### Syndrome Reasoning

Extract syndrome diagnosis and reasoning:

```yaml
name: syndrome_reasoning
type: TemporalGraph
schema:
  nodes:
    - type: Syndrome
    - type: Pattern
    - type: Treatment
```

## Usage Examples

### CLI

```bash
# Extract herb properties
he parse herbal_compendium.txt -t tcm/herb_properties -o output/

# Extract formula composition
he parse prescription.txt -t tcm/formula_composition -o output/
```

### Python API

```python
from hyperextract import Template

# Load TCM template
ka = Template.create("tcm/herb_properties")

# Extract from document
result = ka.parse(herbal_text)

# Access herb information
for herb in result.get_nodes("Herb"):
    print(f"Herb: {herb.name}")
    print(f"Properties: {herb.properties}")
```

## Supported Document Types

- Herbal compendiums
- Prescription forms
- Medical case records
- Meridian treatises
- Formula pharmacopoeias

## Next Steps

- [Medicine Templates](medicine.md)
- [Finance Templates](finance.md)
- [Template Gallery](../../reference/template-gallery.md)
