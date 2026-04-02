# CLI Guide

The Hyper-Extract CLI provides a powerful command-line interface for knowledge extraction.

## Installation

The CLI is included with the main package:

```bash
pip install hyper-extract
```

## Basic Usage

### Initialize Configuration

```bash
he config init -k <your-api-key>
```

### Parse a Document

```bash
he parse sample.txt -o output/
```

### Search Extracted Knowledge

```bash
he search output/ "What are the key events?"
```

### Feed New Documents

```bash
he feed output/ another_sample.txt
```

## Commands

### config

Manage configuration:

```bash
# Initialize
he config init -k <your-api-key>
```
# Show current config
he config show

# Update config
he config set llm.model gpt-4o-mini

# List available templates
he config list-templates
```

### parse

Extract knowledge from documents:

```bash
# Basic usage
he parse input.txt -o output/

# With template
he parse input.txt -t finance/earnings_summary -o output/

# With language detection
he parse input.txt -l zh -o output/

# Batch processing
he parse ./documents/ -o output/ --batch
```

### search

Query extracted knowledge:

```bash
# Basic search
he search output/ "What happened?"

# With filters
he search output/ "financial events" --filter type=Event

# With limit
he search output/ "companies" --limit 10
```

### feed

Add new documents to existing knowledge:

```bash
# Feed single document
he feed output/ new_doc.txt

# Feed multiple documents
he feed output/ ./new_docs/
```

### list

List available templates and presets:

```bash
# List all templates
he list

# List by category
he list --category finance

# List domain templates
he list --domain general
```

## Options

### Global Options

| Option | Description |
|--------|-------------|
| `--help` | Show help message |
| `--version` | Show version |
| `--verbose` | Enable verbose output |
| `--config PATH` | Use custom config file |

### Parse Options

| Option | Description |
|--------|-------------|
| `-o, --output PATH` | Output directory |
| `-t, --template NAME` | Template to use |
| `-l, --language CODE` | Document language (en, zh, etc.) |
| `--batch` | Enable batch processing |

## Examples

### Financial Document Extraction

```bash
he parse annual_report.pdf -t finance/earnings_summary -o ./results/
```

### Legal Document Extraction

```bash
he parse contract.txt -t legal/case_facts -o ./legal_output/
```

### Multi-language Support

```bash
he parse chinese_doc.txt -l zh -o ./output/
```

## Next Steps

- Explore [Python API](python-api.md)
- Browse [Domain Templates](domain-templates/index.md)
- Check [CLI Reference](../reference/cli-reference.md)
