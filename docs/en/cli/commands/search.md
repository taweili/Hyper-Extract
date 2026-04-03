# he search

Perform semantic search over a knowledge base.

---

## Synopsis

```bash
he search KA_PATH QUERY [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `KA_PATH` | Path to knowledge base directory |
| `QUERY` | Search query string |

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--top-k` | `-n` | Number of results to return | 3 |

---

## Description

Semantic search finds relevant information even when keywords don't match exactly. It uses:

1. **Vector embeddings** — Converts query and content to vectors
2. **Similarity matching** — Finds semantically similar content
3. **Ranking** — Returns most relevant results

**Requires**: Search index must be built. Run `he build-index` if needed.

---

## Examples

### Basic Search

```bash
he search ./output/ "Tesla's inventions"
```

### Get More Results

```bash
he search ./output/ "electrical engineering" -n 10
```

### Natural Language Queries

```bash
he search ./kb/ "What were the major achievements?"
he search ./kb/ "People who worked with Edison"
he search ./kb/ "Important dates in the timeline"
```

### After Building Index

```bash
# First, ensure index exists
he build-index ./output/

# Then search
he search ./output/ "innovation"
```

---

## Output Format

```
Found 3 result(s):

Result 1:
{
  "name": "Nikola Tesla",
  "type": "person",
  "description": "Serbian-American inventor, electrical engineer..."
}

Result 2:
{
  "source": "Nikola Tesla",
  "target": "Thomas Edison",
  "type": "worked_with",
  "description": "Tesla worked for Edison in 1884"
}

Result 3:
...
```

---

## How It Works

1. **Query Embedding** — Converts your query to a vector
2. **Index Search** — Finds nearest vectors in the knowledge base
3. **Result Ranking** — Returns top-k most similar items

---

## Tips for Better Search

1. **Use natural language** — "inventions in electrical engineering" vs "invention electrical"
2. **Be specific** — "Tesla's work on AC power" vs "Tesla work"
3. **Try synonyms** — If "inventions" doesn't work, try "discoveries"
4. **Increase top-k** — Use `-n 10` for broader results

---

## Comparison with `he talk`

| Feature | `he search` | `he talk` |
|---------|-------------|-----------|
| Returns | Raw entities/relations | Natural language answer |
| Use case | Find specific data | Get explanations |
| Speed | Faster | Slower (LLM generation) |
| Precision | Exact matches | Interpretive |

---

## Troubleshooting

### "Index not found"

Build the search index:

```bash
he build-index ./output/
```

### "No results found"

Try:
1. Broader query terms
2. Increase `-n` for more results
3. Different phrasing
4. Check `he info ./output/` to verify data exists

---

## See Also

- [`he talk`](talk.md) — Chat with knowledge base
- [`he build-index`](build-index.md) — Build search index
- [`he parse`](parse.md) — Extract with index building
