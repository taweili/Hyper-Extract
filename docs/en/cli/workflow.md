# CLI Workflow Guide

This guide walks you through a complete knowledge extraction workflow using real-world examples.

---

## Scenario: Research Paper Analysis

Imagine you're a researcher who wants to extract and interact with knowledge from academic papers. Here's how to do it with Hyper-Extract.

---

## Step 1: Prepare Your Document

First, ensure your document is in a supported format (`.md`, `.txt`):

```bash
# Example: Convert PDF to text (using external tools)
pdftotext paper.pdf paper.md
```

Or create a sample document:

```bash
cat > transformer_paper.md << 'EOF'
# Attention Is All You Need

## Abstract
The dominant sequence transduction models are based on complex recurrent or 
convolutional neural networks that include an encoder and a decoder. The best 
performing models also connect the encoder and decoder through an attention 
mechanism. We propose a new simple network architecture, the Transformer, 
based solely on attention mechanisms.

## Authors
- Ashish Vaswani
- Noam Shazeer
- Niki Parmar
- Jakob Uszkoreit
- Llion Jones
- Aidan N. Gomez
- Lukasz Kaiser
- Illia Polosukhin

## Key Innovation
The Transformer eschews recurrence and instead relies entirely on an attention 
mechanism to draw global dependencies between input and output sequences.

## Performance
On the WMT 2014 English-to-German translation task, our model achieves a 
BLEU score of 28.4, outperforming all existing models.
EOF
```

---

## Step 2: Extract Knowledge

Use the `parse` command to extract knowledge:

```bash
he parse transformer_paper.md -t general/concept_graph -o ./transformer_kb/ -l en
```

**What happens:**
1. The document is read and chunked (if long)
2. LLM extracts entities and relationships
3. Results are saved to `./transformer_kb/`

**Output structure:**
```
./transformer_kb/
├── data.json       # Extracted knowledge
├── metadata.json   # Extraction metadata
└── index/          # Vector search index (if built)
```

---

## Step 3: Explore the Knowledge

### View Statistics

```bash
he info ./transformer_kb/
```

**Output:**
```
Knowledge Abstract Info

Path          ./transformer_kb/
Template      general/concept_graph
Language      en
Created       2024-01-15 10:30:00
Updated       2024-01-15 10:30:00
Nodes         12
Edges         15
Index         Built
```

### Visualize

```bash
he show ./transformer_kb/
```

This opens an interactive graph in your browser showing:
- **Nodes**: Authors, concepts, models, metrics
- **Edges**: Relationships between them

---

## Step 4: Search for Information

### Semantic Search

Find information even if keywords don't match exactly:

```bash
he search ./transformer_kb/ "neural network architecture"
```

**Results:**
```
Found 3 result(s):

Result 1:
{
  "name": "Transformer",
  "type": "model",
  "description": "A neural network architecture based solely on attention mechanisms"
}

Result 2:
{
  "name": "Attention Mechanism",
  "type": "concept",
  "description": "Mechanism to draw global dependencies between sequences"
}
...
```

### Specific Queries

```bash
he search ./transformer_kb/ "performance metrics" -n 5
```

---

## Step 5: Chat with Your Knowledge

### Single Question

```bash
he talk ./transformer_kb/ -q "What is the main contribution of this paper?"
```

**Response:**
```
The main contribution is the introduction of the Transformer architecture, 
which achieves state-of-the-art results on machine translation tasks while 
being more parallelizable and requiring significantly less training time than 
recurrent or convolutional architectures.
```

### Interactive Mode

```bash
he talk ./transformer_kb/ -i
```

**Session:**
```
Entering interactive mode. Type 'exit' or 'quit' to stop.

> Who are the authors?
The paper was authored by Ashish Vaswani, Noam Shazeer, Niki Parmar, 
Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, and 
Illia Polosukhin.

> What BLEU score did they achieve?
The model achieved a BLEU score of 28.4 on the WMT 2014 English-to-German 
translation task.

> exit
Goodbye!
```

