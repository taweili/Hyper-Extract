# Installation

Hyper-Extract requires **Python 3.11+**.

---

## Install from PyPI

=== "pip"

    ```bash
    pip install hyper-extract
    ```

=== "uv (recommended)"

    ```bash
    uv pip install hyper-extract
    ```

=== "conda"

    ```bash
    pip install hyper-extract
    ```

---

## Verify Installation

```bash
he --version
```

You should see something like:

```
Hyper-Extract CLI version 0.1.0
```

---

## Optional Dependencies

=== "Anthropic Claude Support"

    ```bash
    pip install hyper-extract[anthropic]
    ```

=== "Google Gemini Support"

    ```bash
    pip install hyper-extract[google]
    ```

=== "All Optional Dependencies"

    ```bash
    pip install hyper-extract[all]
    ```

---

## Configuration

Before using Hyper-Extract, you need to configure your LLM API credentials.

### Option 1: Using CLI (Recommended)

```bash
he config init -k YOUR_OPENAI_API_KEY
```

This creates a configuration file at `~/.he/config.toml`.

### Option 2: Using Environment Variables

```bash
export OPENAI_API_KEY=your-api-key
export OPENAI_BASE_URL=https://api.openai.com/v1  # Optional
```

### Option 3: Using .env File (Python Only)

Create a `.env` file in your project root:

```
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

Then load it in your Python code:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Development Installation

If you want to contribute or modify the source code:

```bash
# Clone the repository
git clone https://github.com/yifanfeng97/hyper-extract.git
cd hyper-extract

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

---

## What's Next?

- [:octicons-arrow-right-24: CLI Quickstart](cli-quickstart.md) — Your first extraction from the terminal
- [:octicons-arrow-right-24: Python Quickstart](python-quickstart.md) — Your first extraction with Python
