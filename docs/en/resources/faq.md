# FAQ

Frequently asked questions about Hyper-Extract.

## General

### What is Hyper-Extract?

Hyper-Extract is an intelligent, LLM-powered knowledge extraction framework that transforms unstructured documents into structured knowledge representations.

### What types of documents can Hyper-Extract process?

Hyper-Extract can process various document types including:
- Plain text files
- PDFs
- Markdown files
- HTML documents
- Word documents

### What languages are supported?

Hyper-Extract supports multiple languages including English, Chinese, Japanese, Korean, and more.

## Installation

### How do I install Hyper-Extract?

```bash
pip install hyper-extract
```

### What are the system requirements?

- Python 3.9 or higher
- OpenAI API key (or compatible LLM API)

## Usage

### How do I extract knowledge from a document?

Using CLI:
```bash
he parse document.txt -o output/
```

Using Python API:
```python
from hyperextract import Template
ka = Template.create("general/biography")
result = ka.parse(document_text)
```

### How do I choose the right template?

Choose a template based on:
1. Document type (finance, legal, medical, etc.)
2. Extraction goal (entities, relationships, lists, etc.)
3. Output format needed (graph, list, model, etc.)

### How do I create a custom template?

See the [Template Design Guide](../concepts/templates.md) for creating custom templates.

## Troubleshooting

### API Key Issues

**Error: "API key not found"**

Solution: Set your API key using:
```bash
he config init -k YOUR_API_KEY
```

### Extraction Quality

**Low quality extractions**

Tips for better results:
1. Use domain-specific templates
2. Provide clear extraction instructions
3. Use longer context windows
4. Adjust temperature settings

### Performance

**Slow extraction times**

Optimization tips:
1. Use `light_rag` method for faster extraction
2. Batch process multiple documents
3. Use appropriate batch sizes

## Contributing

### How can I contribute?

See the [Contributing Guide](contributing.md) for information on how to contribute.

### How do I report bugs?

Please open an issue on our GitHub repository with:
- Detailed description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment information
