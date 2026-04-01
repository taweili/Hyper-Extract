# Configuration

This guide covers advanced configuration options for Hyper-Extract.

## Configuration File

Hyper-Extract uses a YAML configuration file. Default location: `~/.hyper-extract/config.yaml`

## Configuration Options

### LLM Settings

```yaml
llm:
  provider: openai  # openai, anthropic, azure, etc.
  model: gpt-4o
  api_key: ${OPENAI_API_KEY}  # Or use environment variable
  temperature: 0.0
  max_tokens: 4096
```

### Embedding Settings

```yaml
embedding:
  provider: openai  # openai, huggingface, etc.
  model: text-embedding-3-small
  api_key: ${OPENAI_API_KEY}
```

### Extraction Settings

```yaml
extraction:
  default_type: AutoGraph
  max_retries: 3
  timeout: 60
  batch_size: 10
```

### Storage Settings

```yaml
storage:
  type: local  # local, s3, etc.
  path: ./output
  format: json  # json, yaml, parquet
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `HYPER_EXTRACT_CONFIG` | Path to config file |

## CLI Configuration

Initialize configuration via CLI:

```bash
# Initialize with OpenAI
he config init -k your-api-key

# Show current configuration
he config show

# Update specific option
he config set llm.model gpt-4o-mini
```

## Next Steps

- Explore [Concepts](../concepts/index.md) to understand extraction types
- Check [CLI Reference](../reference/cli-reference.md) for all commands
