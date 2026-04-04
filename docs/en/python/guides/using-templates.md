# Using Templates

Learn how to use and customize templates for knowledge extraction.

---

## What Are Templates?

Templates are pre-configured extraction setups that combine:
- **Auto-Type** — Output data structure
- **Prompts** — Instructions for the LLM
- **Schema** — Field definitions and types
- **Guidelines** — Extraction rules and constraints

---

## Built-in Templates

Hyper-Extract includes 80+ templates across 6 domains:

| Domain | Templates | Use Cases |
|--------|-----------|-----------|
| `general` | Base types, biography, concept graph | Common extraction tasks |
| `finance` | Earnings, risk, ownership, timeline | Financial analysis |
| `legal` | Contracts, cases, compliance | Legal document processing |
| `medicine` | Anatomy, drugs, treatments | Medical text analysis |
| `tcm` | Herbs, formulas, syndromes | Traditional Chinese Medicine |
| `industry` | Equipment, safety, operations | Industrial documentation |

---

## Creating Templates

### From Preset

```python
from hyperextract import Template

# Basic usage
ka = Template.create("general/biography_graph", language="en")

# With custom clients
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o")
emb = OpenAIEmbeddings()

ka = Template.create(
    "general/biography_graph",
    language="en",
    llm_client=llm,
    embedder=emb
)
```

### From File

```python
# Load custom YAML template
ka = Template.create(
    "/path/to/my_template.yaml",
    language="en"
)
```

### From Method

```python
# Use extraction method instead of template
ka = Template.create("method/light_rag")
```

---

## Listing Templates

### All Templates

```python
from hyperextract import Template

templates = Template.list()

for path, cfg in templates.items():
    print(f"{path}: {cfg.description}")
```

### Filtered Listing

```python
# By type
graphs = Template.list(filter_by_type="graph")

# By tag
biography = Template.list(filter_by_tag="biography")

# By language
zh_templates = Template.list(filter_by_language="zh")

# Combined
results = Template.list(
    filter_by_type="graph",
    filter_by_language="en"
)
```

### Search Templates

```python
# Search in name and description
results = Template.list(filter_by_query="financial")
```

---

## Template Configuration

### Getting Template Info

```python
from hyperextract import Template

# Get template configuration
cfg = Template.get("general/biography_graph")

print(cfg.name)        # biography_graph
print(cfg.type)        # temporal_graph
print(cfg.description) # Template description
```

### Template Properties

```python
cfg = Template.get("general/biography_graph")

# Properties
print(cfg.name)           # Template name
print(cfg.type)           # Auto-Type (graph, list, etc.)
print(cfg.description)    # Human-readable description
print(cfg.tags)           # Associated tags
print(cfg.language)       # Supported languages
```

---

## Common Template Patterns

### Pattern 1: Biography Analysis

```python
from hyperextract import Template

ka = Template.create("general/biography_graph", "en")

with open("biography.md") as f:
    result = ka.parse(f.read())

# Access timeline data
for edge in result.edges:
    if hasattr(edge, 'time'):
        print(f"{edge.time}: {edge.source} -> {edge.target}")

# Build index for interactive visualization
result.build_index()

result.show()  # Visualize life timeline with search/chat
```

### Pattern 2: Financial Report

```python
from hyperextract import Template

ka = Template.create("finance/earnings_summary", "en")

report = ka.parse(earnings_text)

# Access financial data
print(f"Revenue: {report.data.revenue}")
print(f"EPS: {report.data.eps}")
print(f"Growth: {report.data.yoy_growth}%")
```

### Pattern 3: Legal Contract

```python
from hyperextract import Template

ka = Template.create("legal/contract_obligation", "en")

contract = ka.parse(contract_text)

# List obligations
for obligation in contract.data.obligations:
    print(f"Party: {obligation.party}")
    print(f"Obligation: {obligation.description}")
    print(f"Deadline: {obligation.deadline}")
```

### Pattern 4: Research Paper

```python
from hyperextract import Template

ka = Template.create("general/concept_graph", "en")

paper = ka.parse(paper_text)

# Build searchable knowledge base
paper.build_index()

# Query findings
response = paper.chat("What are the main contributions?")
print(response.content)
```

---

## Multi-Language Support

Templates support both English and Chinese:

```python
# English document
ka_en = Template.create("general/biography_graph", "en")
result_en = ka_en.parse(english_text)

# Chinese document
ka_zh = Template.create("general/biography_graph", "zh")
result_zh = ka_zh.parse(chinese_text)
```

**Note:** Use the language that matches your document for best results.

---

## Template Caching

Templates are loaded and cached for efficiency:

```python
# First call loads template
ka1 = Template.create("general/biography_graph", "en")

# Second call uses cached version
ka2 = Template.create("general/biography_graph", "en")

# Both are independent instances with same configuration
```

---

## Error Handling

### Template Not Found

```python
from hyperextract import Template

try:
    ka = Template.create("nonexistent/template")
except ValueError as e:
    print(f"Template not found: {e}")
    
    # List available
    available = Template.list()
    print("Available templates:", list(available.keys()))
```

### Language Not Supported

```python
cfg = Template.get("general/biography_graph")
print(cfg.language)  # Check supported languages

# Will raise error if language not supported
ka = Template.create("general/biography_graph", "fr")  # May fail
```

---

## Best Practices

1. **Choose domain-specific templates** — Better results than generic ones
2. **Match language to document** — Improves extraction quality
3. **Cache template instances** — Reuse for multiple documents
4. **Check template output schema** — Know what fields to expect

---

## See Also

- [Template Library](../../templates/index.md) — Browse all templates
- [Creating Custom Templates](custom-templates.md) — Write your own
- [Choosing Methods](choosing-methods.md) — When to use methods instead
