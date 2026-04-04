# Installation

Hyper-Extract requires **Python 3.11+**.

---

## Install from PyPI

=== "uv (recommended)"

    ```bash
    uv pip install hyper-extract
    ```

=== "pip"

    ```bash
    pip install hyper-extract
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
