# Legal Templates

Hyper-Extract provides specialized templates for legal document extraction.

## Available Templates

### Case Facts

Extract facts from court judgments:

```yaml
name: case_facts
type: TemporalGraph
schema:
  nodes:
    - type: Party
    - type: Event
    - type: LegalFact
  edges:
    - type: PARTICIPATED_IN
    - type: OCCURRED_ON
```

### Contract Terms

Extract contract obligations:

```yaml
name: contract_terms
type: List
schema:
  item:
    - name: clause_type
      type: string
    - name: parties
      type: array
    - name: obligations
      type: string
```

### Compliance Requirements

Extract compliance requirements:

```yaml
name: compliance_requirements
type: List
schema:
  item:
    - name: regulation
      type: string
    - name: requirement
      type: string
    - name: deadline
      type: date
```

## Usage Examples

### CLI

```bash
# Extract case facts
he parse judgment.txt -t legal/case_facts -o output/

# Extract contract terms
he parse contract.pdf -t legal/contract_terms -o output/
```

### Python API

```python
from hyperextract import Template

# Load legal template
ka = Template.create("legal/case_facts")

# Extract from document
result = ka.parse(judgment_text)

# Access parties
for party in result.get_nodes("Party"):
    print(f"Party: {party.name}")
```

## Supported Document Types

- Court judgments
- Legal contracts
- Compliance filings
- Legal treatises
- Regulatory documents

## Next Steps

- [Finance Templates](finance.md)
- [Medicine Templates](medicine.md)
- [Template Gallery](../../reference/template-gallery.md)
