# CLI Configuration Reference

Complete reference for Hyper-Extract CLI configuration.

---

## Configuration File Location

- **Linux/macOS**: `~/.he/config.toml`
- **Windows**: `%USERPROFILE%\.he\config.toml`

---

## Configuration Sections

### [llm] — Language Model Settings

| Key | Description | Default |
|-----|-------------|---------|
| `model` | LLM model name | `gpt-4o-mini` |
| `api_key` | OpenAI API key | *required* |
| `base_url` | API base URL | `https://api.openai.com/v1` |

**Example:**
```toml
[llm]
model = "gpt-4o"
api_key = "sk-your-api-key"
base_url = "https://api.openai.com/v1"
```

**Supported Models:**
- `gpt-4o-mini` — Fast, cost-effective
- `gpt-4o` — High quality
- `gpt-4-turbo` — Best quality
- Other OpenAI-compatible models

---

### [embedder] — Embedding Model Settings

| Key | Description | Default |
|-----|-------------|---------|
| `model` | Embedding model name | `text-embedding-3-small` |
| `api_key` | API key (defaults to llm.api_key) | — |

**Example:**
```toml
[embedder]
model = "text-embedding-3-large"
```

**Supported Models:**
- `text-embedding-3-small` — Fast, cost-effective
- `text-embedding-3-large` — Better quality
- `text-embedding-ada-002` — Legacy

---

### [defaults] — Default Behavior Settings

| Key | Description | Default |
|-----|-------------|---------|
| `language` | Default language (`en` or `zh`) | `en` |
| `chunk_size` | Text chunk size for processing | `2048` |
| `chunk_overlap` | Overlap between chunks | `256` |
| `max_workers` | Parallel processing workers | `10` |
| `verbose` | Enable verbose output | `false` |

**Example:**
```toml
[defaults]
language = "en"
chunk_size = 4096
chunk_overlap = 512
max_workers = 5
verbose = true
```

---

## Environment Variables

All configuration options can be set via environment variables:

| Variable | Maps To | Example |
|----------|---------|---------|
| `OPENAI_API_KEY` | `llm.api_key`, `embedder.api_key` | `sk-...` |
| `OPENAI_BASE_URL` | `llm.base_url` | `https://api.openai.com/v1` |
| `HE_LLM_MODEL` | `llm.model` | `gpt-4o` |
| `HE_EMBEDDER_MODEL` | `embedder.model` | `text-embedding-3-large` |
| `HE_DEFAULT_LANGUAGE` | `defaults.language` | `zh` |
| `HE_CHUNK_SIZE` | `defaults.chunk_size` | `4096` |
| `HE_VERBOSE` | `defaults.verbose` | `true` |

---

## Complete Example

```toml
# ~/.he/config.toml

[llm]
model = "gpt-4o-mini"
api_key = "sk-your-api-key-here"
base_url = "https://api.openai.com/v1"

[embedder]
model = "text-embedding-3-small"
# api_key defaults to llm.api_key

[defaults]
language = "en"
chunk_size = 2048
chunk_overlap = 256
max_workers = 10
verbose = false
```

---

## Configuration Priority

Settings are resolved in this order (highest priority first):

1. **Command-line flags** (e.g., `-l zh`)
2. **Environment variables** (e.g., `OPENAI_API_KEY`)
3. **Configuration file** (`~/.he/config.toml`)
4. **Built-in defaults**

---

## Managing Configuration

### Initialize

```bash
he config init -k your-api-key
```

### View Current Settings

```bash
he config show
```

### Update Settings

```bash
# Update single value
he config set llm.model gpt-4o

# Or edit file directly
nano ~/.he/config.toml
```

### Reset to Defaults

```bash
rm ~/.he/config.toml
he config init -k your-api-key
```

---

## Advanced Configuration

### Custom API Endpoint

For OpenAI-compatible APIs (Azure, local models, etc.):

```toml
[llm]
model = "your-model-name"
api_key = "your-key"
base_url = "https://your-api-endpoint.com/v1"

[embedder]
model = "your-embedding-model"
```

### Different Keys for LLM and Embedder

```toml
[llm]
model = "gpt-4o-mini"
api_key = "sk-llm-key"

[embedder]
model = "text-embedding-3-small"
api_key = "sk-embedder-key"
```

---

## Troubleshooting

### Permission Denied

```bash
# Fix permissions
chmod 600 ~/.he/config.toml
```

### Invalid TOML Format

Validate your configuration:

```bash
# Using Python
python -c "import tomllib; tomllib.load(open('~/.he/config.toml', 'rb'))"
```

Common issues:
- Missing quotes around strings
- Trailing commas
- Incorrect section headers

---

## See Also

- [`he config`](commands/config.md) — Configuration commands
- [Installation Guide](../getting-started/installation.md) — Initial setup
