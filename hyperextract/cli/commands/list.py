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


@app.command(name="template")
def template(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Query to search templates"),
    autotype: Optional[str] = typer.Option(None, "--autotype", "-a", help="Filter by autotype"),
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Filter by language"),
    include_methods: bool = typer.Option(True, "--include-methods/--no-methods", help="Include method templates"),
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

    if include_methods:
        from hyperextract.methods import list_method_cfgs
        method_templates = list_method_cfgs()
        for name, cfg in method_templates.items():
            templates.append((name, cfg.name, "en"))

    if not templates:
        console.print("[yellow]No templates found.[/yellow]")
        return

    table = Table(title="Available Templates", show_header=True, header_style="bold magenta")
    table.add_column("Template ID", style="cyan", width=35)
    table.add_column("Name", style="green", width=30)
    table.add_column("Language", style="yellow", width=10)

    for tid, name, lang in templates:
        table.add_row(tid, name, lang)

    console.print(table)
    console.print(f"\n[dim]Total: {len(templates)} templates[/dim]")
    console.print("\n[dim]Tip: Use -t/--template to specify a template, or -m/--method for methods.[/dim]")


@app.command(name="method")
def method(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Query to search methods"),
):
    """List all available extraction methods."""
    from hyperextract.methods import list_methods

    items = list_methods()

    if query:
        query_lower = query.lower()
        items = {
            k: v for k, v in items.items()
            if query_lower in k.lower() or query_lower in v.get("description", "").lower()
        }

    if not items:
        console.print("[yellow]No methods found.[/yellow]")
        return

    table = Table(title="Available Methods", show_header=True, header_style="bold magenta")
    table.add_column("Method", style="cyan", width=20)
    table.add_column("Type", style="yellow", width=15)
    table.add_column("Description", style="green")

    for name, info in items.items():
        table.add_row(f"method/{name}", info["type"], info["description"])

    console.print(table)
    console.print(f"\n[dim]Total: {len(items)} methods[/dim]")
    console.print("\n[dim]Tip: Use -m/--method to specify a method template.[/dim]")