---

## Step 6: Expand Your Knowledge Base

### Add Another Document

```bash
# Download another paper
curl -o bert_paper.md https://example.com/bert.md

# Add to existing knowledge base
he feed ./transformer_kb/ bert_paper.md
```

### Verify the Update

```bash
he info ./transformer_kb/
```

Notice the increased node/edge count and updated timestamp.

---

## Step 7: Rebuild Index (If Needed)

After adding documents, rebuild the search index:

```bash
he build-index ./transformer_kb/
```

Or force a complete rebuild:

```bash
he build-index ./transformer_kb/ -f
```

---

## Complete Script Example

Here's a bash script that automates the entire workflow:

```bash
#!/bin/bash

# Configuration
INPUT_FILE="paper.md"
OUTPUT_DIR="./paper_kb/"
TEMPLATE="general/concept_graph"
LANGUAGE="en"

echo "=== Hyper-Extract Workflow ==="
echo

# Step 1: Parse
echo "Step 1: Extracting knowledge..."
he parse "$INPUT_FILE" -t "$TEMPLATE" -o "$OUTPUT_DIR" -l "$LANGUAGE"
echo

# Step 2: Info
echo "Step 2: Knowledge base info:"
he info "$OUTPUT_DIR"
echo

# Step 3: Search example
echo "Step 3: Sample search:"
he search "$OUTPUT_DIR" "main contributions" -n 2
echo

# Step 4: Open visualization
echo "Step 4: Opening visualization..."
he show "$OUTPUT_DIR"

echo "=== Workflow Complete ==="
```

---

## Advanced: Batch Processing

Process multiple documents at once:

```bash
# Create output directories
mkdir -p ./kb/paper1 ./kb/paper2 ./kb/paper3

# Process each
he parse papers/paper1.md -t general/concept_graph -o ./kb/paper1/ -l en
he parse papers/paper2.md -t general/concept_graph -o ./kb/paper2/ -l en
he parse papers/paper3.md -t general/concept_graph -o ./kb/paper3/ -l en

# Or use a loop
for file in papers/*.md; do
    name=$(basename "$file" .md)
    he parse "$file" -t general/concept_graph -o "./kb/$name/" -l en
done
```

---

## Common Patterns

### Pattern 1: Continuous Knowledge Building

```bash
# Initial extraction
he parse initial_doc.md -t general/biography_graph -o ./kb/ -l en

# Weekly updates
he feed ./kb/ week1_update.md
he feed ./kb/ week2_update.md
he feed ./kb/ week3_update.md

# Monthly rebuild
he build-index ./kb/ -f
```

### Pattern 2: Multi-Domain Project

```bash
# Technical documentation
he parse api_docs.md -t general/concept_graph -o ./project_kb/tech/ -l en

# Legal contracts
he parse contract.pdf -t legal/contract_obligation -o ./project_kb/legal/ -l en

# Financial reports
he parse q4_report.md -t finance/earnings_summary -o ./project_kb/finance/ -l en
```

### Pattern 3: Compare Documents

```bash
# Extract two versions
he parse draft_v1.md -t general/concept_graph -o ./kb/v1/ -l en
he parse draft_v2.md -t general/concept_graph -o ./kb/v2/ -l en

# Compare via chat
he talk ./kb/v1/ -q "What are the main topics?"
he talk ./kb/v2/ -q "What are the main topics?"
```

---

## Troubleshooting Tips

| Issue | Solution |
|-------|----------|
| Extraction is slow | Long documents are chunked; use `--no-index` to skip indexing during parse |
| Search returns nothing | Ensure index is built: `he build-index ./kb/` |
| Template not found | List available: `he list template` |
| Out of memory | Reduce chunk size in config or process smaller documents |

---

## Next Steps

- Learn about [all CLI commands](commands/parse.md)
- Explore the [Template Library](../templates/index.md)
- Read about [choosing the right Auto-Type](../concepts/autotypes.md)
