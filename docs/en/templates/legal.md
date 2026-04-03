# Legal Templates

Legal document processing and analysis.

---

## Overview

Legal templates are designed for extracting structured information from legal documents.

---

## Templates

### contract_obligation

**Type**: list

**Purpose**: Extract contract obligations and terms

**Best for**:
- Service agreements
- Employment contracts
- Purchase agreements
- License agreements

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `party` | str | Obligated party |
| `obligation` | str | Description of obligation |
| `deadline` | str | Due date/timeline |
| `conditions` | str | Conditions or caveats |

**Example:**
```bash
he parse contract.md -t legal/contract_obligation -l en
```

**Python:**
```python
ka = Template.create("legal/contract_obligation", "en")
result = ka.parse(contract_text)

for obl in result.data.items:
    print(f"{obl.party}: {obl.obligation}")
    if obl.deadline:
        print(f"  Due: {obl.deadline}")
```

---

### case_citation

**Type**: graph

**Purpose**: Extract legal case citations and relationships

**Best for**:
- Legal briefs
- Court opinions
- Research memos
- Case law analysis

**Entities**:
- Cases
- Statutes
- Regulations
- Courts

**Relations**:
- `cited_by` — Citation relationships
- `overruled` — Overruling relationships
- `distinguished` — Distinction relationships

**Example:**
```bash
he parse brief.md -t legal/case_citation -l en
```

---

### case_fact_timeline

**Type**: temporal_graph

**Purpose**: Extract chronological case facts

**Best for**:
- Case summaries
- Investigative reports
- Litigation timelines

**Features**:
- Event dates
- Fact descriptions
- Related parties

**Example:**
```bash
he parse case_summary.md -t legal/case_fact_timeline -l en
```

---

### compliance_list

**Type**: list

**Purpose**: Extract compliance requirements

**Best for**:
- Regulatory documents
- Compliance manuals
- Policy documents

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `requirement` | str | Compliance requirement |
| `regulation` | str | Source regulation |
| `priority` | str | Priority level |

**Example:**
```bash
he parse compliance.md -t legal/compliance_list -l en
```

---

### defined_term_set

**Type**: set

**Purpose**: Extract defined terms and their meanings

**Best for**:
- Contracts with definitions sections
- Technical legal documents
- Glossary extraction

**Example:**
```bash
he parse agreement.md -t legal/defined_term_set -l en
```

**Output:**
```python
{
    "items": [
        "Confidential Information: means any and all non-public...",
        "Effective Date: means the date of execution...",
        "Party: means either signatory..."
    ]
}
```

---

## Use Cases

### Contract Review

```python
from hyperextract import Template

ka = Template.create("legal/contract_obligation", "en")
obligations = ka.parse(contract)

# Find all deadlines
deadlines = [o for o in obligations.data.items if o.deadline]
for d in sorted(deadlines, key=lambda x: x.deadline):
    print(f"{d.deadline}: {d.party} - {d.obligation}")
```

### Case Law Analysis

```python
ka = Template.create("legal/case_citation", "en")
case_graph = ka.parse(brief)

# Find most cited cases
citations = {}
for rel in case_graph.data.relations:
    if rel.type == "cited_by":
        citations[rel.target] = citations.get(rel.target, 0) + 1

top_cases = sorted(citations.items(), key=lambda x: x[1], reverse=True)
```

### Due Diligence

```python
# Extract obligations
ka = Template.create("legal/contract_obligation", "en")
obligations = ka.parse(agreement)

# Extract risks
ka2 = Template.create("finance/risk_factor_set", "en")
risks = ka2.parse(agreement)

# Analyze
high_risk_obligations = [
    o for o in obligations.data.items
    if any(r in o.obligation.lower() for r in risks.data.items)
]
```

---

## Tips

1. **contract_obligation for deadlines** — Track contractual obligations
2. **case_citation for research** — Build citation networks
3. **defined_term_set for clarity** — Extract key definitions
4. **Combine with search** — Use `he search` to find specific clauses

---

## See Also

- [Browse All Templates](browse.md)
- [Finance Templates](finance.md)
