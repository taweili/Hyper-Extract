# Python Quickstart

Get your first knowledge extraction running in 5 minutes using Python.

---

## Prerequisites

- [Hyper-Extract installed](installation.md)
- API key configured (via `.env` file or environment variable)

---

## Step 1: Set Up Your Project

Create a new directory and set up your environment:

```bash
mkdir my_extraction_project
cd my_extraction_project

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install hyper-extract
pip install hyper-extract
```

---

## Step 2: Configure API Key

Create a `.env` file:

```bash
echo "OPENAI_API_KEY=your-api-key" > .env
```

Or set it in your code:

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"
```

---

## Step 3: Create Your First Extraction Script

Create a file `extract.py`:

```python
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

from hyperextract import Template

# Create a template instance
ka = Template.create("general/biography_graph", language="en")

# Sample text
text = """
Nikola Tesla was a Serbian-American inventor, electrical engineer, 
mechanical engineer, and futurist. He is best known for his 
contributions to the design of the modern alternating current 
(AC) electricity supply system.

Born: July 10, 1856, Smiljan, Croatia
Died: January 7, 1943, New York City, NY
"""

# Extract knowledge
result = ka.parse(text)

# Access the extracted data
print(f"Entities: {len(result.data.entities)}")
print(f"Relations: {len(result.data.relations)}")

# Print first entity
if result.data.entities:
    entity = result.data.entities[0]
    print(f"\nFirst entity: {entity.name} ({entity.type})")

# Visualize
result.show()
```

---

## Step 4: Run the Script

```bash
python extract.py
```

You should see:

```
Entities: 5
Relations: 4

First entity: Nikola Tesla (person)
```

And a browser window will open showing the interactive knowledge graph.

---

## Step 5: Working with Results

Access different parts of the extraction:

```python
# Iterate over all entities
for entity in result.data.entities:
    print(f"- {entity.name}: {entity.description}")

# Iterate over all relations
for relation in result.data.relations:
    print(f"- {relation.source} --{relation.type}--> {relation.target}")

# Search within the knowledge base
result.build_index()
search_results = result.search("inventions", top_k=3)
for item in search_results:
    print(item)
```

---

## Step 6: Save and Load

Save your knowledge base for later use:

```python
# Save to disk
result.dump("./my_knowledge_base/")

# Load it back later
new_ka = Template.create("general/biography_graph", language="en")
new_ka.load("./my_knowledge_base/")
```

---

## Step 7: Incremental Updates

Add more text without losing existing knowledge:

```python
additional_text = """
Tesla worked for Thomas Edison in New York City in 1884. 
They had a contentious relationship due to differing views on DC vs AC power.
"""

# Feed adds to existing knowledge
result.feed_text(additional_text)

# Visualize the updated graph
result.show()
```

---

## Complete Example

Here's a complete, production-ready script:

```python
"""Extract knowledge from a document and interact with it."""

import os
from pathlib import Path
from dotenv import load_dotenv
from hyperextract import Template

# Configuration
load_dotenv()

INPUT_FILE = "document.txt"
OUTPUT_DIR = "./output/"
TEMPLATE = "general/biography_graph"
LANGUAGE = "en"


def main():
    # Create template
    print(f"Creating template: {TEMPLATE}")
    ka = Template.create(TEMPLATE, language=LANGUAGE)
    
    # Read document
    print(f"Reading: {INPUT_FILE}")
    text = Path(INPUT_FILE).read_text(encoding="utf-8")
    
    # Extract knowledge
    print("Extracting knowledge...")
    result = ka.parse(text)
    
    # Print summary
    print(f"\nExtraction complete:")
    print(f"  - Entities: {len(result.data.entities)}")
    print(f"  - Relations: {len(result.data.relations)}")
    
    # Build search index
    print("Building search index...")
    result.build_index()
    
    # Save to disk
    print(f"Saving to: {OUTPUT_DIR}")
    result.dump(OUTPUT_DIR)
    
    # Interactive visualization
    print("Opening visualization...")
    result.show()
    
    print("\nDone!")


if __name__ == "__main__":
    main()
```

---

## What's Next?

- [Python SDK Overview](../python/index.md) — Complete API reference
- [Working with Templates](../python/guides/using-templates.md) — Template usage guide
- [Auto-Types Guide](../concepts/autotypes.md) — Choose the right data structure

---

## Troubleshooting

**"No module named 'hyperextract'"**
→ Run `pip install hyper-extract`

**"API key not found"**
→ Check your `.env` file or set `OPENAI_API_KEY` environment variable

**"Template not found"**
→ Use `Template.list()` to see available templates
