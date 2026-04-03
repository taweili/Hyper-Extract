# CLI Configuration

## Configuration File

The CLI configuration is stored in `~/.he/config.toml`.

## Initialize Configuration

```bash
# Initialize with API Key (recommended for first-time users)
he config init -k YOUR_OPENAI_API_KEY

# Interactive setup (will prompt for LLM and Embedder settings)
he config init
```

## View Configuration

```bash
# Show current configuration
he config show
```

## Configure LLM

```bash
# Set LLM API key and model
he config llm --api-key YOUR_KEY --model gpt-4o-mini

# Show current LLM configuration
he config llm --show

# Set custom base URL
he config llm --api-key YOUR_KEY --base-url https://api.openai.com/v1

# Clear LLM configuration
he config llm --unset
```

## Configure Embedder

```bash
# Set Embedder API key and model
he config embedder --api-key YOUR_KEY --model text-embedding-3-small

# Show current Embedder configuration
he config embedder --show

# Set custom base URL
he config embedder --api-key YOUR_KEY --base-url https://api.openai.com/v1

# Clear Embedder configuration
he config embedder --unset
```

## Configuration Options

### LLM Options

| Option | Flag | Description | Default |
|--------|------|-------------|---------|
| API Key | `--api-key`, `-k` | LLM API key | Required |
| Model | `--model`, `-m` | LLM model name | `gpt-4o-mini` |
| Base URL | `--base-url`, `-u` | Custom API base URL | OpenAI default |

### Embedder Options

| Option | Flag | Description | Default |
|--------|------|-------------|---------|
| API Key | `--api-key`, `-k` | Embedder API key | Required |
| Model | `--model`, `-m` | Embedder model name | `text-embedding-3-small` |
| Base URL | `--base-url`, `-u` | Custom API base URL | OpenAI default |

## Environment Variables

You can also use environment variables as an alternative:

```bash
export OPENAI_API_KEY=your-api-key
export OPENAI_BASE_URL=https://api.openai.com/v1
```

Environment variables are used when not set in the configuration file.
