# Incremental Updates

Add new information to existing knowledge bases without reprocessing.

---

## Overview

The `feed_text()` method allows you to incrementally add documents to an existing knowledge base:

1. **Preserves existing data** — Won't overwrite what's already there
2. **Intelligent merging** — Handles duplicates and conflicts
3. **Updates metadata** — Tracks when updates occurred

---

## Basic Usage

```python
from hyperextract import Template

ka = Template.create("general/biography_graph", "en")

# Initial extraction
result = ka.parse(initial_text)
print(f"Initial: {len(result.nodes)} nodes")

# Add more content
result.feed_text(additional_text)
print(f"After feed: {len(result.nodes)} nodes")
```

---

## Use Cases

### Building Knowledge Over Time

```python
ka = Template.create("general/biography_graph", "en")
kb = ka.parse(early_life_text)

# Add career information
kb.feed_text(career_text)

# Add later years
kb.feed_text(later_years_text)

# Rebuild index after feeding new data
kb.build_index()

# Final result combines all periods (with interactive search/chat)
kb.show()
```

### Processing Multiple Documents

```python
ka = Template.create("general/concept_graph", "en")
kb = ka.parse(documents[0])

for doc in documents[1:]:
    kb.feed_text(doc)
    print(f"Added document, now {len(kb.nodes)} nodes")
```

### Updating with New Information

```python
# Original extraction
kb = ka.parse(original_paper)

# Add corrections/updates
kb.feed_text(corrections)

# Save updated version
kb.dump("./updated_kb/")
```

---

## How Merging Works

### Entity Merging

```python
# If same entity appears in both texts
# Result: Merged descriptions, fields combined
```

### Relation Merging

```python
# If same relation appears
# Result: Updated with latest information
```

### Duplicate Handling

```python
# Exact duplicates are detected and merged
# Near-duplicates (similar names) may create separate entries
```

---

## Best Practices

### 1. Same Template Type

Ensure you're using compatible Auto-Types:

```python
# Good: Same template type
kb = ka.parse(text1)  # biography_graph
kb.feed_text(text2)   # same type

# Be careful: Mixing types may cause issues
```

### 2. Rebuild Index After Feeding

```python
kb.feed_text(new_text)
kb.build_index()  # Required for search/chat
```

### 3. Save Intermediate States

```python
# Save after major updates
kb.feed_text(chapter1)
kb.dump("./kb_v1/")

kb.feed_text(chapter2)
kb.dump("./kb_v2/")
```

### 4. Monitor Growth

```python
initial_count = len(kb.nodes)
kb.feed_text(new_text)
new_count = len(kb.nodes)

print(f"Added {new_count - initial_count} new nodes")
```

---

## Complete Example

```python
"""Build a knowledge base incrementally from multiple sources."""

from hyperextract import Template
from pathlib import Path

def build_knowledge_base(source_dir, output_dir):
    ka = Template.create("general/biography_graph", "en")
    
    # Get all text files
    files = sorted(Path(source_dir).glob("*.md"))
    
    if not files:
        print("No files found")
        return
    
    # Initial extraction from first file
    print(f"Processing {files[0].name}...")
    kb = ka.parse(files[0].read_text())
    
    # Feed remaining files
    for file in files[1:]:
        print(f"Adding {file.name}...")
        kb.feed_text(file.read_text())
        print(f"  Now {len(kb.nodes)} nodes")
    
    # Build index for search/chat
    print("Building search index...")
    kb.build_index()
    
    # Save
    print(f"Saving to {output_dir}...")
    kb.dump(output_dir)
    
    print("Done!")
    return kb

# Usage
kb = build_knowledge_base("./sources/", "./combined_kb/")
```

---

## Comparison: Parse vs Feed

| Operation | Use When | Result |
|-----------|----------|--------|
| `parse()` | Starting fresh | New knowledge base |
| `feed_text()` | Adding to existing | Updated knowledge base |

### Chaining Operations

```python
# Parse returns new instance
result1 = ka.parse(text1)
result2 = ka.parse(text2)  # Independent of result1

# Feed modifies existing
result1.feed_text(text2)   # result1 is updated
```

---

## Limitations

### 1. Memory Usage

Large knowledge bases consume memory:

```python
# Monitor size
import sys
size = sys.getsizeof(kb.data)
print(f"Knowledge base size: {size} bytes")
```

### 2. Merge Quality

Merging isn't perfect:
- Similar but not identical entities may not merge
- Very large knowledge bases may slow down

### 3. Index Staleness

Always rebuild after feeding:

```python
kb.feed_text(text)
kb.build_index()  # Don't forget!
```

---

## Troubleshooting

### "Memory error"

Process in smaller batches:

```python
for batch in chunks(documents, batch_size=5):
    for doc in batch:
        kb.feed_text(doc)
    kb.dump(f"./kb_checkpoint/")  # Save periodically
```

### "Duplicate entities"

Normalize entity names in your text:

```python
# Instead of "Nikola Tesla" and "Tesla"
# Use consistent naming
```

### "Index out of date"

```python
# Forgot to rebuild?
kb.build_index()
```

---

## See Also

- [Saving and Loading](saving-loading.md)
- [Search and Chat](search-and-chat.md)
- [Working with Auto-Types](working-with-autotypes.md)
