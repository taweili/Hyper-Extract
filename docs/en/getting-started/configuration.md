# Configuration

Hyper-Extract uses a TOML configuration file. Default location: `~/.he/config.toml`

## Quick Setup

```bash
# Initialize with API key (recommended)
he config init -k <your-api-key>

# Or configure LLM and Embedder separately
he config llm --api-key <your-api-key>
he config embedder --api-key <your-api-key>
```

## Configuration Options

### LLM Settings

```bash
he config llm --api-key <your-api-key> --model gpt-4o-mini
```

| Option | Description | Default |
|--------|-------------|---------|
| `--api-key`, `-k` | LLM API key | Required |
| `--model`, `-m` | Model name | gpt-4o-mini |
| `--base-url`, `-u` | Custom API base URL | (default) |

### Embedder Settings

```bash
he config embedder --api-key <your-api-key> --model text-embedding-3-small
```

| Option | Description | Default |
|--------|-------------|---------|
| `--api-key`, `-k` | Embedder API key | Required |
| `--model`, `-m` | Model name | text-embedding-3-small |
| `--base-url`, `-u` | Custom API base URL | (default) |

## View Configuration

```bash
he config show
```

## Commands

| Command | Description |
|---------|-------------|
| `he config init -k KEY` | Initialize with API key for both LLM and Embedder |
| `he config llm` | Configure LLM settings |
| `he config embedder` | Configure Embedder settings |
| `he config show` | Show current configuration |

## Next Steps

- Learn about [Templates](../concepts/templates.md)
- Browse [Preset Templates](../concepts/templates.md#preset-templates)
