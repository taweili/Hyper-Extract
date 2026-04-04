# Saving and Loading

Persist knowledge bases to disk and restore them later.

---

## Overview

Hyper-Extract provides serialization for:
- **Data** — Extracted entities and relations
- **Metadata** — Extraction settings and timestamps
- **Index** — Vector search index (optional)

---

## Saving Knowledge Bases

### Basic Save

```python
from hyperextract import Template

ka = Template.create("general/biography_graph", "en")
result = ka.parse(text)

# Save to directory
result.dump("./my_kb/")
```

### Save Structure

```
./my_kb/
├── data.json          # Extracted knowledge
├── metadata.json      # Extraction info
└── index/             # Search index (if built)
    ├── index.faiss
    └── docstore.json
```

### Before Saving

```python
# Build index first (if needed)
result.build_index()

# Then save
result.dump("./my_kb/")
```

---

## Loading Knowledge Bases

### Basic Load

```python
from hyperextract import Template

# Create template (must match original)
ka = Template.create("general/biography_graph", "en")

# Load saved data
ka.load("./my_kb/")

# Use
print(f"Loaded {len(ka.nodes)} nodes")
```

### Verify Loaded Data

```python
ka.load("./my_kb/")

# Check it's not empty
if ka.empty():
    print("Warning: No data loaded")
else:
    print(f"Nodes: {len(ka.nodes)}")
    print(f"Edges: {len(ka.edges)}")
```

---

## Use Cases

### Long-term Storage

```python
# Extract and save
ka = Template.create("general/concept_graph", "en")
result = ka.parse(research_paper)
result.build_index()
result.dump("./research_paper_kb/")

# Use weeks later
ka2 = Template.create("general/concept_graph", "en")
ka2.load("./research_paper_kb/")
response = ka2.chat("What are the main findings?")
```

### Sharing Knowledge Bases

```python
# Save to shared location
result.dump("/shared/kb/project_x/")

# Others can load
ka.load("/shared/kb/project_x/")
```

### Backup and Versioning

```python
from datetime import datetime

# Save with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
result.dump(f"./backups/kb_{timestamp}/")

# Or versioned
result.dump("./kb_v1/")
# ... later updates ...
result.dump("./kb_v2/")
```

---

## Working with the Filesystem

### Checking for Existing KB

```python
from pathlib import Path

kb_path = Path("./my_kb/")

if kb_path.exists() and (kb_path / "data.json").exists():
    print("Knowledge base exists, loading...")
    ka.load(kb_path)
else:
    print("Creating new knowledge base...")
    result = ka.parse(text)
    result.dump(kb_path)
```

### Listing Saved KBs

```python
import os

kb_dirs = [d for d in os.listdir("./") if os.path.isdir(d) and "_kb" in d]
print("Available knowledge bases:", kb_dirs)
```

### Moving/Copying

```python
import shutil

# Copy knowledge base
shutil.copytree("./kb_v1/", "./kb_backup/")

# Move knowledge base
shutil.move("./old_location/", "./new_location/")
```

---

## Metadata

### Accessing Metadata

```python
result.dump("./my_kb/")

# Metadata is saved automatically
# Contents:
# - template: Template used
# - lang: Language
# - created_at: Creation timestamp
# - updated_at: Last update timestamp
```

### Custom Metadata

```python
# Add custom metadata
result.metadata["project"] = "Research Project X"
result.metadata["version"] = "1.0"

result.dump("./my_kb/")
```

---

## Complete Example

```python
"""Manage knowledge bases with save/load."""

from hyperextract import Template
from pathlib import Path
import json

class KnowledgeBaseManager:
    def __init__(self, storage_dir="./knowledge_bases/"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def save(self, kb, name):
        """Save knowledge base."""
        kb_path = self.storage_dir / name
        kb.dump(kb_path)
        print(f"Saved to {kb_path}")
        return kb_path
    
    def load(self, name, template="general/biography_graph", lang="en"):
        """Load knowledge base."""
        kb_path = self.storage_dir / name
        
        if not kb_path.exists():
            raise FileNotFoundError(f"Knowledge base not found: {name}")
        
        ka = Template.create(template, lang)
        ka.load(kb_path)
        return ka
    
    def list(self):
        """List available knowledge bases."""
        return [d.name for d in self.storage_dir.iterdir() if d.is_dir()]
    
    def info(self, name):
        """Get knowledge base info."""
        kb_path = self.storage_dir / name
        meta_path = kb_path / "metadata.json"
        
        if meta_path.exists():
            return json.loads(meta_path.read_text())
        return None

# Usage
manager = KnowledgeBaseManager()

# Save
ka = Template.create("general/biography_graph", "en")
result = ka.parse(text)
manager.save(result, "tesla_biography")

# List
print(manager.list())  # ['tesla_biography']

# Load
kb = manager.load("tesla_biography")
print(kb.chat("What did Tesla invent?"))
```

---

## Best Practices

### 1. Match Template on Load

```python
# Save with template X
ka = Template.create("general/biography_graph", "en")

# Load with same template
ka2 = Template.create("general/biography_graph", "en")
ka2.load("./kb/")
```

### 2. Build Index After Loading

```python
ka.load("./kb/")

# Check if index exists, otherwise rebuild
index_path = Path("./kb/") / "index"
if not index_path.exists():
    ka.build_index()
```

### 3. Validate Before Use

```python
try:
    ka.load("./kb/")
    if ka.empty():
        print("Warning: Empty knowledge base")
except FileNotFoundError:
    print("Knowledge base not found")
```

### 4. Use Descriptive Names

```python
# Good
result.dump("./kb/tesla_2024_01_15/")

# Avoid
result.dump("./kb/temp/")
```

---

## Troubleshooting

### "File not found"

```python
from pathlib import Path

kb_path = Path("./my_kb/")
if not kb_path.exists():
    print(f"Directory not found: {kb_path}")
    print(f"Available: {list(Path('.').glob('*/'))}")
```

### "Corrupted data"

```python
# Check data file
import json
data = json.load(open("./my_kb/data.json"))
print(f"Keys: {data.keys()}")
```

### "Index not loaded"

```python
ka.load("./kb/")

# Check if index exists
if (Path("./kb/") / "index").exists():
    print("Index directory exists")
else:
    print("No index, building...")
    ka.build_index()
```

---

## See Also

- [Incremental Updates](incremental-updates.md)
- [Search and Chat](search-and-chat.md)
- [CLI `he parse` command](../../cli/commands/parse.md)
