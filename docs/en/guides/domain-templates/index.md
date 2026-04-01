# Domain Templates

Hyper-Extract includes specialized templates for various industries and use cases.

## Available Domains

- [Finance](finance.md) - Financial document extraction
- [Legal](legal.md) - Legal document extraction
- [Medicine](medicine.md) - Medical document extraction
- [TCM](tcm.md) - Traditional Chinese Medicine templates

## Quick Start

### Using a Domain Template

```bash
# CLI
he parse document.txt -t finance/earnings_summary

# Python API
ka = Template.create("finance/earnings_summary")
result = ka.parse(document_text)
```

## Template Categories

### Finance Templates

Extract financial information from various document types:

- Earnings reports
- Financial news
- IPO prospectuses
- Equity research
- Supply chain analysis

### Legal Templates

Extract legal information:

- Court judgments
- Contracts
- Compliance filings
- Legal treatises

### Medicine Templates

Extract medical information:

- Clinical guidelines
- Discharge summaries
- Package inserts
- Pathology reports
- Textbooks

### TCM Templates

Traditional Chinese Medicine specific templates:

- Herb properties
- Formula composition
- Meridian graphs
- Syndrome reasoning

## Creating Custom Domain Templates

See [Template Design Guide](../../concepts/templates.md) for creating your own domain-specific templates.
