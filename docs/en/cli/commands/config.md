# he config

Manage Hyper-Extract configuration for LLM and embedder settings.

---

## Synopsis

```bash
he config [COMMAND] [OPTIONS]
```

## Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize configuration (lazy defaults: `gpt-4o-mini` + `text-embedding-3-small`) |
| `show` | Display current configuration |
| `llm` | Configure LLM settings |
| `embedder` | Configure embedder settings |

---

## he config init

Initialize configuration. This is the **lazy one-step setup** — if you pass `-k`, it skips all prompts and uses the built-in defaults:

- **LLM**: `gpt-4o-mini`
- **Embedder**: `text-embedding-3-small`

```bash
he config init [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--api-key` | `-k` | API key for both LLM and embedder |
| `--base-url` | `-u` | Custom API base URL (optional) |

### Examples

#### Lazy one-step setup (recommended)

```bash
he config init -k sk-your-api-key-here
```

This saves `gpt-4o-mini` and `text-embedding-3-small` automatically.

#### With custom base URL

```bash
he config init -k sk-your-key -u https://api.openai.com/v1
```

#### Interactive setup

```bash
he config init
# Prompts for model names and API keys step by step
```

---

## he config show

Display current configuration.

```bash
he config show
```

**Output:**

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

---

## he config llm

Configure LLM settings individually.

```bash
he config llm [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--api-key` | `-k` | LLM API key |
| `--model` | `-m` | LLM model name |
| `--base-url` | `-u` | Custom API base URL |
| `--show` | — | Show current LLM configuration |
| `--unset` | — | Clear LLM configuration |

### Examples

```bash
# View LLM config
he config llm --show

# Update LLM model
he config llm --model gpt-4o

# Update LLM API key and endpoint
he config llm --api-key sk-your-key --base-url https://api.openai.com/v1

# Reset LLM config
he config llm --unset
```

---

## he config embedder

Configure embedder settings individually.

```bash
he config embedder [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--api-key` | `-k` | Embedder API key |
| `--model` | `-m` | Embedder model name |
| `--base-url` | `-u` | Custom API base URL |
| `--show` | — | Show current embedder configuration |
| `--unset` | — | Clear embedder configuration |

### Examples

```bash
# View embedder config
he config embedder --show

# Use a different embedding model
he config embedder --model text-embedding-3-large

# Reset embedder config
he config embedder --unset
```

---

## Configuration File

Configuration is stored at:

- **Linux/macOS**: `~/.he/config.toml`
- **Windows**: `%USERPROFILE%\.he\config.toml`

### Example

```toml
[llm]
model = "gpt-4o-mini"
api_key = "sk-your-api-key"
base_url = "https://api.openai.com/v1"

[embedder]
model = "text-embedding-3-small"
api_key = ""  # Empty inherits from llm.api_key
base_url = ""  # Empty inherits from llm.base_url
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | API key fallback for LLM and embedder |
| `OPENAI_BASE_URL` | Custom API base URL fallback |

**Priority (highest first):** command-line flags → environment variables → config file → defaults.

---

## Troubleshooting

### "API key not found"

```bash
he config init -k your-api-key
```

Or:

```bash
export OPENAI_API_KEY=your-api-key
```

### "Configuration file not found"

```bash
he config init -k your-api-key
```

---

## See Also

- [Configuration Reference](../configuration.md) — Detailed configuration options
- [Installation Guide](../../getting-started/installation.md) — Initial setup
