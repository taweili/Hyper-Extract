# Browse All Templates

Complete list of available templates.

---

## Statistics

- **Total Templates**: 80+
- **Categories**: 6 domains
- **Auto-Types**: 8 types
- **Languages**: Chinese, English

---

## By Domain

### General Templates

| Template | Type | Description |
|----------|------|-------------|
| `general/base_model` | model | Basic structured model |
| `general/base_list` | list | Basic ordered list |
| `general/base_set` | set | Basic unique set |
| `general/base_graph` | graph | Basic knowledge graph |
| `general/base_hypergraph` | hypergraph | Basic hypergraph |
| `general/base_temporal_graph` | temporal_graph | Basic temporal graph |
| `general/base_spatial_graph` | spatial_graph | Basic spatial graph |
| `general/base_spatio_temporal_graph` | spatio_temporal_graph | Basic spatio-temporal graph |
| `general/biography_graph` | temporal_graph | Person's life timeline |
| `general/concept_graph` | graph | Research concept extraction |
| `general/doc_structure` | model | Document outline structure |
| `general/workflow_graph` | graph | Process workflows |

### Finance Templates

| Template | Type | Description |
|----------|------|-------------|
| `finance/earnings_summary` | model | Quarterly/annual earnings |
| `finance/event_timeline` | temporal_graph | Financial events |
| `finance/ownership_graph` | graph | Company ownership structure |
| `finance/risk_factor_set` | set | Risk factors |
| `finance/sentiment_model` | model | Sentiment analysis |

### Legal Templates

| Template | Type | Description |
|----------|------|-------------|
| `legal/case_citation` | graph | Legal case precedents |
| `legal/case_fact_timeline` | temporal_graph | Case chronology |
| `legal/compliance_list` | list | Compliance requirements |
| `legal/contract_obligation` | list | Contract obligations |
| `legal/defined_term_set` | set | Defined terms |

### Medical Templates

| Template | Type | Description |
|----------|------|-------------|
| `medicine/anatomy_graph` | graph | Anatomical structures |
| `medicine/discharge_instruction` | model | Patient discharge summary |
| `medicine/drug_interaction` | graph | Drug interactions |
| `medicine/hospital_timeline` | temporal_graph | Hospital stay timeline |
| `medicine/treatment_map` | graph | Treatment protocols |

### TCM (Traditional Chinese Medicine) Templates

| Template | Type | Description |
|----------|------|-------------|
| `tcm/formula_composition` | graph | Herbal formula composition |
| `tcm/herb_property` | model | Herb properties |
| `tcm/herb_relation` | graph | Herb relationships |
| `tcm/meridian_graph` | graph | Meridian pathways |
| `tcm/syndrome_reasoning` | graph | Syndrome differentiation |

### Industry Templates

| Template | Type | Description |
|----------|------|-------------|
| `industry/emergency_response` | graph | Emergency procedures |
| `industry/equipment_topology` | graph | Equipment connections |
| `industry/failure_case` | temporal_graph | Failure analysis |
| `industry/operation_flow` | graph | Operational workflows |
| `industry/safety_control` | graph | Safety control systems |

---

## By Auto-Type

### Model Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/base_model` | general | Basic structured model |
| `finance/earnings_summary` | finance | Financial summary |
| `finance/sentiment_model` | finance | Sentiment analysis |
| `medicine/discharge_instruction` | medical | Discharge summary |
| `tcm/herb_property` | tcm | Herb properties |

### List Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/base_list` | general | Basic list |
| `legal/compliance_list` | legal | Compliance requirements |
| `legal/contract_obligation` | legal | Contract obligations |

### Set Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/base_set` | general | Basic set |
| `finance/risk_factor_set` | finance | Risk factors |
| `legal/defined_term_set` | legal | Defined terms |

### Graph Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/base_graph` | general | Basic graph |
| `general/knowledge_graph` | general | Knowledge graph |
| `general/concept_graph` | general | Concept graph |
| `finance/ownership_graph` | finance | Ownership structure |
| `legal/case_citation` | legal | Case precedents |
| `medicine/anatomy_graph` | medical | Anatomy |
| `tcm/herb_relation` | tcm | Herb relationships |

### Temporal Graph Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `general/biography_graph` | general | Biography timeline |
| `finance/event_timeline` | finance | Financial events |
| `legal/case_fact_timeline` | legal | Case timeline |
| `medicine/hospital_timeline` | medical | Hospital timeline |

---

## By Language

### English Only

Methods (not templates):
- `method/light_rag`
- `method/graph_rag`
- `method/hyper_rag`
- `method/itext2kg`
- etc.

### Bilingual (zh, en)

All templates support both languages:
- `general/biography_graph`
- `finance/earnings_summary`
- `legal/contract_obligation`
- etc.

---

## Using This List

### CLI

```bash
# List all
he list template

# Filter by domain
he list template | grep finance
```

### Python

```python
from hyperextract import Template

# Get all
templates = Template.list()

# Filter by type
graphs = Template.list(filter_by_type="graph")

# Filter by tag
finance = Template.list(filter_by_tag="finance")
```

---

## See Also

- [How to Choose](how-to-choose.md)
- [Template Library](index.md)
- [Domain-Specific Guides](general/index.md)
