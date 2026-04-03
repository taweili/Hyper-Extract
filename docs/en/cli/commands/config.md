# he config

Manage Hyper-Extract configuration.

---

## Synopsis

```bash
he config [COMMAND] [OPTIONS]
```

## Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize configuration |
| `show` | Display current configuration |
| `set` | Set a configuration value |
| `get` | Get a configuration value |

---

## he config init

Initialize configuration with API credentials.

```bash
he config init [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--key` | `-k` | OpenAI API key |
| `--base-url` | `-u` | API base URL (optional) |
| `--model` | `-m` | Default model (default: gpt-4o-mini) |
| `--embedder` | `-e` | Embedding model (default: text-embedding-3-small) |

### Examples

#### Basic Setup

```bash
he config init -k sk-your-api-key-here
```

#### With Custom Base URL

```bash
he config init -k sk-your-key -u https://api.openai.com/v1
```

#### With Custom Models

```bash
he config init -k sk-your-key -m gpt-4o -e text-embedding-3-large
```

#### Interactive Mode

```bash
he config init
# Prompts for API key interactively
```

---

## he config show

Display current configuration.

```bash
he config show
```

**Output:**
```
Configuration (from ~/.he/config.toml):

[llm]
model = "gpt-4o-mini"
api_key = "sk-...***"
base_url = "https://api.openai.com/v1"

[embedder]
model = "text-embedding-3-small"
api_key = "sk-...***"

[defaults]
language = "en"
chunk_size = 2048
max_workers = 10
```

---

## he config set

Set a configuration value.

```bash
he config set <KEY> <VALUE>
```

### Examples

```bash
# Change default model
he config set llm.model gpt-4o

# Change embedding model
he config set embedder.model text-embedding-3-large

# Set default language
he config set defaults.language zh
```

---

## he config get

Get a configuration value.

```bash
he config get <KEY>
```

### Examples

```bash
he config get llm.model
# Output: gpt-4o-mini

he config get defaults.language
# Output: en
```

---

## Configuration File

Configuration is stored at:

- **Linux/macOS**: `~/.he/config.toml`
- **Windows**: `%USERPROFILE%\.he\config.toml`

### Example Configuration

```toml
[llm]
model = "gpt-4o-mini"
api_key = "sk-your-api-key"
base_url = "https://api.openai.com/v1"

[embedder]
model = "text-embedding-3-small"
api_key = "sk-your-api-key"

[defaults]
language = "en"
chunk_size = 2048
chunk_overlap = 256
max_workers = 10
verbose = false
```

---

## Environment Variables

Configuration can also be set via environment variables (higher priority):

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | API key for LLM and embedder |
| `OPENAI_BASE_URL` | Custom API base URL |
| `HE_LLM_MODEL` | Default LLM model |
| `HE_EMBEDDER_MODEL` | Default embedding model |

---

## Priority Order

Configuration is resolved in this order (highest first):

1. Command-line flags
2. Environment variables
3. Configuration file
4. Built-in defaults

---

## Troubleshooting

### "API key not found"

Initialize configuration:

```bash
he config init -k your-api-key
```

Or set environment variable:

```bash
export OPENAI_API_KEY=your-api-key
```

### "Invalid API key"

Check your API key:

```bash
he config show
# Verify the key is correct
```

### "Configuration file not found"

Run init to create it:

```bash
he config init -k your-api-key
```

---

## See Also

- [Configuration Reference](../configuration.md) — Detailed configuration options
- [Installation Guide](../../getting-started/installation.md) — Initial setup
