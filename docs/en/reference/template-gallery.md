# Template Gallery

Complete list of all available preset templates in Hyper-Extract.

## Finance Templates

### Core Templates

| Template | Description |
|----------|-------------|
| `finance/earnings_summary` | Extract earnings report highlights |
| `finance/risk_factor_set` | Extract risk factors |
| `finance/ownership_graph` | Extract ownership relationships |
| `finance/event_timeline` | Extract financial events timeline |
| `finance/sentiment_model` | Extract sentiment analysis |

## Legal Templates

### Core Templates

| Template | Description |
|----------|-------------|
| `legal/case_facts` | Extract case facts from judgments |
| `legal/case_citation` | Extract legal citations |
| `legal/contract_obligation` | Extract contract obligations |
| `legal/compliance_list` | Extract compliance requirements |
| `legal/defined_term_set` | Extract defined terms |
| `legal/case_fact_timeline` | Extract case fact timeline |

## Medicine Templates

### Core Templates

| Template | Description |
|----------|-------------|
| `medicine/drug_interaction` | Extract drug interactions |
| `medicine/treatment_map` | Extract treatment plans |
| `medicine/anatomy_graph` | Extract anatomical relationships |
| `medicine/hospital_timeline` | Extract patient hospital timeline |
| `medicine/discharge_instruction` | Extract discharge instructions |

## TCM Templates

### Core Templates

| Template | Description |
|----------|-------------|
| `tcm/herb_property` | Extract herb properties |
| `tcm/formula_composition` | Extract formula composition |
| `tcm/herb_relation` | Extract herb relationships |
| `tcm/meridian_graph` | Extract meridian relationships |
| `tcm/syndrome_reasoning` | Extract syndrome reasoning |

## Industry Templates

### Core Templates

| Template | Description |
|----------|-------------|
| `industry/safety_control` | Extract safety controls |
| `industry/equipment_topology` | Extract equipment relationships |
| `industry/operation_flow` | Extract operation flows |
| `industry/failure_case` | Extract failure case analysis |
| `industry/emergency_response` | Extract emergency procedures |

## General Templates

### Core Templates

| Template | Description |
|----------|-------------|
| `general/biography` | Extract biographical information |
| `general/concepts` | Extract conceptual relationships |
| `general/workflow` | Extract workflow steps |
| `general/doc_structure` | Extract document structure |
| `general/base_model` | Basic model extraction |
| `general/base_list` | Basic list extraction |
| `general/base_set` | Basic set extraction |
| `general/base_graph` | Basic graph extraction |
| `general/base_hypergraph` | Basic hypergraph extraction |

## Using Templates

### CLI

```bash
he parse document.txt -t <template_name>
```

### Python API

```python
ka = Template.create("<template_name>")
result = ka.parse(document_text)
```

## Creating Custom Templates

See the [Template Design Guide](../concepts/templates.md) for creating your own templates.
