# he info

Display information and statistics about a knowledge base.

---

## Synopsis

```bash
he info KA_PATH
```

## Arguments

| Argument | Description |
|----------|-------------|
| `KA_PATH` | Path to knowledge base directory |

---

## Description

Shows metadata and statistics for a knowledge base:

- **Path** — Location of the knowledge base
- **Template** — Template used for extraction
- **Language** — Language code (en/zh)
- **Timestamps** — Creation and last update times
- **Statistics** — Node count, edge count
- **Index status** — Whether search index is built

---

## Examples

### Basic Usage

```bash
he info ./output/
```

**Output:**
```
Knowledge Abstract Info

Path          ./output/
Template      general/biography_graph
Language      en
Created       2024-01-15 10:30:00
Updated       2024-01-15 10:35:22
Nodes         25
Edges         32
Index         Built
```

### After Extraction

```bash
he parse tesla.md -t general/biography_graph -o ./kb/ -l en
he info ./kb/
```

### After Feed

```bash
he feed ./kb/ more_content.md
he info ./kb/
# Note the updated node/edge counts and timestamp
```

---

## Output Fields

| Field | Description |
|-------|-------------|
| `Path` | Absolute path to knowledge base |
| `Template` | Template identifier (e.g., `general/biography_graph`) |
| `Language` | Processing language (`en` or `zh`) |
| `Created` | Initial extraction timestamp |
| `Updated` | Last modification timestamp |
| `Nodes` | Number of entities/items |
| `Edges` | Number of relationships |
| `Index` | Search index status (`Built` or `Not Built`) |

---

## Use Cases

### Verify Extraction

Check that extraction worked:

```bash
he info ./kb/
# Should show Nodes > 0, Edges > 0
```

### Check Index Status

Before using search or chat:

```bash
he info ./kb/
# If Index shows "Not Built", run:
he build-index ./kb/
```

### Monitor Growth

Track knowledge base growth over time:

```bash
he info ./kb/
# Feed more documents
he feed ./kb/ update.md
he info ./kb/
# Compare node/edge counts
```

### Scripting

Use in automation scripts:

```bash
#!/bin/bash

if he info ./kb/ 2>/dev/null; then
    echo "Knowledge base exists"
    he feed ./kb/ new_doc.md
else
    echo "Creating new knowledge base"
    he parse new_doc.md -t general/biography_graph -o ./kb/ -l en
fi
```

---

## Troubleshooting

### "Knowledge base directory not found"

The directory doesn't exist or doesn't contain a knowledge base:

```bash
# Check directory exists
ls ./kb/

# Should contain:
# - data.json
# - metadata.json
```

### Missing metadata

If metadata is corrupted, template/language show as "unknown":

```bash
he info ./kb/
# Template: [yellow]unknown[/yellow]
# Language: [yellow]unknown[/yellow]
```

The knowledge base is still usable but some features may be limited.

---

## See Also

- [`he parse`](parse.md) — Create knowledge base
- [`he feed`](feed.md) — Add to knowledge base
- [`he build-index`](build-index.md) — Build search index
