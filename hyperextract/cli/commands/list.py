"""List command for Hyper-Extract CLI."""

from typing import Optional
from rich.console import Console
from rich.table import Table
import typer

from hyperextract.utils.template_engine import Gallery

console = Console()

app = typer.Typer(
    name="list",
    help="List available resources",
)

METHODS = [
    ("kg_gen", "Knowledge Graph Generation"),
    ("atom", "Atomic Information Extraction"),
    ("itext2kg", "iText2KG - Iterative Knowledge Graph Construction"),
    ("itext2kg_star", "iText2KG-Star - Star-shaped Knowledge Graph"),
    ("light_rag", "LightRAG - Lightweight Graph RAG"),
    ("hyper_rag", "HyperRAG - Hypergraph RAG"),
    ("cog_rag", "CogRAG - Cognitive RAG"),
    ("hypergraph_rag", "Hypergraph RAG"),
]


@app.command(name="template")
def template(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Query to search templates"),
    autotype: Optional[str] = typer.Option(None, "--autotype", "-a", help="Filter by autotype"),
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Filter by language"),
):
    """List all available templates."""
    results = Gallery.list(
        filter_by_query=query,
        filter_by_type=autotype,
        filter_by_language=language,
    )

    templates = []
    for path, cfg in results.items():
        full_name = cfg.name
        languages = cfg.language if cfg.language else ["zh"]
        if isinstance(languages, str):
            languages = [languages]

        for lang in languages:
            templates.append((path, full_name, lang))

    if not templates:
        console.print("[yellow]No templates found.[/yellow]")
        return

    table = Table(title="Available Templates", show_header=True, header_style="bold magenta")
    table.add_column("Template ID", style="cyan", width=30)
    table.add_column("Name", style="green", width=30)
    table.add_column("Language", style="yellow", width=10)

    for tid, name, lang in templates:
        table.add_row(tid, name, lang)

    console.print(table)
    console.print(f"\n[dim]Total: {len(templates)} templates[/dim]")
    console.print("\n[dim]Tip: Use -t/--template to specify a template.[/dim]")


@app.command(name="method")
def method(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Query to search methods"),
):
    """List all available extraction methods."""
    items = METHODS

    if query:
        query_lower = query.lower()
        items = [
            item for item in items
            if query_lower in item[0].lower() or query_lower in item[1].lower()
        ]

    if not items:
        console.print("[yellow]No methods found.[/yellow]")
        return

    table = Table(title="Available Methods", show_header=True, header_style="bold magenta")
    table.add_column("Method", style="cyan", width=20)
    table.add_column("Description", style="green")

    for name, desc in items:
        table.add_row(name, desc)

    console.print(table)
    console.print(f"\n[dim]Total: {len(items)} methods[/dim]")
