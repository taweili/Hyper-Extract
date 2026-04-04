# CLI Configuration Reference

Configuration guide for Hyper-Extract CLI, from quick start to advanced settings.

---

## Quick Start

Complete configuration in 3 steps.

### 1. Initialize Configuration

```bash
he config init -k YOUR_API_KEY
```

This creates `~/.he/config.toml` with the following defaults:
- **LLM**: `gpt-4o-mini`
- **Embedder**: `text-embedding-3-small`

### 2. Verify Configuration

```bash
he config show
```

You should see output like this:

```
┌─────────────────────────────────────────────────────────┐
│         Hyper-Extract Configuration                     │
├──────────┬─────────────────────┬─────────────┬──────────┤
│ Service  │ Model               │ API Key     │ Base URL │
├──────────┼─────────────────────┼─────────────┼──────────┤
│ LLM      │ gpt-4o-mini         │ sk-xxxxx... │ (default)│
│ Embedder │ text-embedding-3... │ sk-xxxxx... │ (default)│
└──────────┴─────────────────────┴─────────────┴──────────┘
```

### 3. Modify Configuration (Optional)

```bash
# Change LLM model
he config llm --model gpt-4o

# Use different embedder model
he config embedder --model text-embedding-3-large

# Configure custom API endpoint
he config llm --base-url https://your-api-endpoint.com/v1
```

---

## CLI Command Reference

### Command Overview

| Command | Common Flags | Description |
|---------|-------------|-------------|
| `he config init` | `-k, --api-key` — API key<br>`-u, --base-url` — Custom API base URL | Initialize configuration (first time) |
| `he config llm` | `-m, --model` — Model name<br>`-k, --api-key` — API key<br>`-u, --base-url` — Custom API base URL<br>`--show` — Show current config<br>`--unset` — Clear configuration | Configure LLM |
| `he config embedder` | `-m, --model` — Model name<br>`-k, --api-key` — API key<br>`-u, --base-url` — Custom API base URL<br>`--show` — Show current config<br>`--unset` — Clear configuration | Configure embedder |
| `he config show` | — | View complete configuration |

### Common Usage Examples

**Interactive initialization (recommended for first-time users):**
```bash
he config init
# Follow prompts to enter model name, API key, etc.
```

**Non-interactive initialization (for scripts):**
```bash
he config init -k sk-your-api-key
```

**View LLM configuration:**
```bash
he config llm --show
```

**Configure embedder separately (using different key):**
```bash
he config embedder --api-key sk-embedder-key --model text-embedding-3-large
```

**Clear configuration (reset to defaults):**
```bash
he config llm --unset
he config embedder --unset
```

---

## Configuration File Details

Running `he config init` automatically creates `~/.he/config.toml`.

### File Location

- **Linux/macOS**: `~/.he/config.toml`
- **Windows**: `%USERPROFILE%\.he\config.toml`

### Configuration Format

```toml
[llm]
model = "gpt-4o-mini"
api_key = "sk-your-api-key"
base_url = "https://api.openai.com/v1"

[embedder]
model = "text-embedding-3-small"
api_key = ""  # Empty means inherit from llm.api_key
base_url = ""  # Empty means inherit from llm.base_url
```

### Configuration Options

| Section | Key | Description | Default |
|---------|-----|-------------|---------|
| `[llm]` | `model` | LLM model name | `gpt-4o-mini` |
| `[llm]` | `api_key` | OpenAI API key | Required |
| `[llm]` | `base_url` | API base URL | `https://api.openai.com/v1` |
| `[embedder]` | `model` | Embedding model name | `text-embedding-3-small` |
| `[embedder]` | `api_key` | API key (empty inherits from llm) | — |
| `[embedder]` | `base_url` | API base URL (empty inherits from llm) | — |

### Supported Models

**LLM Models:**
- `gpt-4o-mini` — Fast, cost-effective (default)
- `gpt-4o` — High quality
- `gpt-4-turbo` — Best quality
- Other OpenAI-compatible models

**Embedding Models:**
- `text-embedding-3-small` — Fast, cost-effective (default)
- `text-embedding-3-large` — Better quality
- `text-embedding-ada-002` — Legacy model

---

## Environment Variables

The following environment variables can be used as configuration fallback:

| Variable | Maps To | Example |
|----------|---------|---------|
| `OPENAI_API_KEY` | `llm.api_key`, `embedder.api_key` | `sk-...` |
| `OPENAI_BASE_URL` | `llm.base_url` | `https://api.openai.com/v1` |

**Priority Note:** Environment variables take precedence over config file, but are overridden by command-line flags.

**Use Cases:**
- Temporarily switch API keys
- Inject secrets in CI/CD environments
- Avoid hardcoding keys in config files

---

## Advanced Configuration

### Using OpenAI-Compatible APIs

For Azure, local models, and other OpenAI-compatible APIs:

```toml
[llm]
model = "your-model-name"
api_key = "your-key"
base_url = "https://your-api-endpoint.com/v1"

[embedder]
model = "your-embedding-model"
```

### Different Keys and Base URLs for LLM and Embedder

```toml
[llm]
model = "gpt-4o-mini"
api_key = "sk-llm-key"
base_url = "https://api.openai.com/v1"

[embedder]
model = "text-embedding-3-large"
api_key = "sk-embedder-key"
base_url = "https://your-embedder-provider.com/v1"
```

---

## Troubleshooting

### "API key not found"

**Cause**: API key not configured

**Solution**:

```bash
he config init -k YOUR_API_KEY
```

### "Failed to connect to API"

**Cause**: Network issues or incorrect base_url

**Solution**:

```bash
# Check configuration
he config llm --show

# Reset base_url
he config llm --base-url https://api.openai.com/v1
```

### Permission Denied

**Solution**:

```bash
chmod 600 ~/.he/config.toml
```

### Invalid TOML Format

**Validate configuration**:

```bash
python3 -c "import tomllib; tomllib.load(open('$HOME/.he/config.toml', 'rb'))"
```

**Common issues**:

- Missing quotes around strings
- Trailing commas
- Incorrect section headers

---

## See Also

- [`he config`](commands/config.md) — Detailed configuration command reference
- [Installation Guide](../getting-started/installation.md) — Initial setup steps
