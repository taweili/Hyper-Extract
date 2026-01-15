# Building Documentation

This guide explains how to build and preview the Hyper-Extract documentation.

## Prerequisites

The documentation uses MkDocs with Material theme. Required dependencies are in the `dev` dependency group:

```toml
[dependency-groups]
dev = [
    "mkdocs>=1.6.1",
    "mkdocs-material>=9.7.1",
    "mkdocstrings[python]>=1.0.0",
]
```

## Installation

### Using uv (Recommended)

```bash
# Install all dependencies including dev dependencies
uv sync

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
```

### Using pip

```bash
# Install project with dev dependencies
pip install -e ".[dev]"
```

## Building Documentation

### Development Server (Live Preview)

Start a local server with live reloading:

```bash
mkdocs serve
```

Then open your browser to `http://127.0.0.1:8000/`

- Changes to `.md` files auto-reload
- Hot reload for configuration changes
- Useful for writing and testing documentation

### Build Static Site

Generate the static HTML site:

```bash
mkdocs build
```

Output is in `site/` directory:
```
site/
├── index.html
├── user-guide/
│   ├── getting-started/
│   └── knowledge-patterns/
├── api/
│   ├── base/
│   ├── unit/
│   ├── list/
│   └── set/
├── zh/
│   └── index.html
└── assets/
```

### Build with Clean

Remove old build artifacts first:

```bash
mkdocs build --clean
```

### Strict Mode

Build with warnings as errors:

```bash
mkdocs build --strict
```

Useful for CI/CD to catch documentation issues.

## Documentation Structure

```
docs/
├── index.md                    # English homepage
├── user-guide/
│   ├── getting-started.md     # Installation and basic usage
│   └── knowledge-patterns.md  # Pattern selection guide
├── api/
│   ├── index.md               # API overview
│   ├── base.md                # BaseAutoType API
│   ├── unit.md                # AutoModel API
│   ├── list.md                # AutoList API
│   └── set.md                 # AutoSet API
└── zh/
    └── index.md               # Chinese homepage (中文首页)
```

## Multi-Language Support

### Current Languages

- **English** (default): `/`
- **中文** (Chinese): `/zh/`

### Adding New Languages

1. Create language directory:
   ```bash
   mkdir docs/ja  # Japanese example
   ```

2. Add translation files:
   ```bash
   cp docs/index.md docs/ja/index.md
   # Translate content to Japanese
   ```

3. Update `mkdocs.yml`:
   ```yaml
   extra:
     alternate:
       - name: English
         link: /
         lang: en
       - name: 中文
         link: /zh/
         lang: zh
       - name: 日本語
         link: /ja/
         lang: ja
   ```

4. Add to navigation:
   ```yaml
   nav:
     # ... existing nav ...
     - 日本語:
         - ホーム: ja/index.md
   ```

## Configuration

### MkDocs Configuration (`mkdocs.yml`)

Key sections:

```yaml
# Site metadata
site_name: Hyper-Extract
site_description: An intelligent, LLM-powered knowledge extraction framework

# Theme
theme:
  name: material
  language: en
  features:
    - navigation.tabs
    - search.suggest
    - content.code.copy

# Plugins
plugins:
  - search
  - mkdocstrings  # Auto-generate API docs from docstrings

# Markdown extensions
markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - admonition
```

### MkDocstrings Configuration

Auto-generates API documentation from Python docstrings:

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          paths: [.]  # Search path for modules
          options:
            show_source: true
            show_root_heading: true
            docstring_style: google
```

Usage in markdown:
```markdown
# BaseAutoType API

::: hyperextract.core.base.BaseAutoType
    options:
      show_source: true
      heading_level: 2
```

## Deployment

### GitHub Pages

1. **Build documentation**:
   ```bash
   mkdocs gh-deploy
   ```

   This command:
   - Builds the documentation
   - Commits to `gh-pages` branch
   - Pushes to GitHub

2. **Configure GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from branch
   - Branch: `gh-pages` / `root`

### Manual Deployment

1. Build static site:
   ```bash
   mkdocs build
   ```

2. Deploy `site/` directory to your hosting:
   ```bash
   # Example: Deploy to Netlify
   netlify deploy --dir=site --prod
   
   # Example: Deploy to Vercel
   vercel --prod site/
   ```

## Continuous Integration

### GitHub Actions

Create `.github/workflows/docs.yml`:

```yaml
name: Deploy Documentation

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'mkdocs.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install mkdocs mkdocs-material mkdocstrings[python]
      
      - name: Deploy documentation
        run: mkdocs gh-deploy --force
```

## Tips

### Writing Documentation

1. **Use code blocks with language hints**:
   ````markdown
   ```python
   from hyperextract import AutoModel
   ```
   ````

2. **Add admonitions for important notes**:
   ```markdown
   !!! note
       This is an important note.
   
   !!! warning
       Be careful with this feature.
   ```

3. **Link to other pages**:
   ```markdown
   See [Getting Started](user-guide/getting-started.md)
   See [API Reference](api/base.md#extract)
   ```

4. **Use tabs for alternatives**:
   ````markdown
   === "Python"
       ```python
       knowledge.extract(text)
       ```
   
   === "Result"
       ```json
       {"title": "Example"}
       ```
   ````

### Auto-generating API Docs

For classes with good docstrings:

```markdown
# MyClass API

::: mymodule.MyClass
    options:
      show_source: true
      members:
        - __init__
        - method1
        - method2
```

### Search Optimization

MkDocs indexes all content automatically. To improve searchability:

- Use clear headings
- Include keywords in descriptions
- Add synonyms in metadata

## Troubleshooting

### MkDocs not found

```bash
# Install mkdocs
pip install mkdocs mkdocs-material mkdocstrings[python]
```

### Module not found (mkdocstrings)

Ensure the project root is in Python path:

```yaml
# mkdocs.yml
plugins:
  - mkdocstrings:
      handlers:
        python:
          paths: [.]  # Current directory
```

### Port already in use

```bash
# Use different port
mkdocs serve --dev-addr=127.0.0.1:8001
```

### Build errors

```bash
# Verbose output
mkdocs build --verbose

# Clean and rebuild
mkdocs build --clean
```

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [MkDocstrings](https://mkdocstrings.github.io/)

## Need Help?

- Check [MkDocs User Guide](https://www.mkdocs.org/user-guide/)
- See [Material Theme Reference](https://squidfunk.github.io/mkdocs-material/reference/)
- Open an issue on GitHub
