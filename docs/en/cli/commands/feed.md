# he feed

Add documents to an existing knowledge base incrementally.

---

## Synopsis

```bash
he feed KA_PATH INPUT [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `KA_PATH` | Path to existing knowledge base directory |
| `INPUT` | Input file path or `-` for stdin |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--template` | `-t` | Override template (uses metadata if omitted) |
| `--lang` | `-l` | Override language (uses metadata if omitted) |

---

## Description

The `feed` command adds new documents to an existing knowledge base without losing existing data:

1. **Loads existing knowledge** — Reads current knowledge base state
2. **Extracts from new document** — Processes the new content
3. **Merges intelligently** — Combines new and existing data, handling duplicates
4. **Updates metadata** — Records the update timestamp

This is ideal for:
- Building knowledge bases over time
- Adding updates to existing documents
- Combining information from multiple sources

---

## Examples

### Basic Usage

```bash
# Initial extraction
he parse tesla_bio.md -t general/biography_graph -o ./tesla_kb/ -l en

# Add more content
he feed ./tesla_kb/ tesla_inventions.md
```

### Feed Multiple Documents

```bash
he feed ./kb/ doc1.md
he feed ./kb/ doc2.md
he feed ./kb/ doc3.md
```

Or use a loop:

```bash
for file in updates/*.md; do
    he feed ./kb/ "$file"
done
```

### From Stdin

```bash
cat new_content.md | he feed ./kb/ -
```

---

## Merge Behavior

The merge process handles:

| Scenario | Behavior |
|----------|----------|
| Same entity | Merged, descriptions combined |
| Same relation | Updated with latest information |
| New entities | Added to knowledge base |
| New relations | Added connecting existing/new entities |

---

## Workflow Example

### Building a Research Knowledge Base

```bash
# Day 1: Initial paper
he parse paper_v1.md -t general/concept_graph -o ./research_kb/ -l en
he show ./research_kb/

# Day 7: Updated version
he feed ./research_kb/ paper_v2.md
he show ./research_kb/

# Day 14: Related work
he feed ./research_kb/ related_work.md
he build-index ./research_kb/
he talk ./research_kb/ -q "What are the key concepts across all papers?"
```

### Incremental Biography

```bash
# Start with early life
he parse early_life.md -t general/biography_graph -o ./bio_kb/ -l en

# Add career period
he feed ./bio_kb/ career.md

# Add later years
he feed ./bio_kb/ later_years.md

# Final visualization
he show ./bio_kb/
```

---

## Verification

Check that the feed worked:

```bash
he info ./kb/
```

Look for:
- Increased node count
- Increased edge count  
- Updated timestamp

---

## Best Practices

1. **Use same template** — Feeding should use compatible templates
2. **Match language** — Use consistent language for best results
3. **Rebuild index after** — `he build-index ./kb/` for search/chat
4. **Visualize changes** — `he show ./kb/` to see updates

---

## Error Handling

### "Not a valid Knowledge Abstract directory"

The directory doesn't contain a valid knowledge base. Check:

```bash
ls ./kb/
# Should contain: data.json, metadata.json
```

### "Template mismatch"

Feeding works best with the same template type. Override if needed:

```bash
he feed ./kb/ doc.md -t general/biography_graph
```

---

## See Also

- [`he parse`](parse.md) — Create new knowledge base
- [`he info`](info.md) — View knowledge base statistics
- [`he build-index`](build-index.md) — Rebuild search index after feeding
