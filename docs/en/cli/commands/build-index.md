# he build-index

Build or rebuild the vector search index for a knowledge base.

---

## Synopsis

```bash
he build-index KA_PATH [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `KA_PATH` | Path to knowledge base directory |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--force` | `-f` | Force rebuild even if index exists |

---

## Description

Builds a vector search index for semantic search and chat functionality:

1. **Reads all entities/relations** — From the knowledge base data
2. **Generates embeddings** — Using the configured embedding model
3. **Builds FAISS index** — For fast similarity search
4. **Saves to disk** — In the `index/` subdirectory

**Required for**: `he search` and `he talk` commands.

---

## Examples

### Build Index

```bash
he build-index ./output/
```

**Output:**
```
Template: general/biography_graph
Language: en

Success! Index built for ./output/

Now you can:
  he search ./output/ "keyword"  # Semantic search
  he talk ./output/ -i           # Interactive chat
```

### Force Rebuild

If the index is corrupted or you want to rebuild:

```bash
he build-index ./output/ -f
```

---

## When to Build Index

### After Parse (Default)

By default, `he parse` builds the index automatically:

```bash
he parse doc.md -t general/biography_graph -o ./kb/ -l en
# Index is built automatically
```

Skip with `--no-index` if you don't need search/chat:

```bash
he parse doc.md -t general/biography_graph -o ./kb/ -l en --no-index
```

### After Feed

Always rebuild after feeding new documents:

```bash
he feed ./kb/ new_doc.md
he build-index ./kb/
```

### After Manual Changes

If you modify `data.json` manually:

```bash
he build-index ./kb/ -f
```

---

## Index Storage

The index is stored in the knowledge base directory:

```
./kb/
├── data.json
├── metadata.json
└── index/              # Index directory
    ├── index.faiss     # FAISS vector index
    └── docstore.json   # Document store mapping
```

---

## Performance

### Build Time

| Knowledge Base Size | Approximate Build Time |
|---------------------|----------------------|
| Small (< 100 items) | < 5 seconds |
| Medium (100-1000) | 5-30 seconds |
| Large (1000+) | 30+ seconds |

### Search Speed

Once built, searches are fast:

```bash
he search ./kb/ "query"  # Typically < 1 second
```

---

## Best Practices

1. **Build after feeding** — Index becomes stale after `he feed`
2. **Use `--no-index` for batch** — Build once after all parsing
3. **Force rebuild if issues** — Use `-f` if search returns unexpected results
4. **Backup large indices** — The `index/` directory can be large

---

## Batch Workflow

For processing multiple documents efficiently:

```bash
# Parse all without building index
he parse doc1.md -t general/biography_graph -o ./kb/ -l en --no-index
he feed ./kb/ doc2.md
he feed ./kb/ doc3.md

# Build index once at the end
he build-index ./kb/

# Now ready for search/chat
he search ./kb/ "query"
he talk ./kb/ -q "question"
```

---

## Troubleshooting

### "Index already exists"

Use `-f` to force rebuild:

```bash
he build-index ./kb/ -f
```

### "Failed to build index"

Check:
1. Knowledge base has data: `he info ./kb/`
2. API key is configured: `he config show`
3. Sufficient disk space for index

### Search still doesn't work

Try force rebuild:

```bash
he build-index ./kb/ -f
```

---

## See Also

- [`he parse`](parse.md) — Parse with optional index building
- [`he feed`](feed.md) — Add documents (requires rebuild)
- [`he search`](search.md) — Search the index
- [`he talk`](talk.md) — Chat using the index
