# Installation

This guide covers how to install Hyper-Extract and its dependencies.

## Requirements

- Python 3.9+
- pip or uv package manager
- OpenAI API key (or compatible LLM API)

## Installation Methods

### Using pip

```bash
pip install hyper-extract
```

### Using uv

```bash
uv pip install hyper-extract
```

## Install with Extras

For specific use cases, you can install with extras:

```bash
# With all integrations
pip install hyper-extract[all]

# With OpenAI support
pip install hyper-extract[openai]

# With development tools
pip install hyper-extract[dev]
```

## Verify Installation

After installation, verify it works:

```bash
he --version
```

You should see the version number printed.

## Setting Up API Keys

Hyper-Extract requires an API key for LLM services. Set it up:

### Using Environment Variable

```bash
export OPENAI_API_KEY=your-api-key-here
```

### Using CLI

```bash
he config init -k your-api-key-here
```

## Next Steps

- Continue to [Quick Start](quickstart.md) to run your first extraction
- Or configure advanced settings in [Configuration](configuration.md)
