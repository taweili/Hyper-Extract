# CLI Reference

Complete reference for all Hyper-Extract CLI commands.

## Command Overview

| Command | Description |
|---------|-------------|
| `he config` | Manage configuration |
| `he parse` | Extract knowledge from documents |
| `he search` | Query extracted knowledge |
| `he feed` | Add new documents to knowledge base |
| `he list` | List available templates |

## config

Manage Hyper-Extract configuration.

### Syntax

```bash
he config <action> [options]
```

### Actions

#### init

Initialize configuration:

```bash
he config init -k API_KEY [--provider PROVIDER]
```

#### show

Show current configuration:

```bash
he config show [--format json|yaml]
```

#### set

Update configuration option:

```bash
he config set KEY VALUE
```

#### list-templates

List available templates:

```bash
he config list-templates [--category CATEGORY]
```

## parse

Extract knowledge from documents.

### Syntax

```bash
he parse <input> [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output directory | Required |
| `-t, --template` | Template name | Auto-detect |
| `-l, --language` | Document language | Auto-detect |
| `--method` | Extraction method | Default |
| `--batch` | Batch processing | False |
| `--format` | Output format | json |

### Examples

```bash
# Basic usage
he parse document.txt -o output/

# With template
he parse document.txt -t finance/earnings_summary -o output/

# Batch processing
he parse ./documents/ -o output/ --batch

# Specify language
he parse chinese.txt -l zh -o output/
```

## search

Query extracted knowledge.

### Syntax

```bash
he search <knowledge_base> <query> [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--filter` | Filter by node/edge type | None |
| `--limit` | Maximum results | 10 |
| `--format` | Output format | json |

### Examples

```bash
# Basic search
he search output/ "What happened?"

# With filters
he search output/ "financial events" --filter type=FinancialEvent

# Limited results
he search output/ "companies" --limit 5
```

## feed

Add new documents to existing knowledge base.

### Syntax

```bash
he feed <knowledge_base> <documents...> [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-t, --template` | Template name | Inherited |
| `--merge` | Merge strategy | smart |

### Examples

```bash
# Add single document
he feed output/ new_doc.txt

# Add multiple documents
he feed output/ doc1.txt doc2.txt doc3.txt

# Add directory
he feed output/ ./new_documents/
```

## list

List available templates.

### Syntax

```bash
he list [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--category` | Filter by category | All |
| `--domain` | Filter by domain | All |
| `--format` | Output format | table |

### Categories

- `finance`
- `legal`
- `medicine`
- `tcm`
- `industry`
- `general`

## Global Options

| Option | Description |
|--------|-------------|
| `--help` | Show help message |
| `--version` | Show version number |
| `--verbose` | Enable verbose output |
| `--debug` | Enable debug mode |
| `--config PATH` | Custom config file |
