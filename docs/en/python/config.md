# Python SDK Configuration

## Environment Variables

Create a `.env` file in your project root:

```bash
# Copy the example env file
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

## Loading Environment Variables

Use `python-dotenv` to load environment variables:

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
```

## Programmatic Configuration

You can also set environment variables programmatically:

```python
import os

os.environ["OPENAI_API_KEY"] = "your-api-key"
os.environ["OPENAI_BASE_URL"] = "https://api.openai.com/v1"
```

## Configuration Options

### LLM Options

| Option | Environment Variable | Default |
|--------|---------------------|---------|
| API Key | `OPENAI_API_KEY` | Required |
| Base URL | `OPENAI_BASE_URL` | OpenAI default |
| Model | `LLM_MODEL` | `gpt-4o-mini` |
| Temperature | `LLM_TEMPERATURE` | `0.0` |

### Embedder Options

| Option | Environment Variable | Default |
|--------|---------------------|---------|
| Model | `EMBEDDER_MODEL` | `text-embedding-3-small` |
| Batch Size | `EMBEDDER_BATCH_SIZE` | `100` |

## Example .env File

```bash
# Required
OPENAI_API_KEY=sk-your-api-key

# Optional
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.0
EMBEDDER_MODEL=text-embedding-3-small
```
