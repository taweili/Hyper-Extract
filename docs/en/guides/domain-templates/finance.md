# Finance Templates

Hyper-Extract provides specialized templates for financial document extraction.

## Available Templates

### Earnings Summary

Extract key financial metrics from earnings reports:

```yaml
name: earnings_summary
type: TemporalGraph
schema:
  nodes:
    - type: FinancialMetric
    - type: Company
  edges:
    - type: REPORTED
```

### Risk Factors

Extract risk factors from financial documents:

```yaml
name: risk_factors
type: List
schema:
  item:
    - name: category
      type: string
    - name: description
      type: string
```

### Ownership Graph

Extract ownership relationships:

```yaml
name: ownership_graph
type: Graph
schema:
  nodes:
    - type: Entity
    - type: Company
  edges:
    - type: OWNS
```

## Usage Examples

### CLI

```bash
# Extract earnings summary
he parse earnings_report.pdf -t finance/earnings_summary -o output/

# Extract risk factors
he parse 10k_filing.txt -t finance/risk_factors -o output/
```

### Python API

```python
from hyperextract import Template

# Load finance template
ka = Template.create("finance/earnings_summary")

# Extract from document
result = ka.parse(earnings_text)

# Access financial metrics
for metric in result.get_nodes("FinancialMetric"):
    print(f"{metric.name}: {metric.value}")
```

## Supported Document Types

- Annual reports
- Quarterly earnings
- 10-K/10-Q filings
- Equity research reports
- Financial news articles
- IPO prospectuses
- Supply chain analysis

## Next Steps

- [Legal Templates](legal.md)
- [Medicine Templates](medicine.md)
- [Template Gallery](../../reference/template-gallery.md)
