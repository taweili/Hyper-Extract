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


def _get_description(cfg) -> str:
    """Get description from template config, handling both str and dict types."""
    desc = cfg.description
    if isinstance(desc, dict):
        return desc.get("zh", desc.get("en", ""))
    return desc or ""


@app.command(name="template")
def template(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Query to search templates"),
    autotype: Optional[str] = typer.Option(None, "--autotype", "-a", help="Filter by autotype"),
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Filter by language"),
    include_methods: bool = typer.Option(True, "--include-methods/--no-methods", help="Include method templates"),
):
    """List all available templates with detailed information."""
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
            templates.append((path, full_name, lang, cfg.type, _get_description(cfg)))

    if include_methods:
        from hyperextract.methods import list_method_cfgs
        method_templates = list_method_cfgs()
        for name, cfg in method_templates.items():
            templates.append((name, cfg.name, "en", cfg.type, cfg.description))

    if not templates:
        console.print("[yellow]No templates found.[/yellow]")
        return

    table = Table(
        title="Available Templates",
        show_header=True,
        header_style="bold magenta",
        expand=True,
    )
    table.add_column("Template ID", style="cyan", no_wrap=True, width=30)
    table.add_column("Name", style="green", width=20)
    table.add_column("Type", style="yellow", no_wrap=True, width=12)
    table.add_column("Language", style="magenta", no_wrap=True, width=8)
    table.add_column("Description", style="white")

    for tid, name, lang, template_type, desc in templates:
        desc_text = desc[:60] + "..." if len(desc) > 60 else desc
        table.add_row(tid, name, template_type, lang, desc_text)

    console.print(table)
    console.print(f"\n[dim]Total: {len(templates)} templates[/dim]")
    console.print()
    console.print("[dim]Type explanations:[/dim]")
    console.print("  [cyan]graph[/cyan] - Entity-relationship graph (binary relations)")
    console.print("  [cyan]hypergraph[/cyan] - Hypergraph (n-ary relations)")
    console.print("  [cyan]list[/cyan] - Key-value list")
    console.print("  [cyan]model[/cyan] - Structured data model")
    console.print("  [cyan]set[/cyan] - Entity collection")
    console.print()
    console.print("[dim]Tip: Use [bold]he parse <input> -t <template_id> -l <lang>[/bold] to extract with a template[/dim]")


@app.command(name="method")
def method(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Query to search methods"),
):
    """List all available extraction methods with detailed information."""
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

    table = Table(
        title="Available Methods",
        show_header=True,
        header_style="bold magenta",
        expand=True,
    )
    table.add_column("Method", style="cyan", no_wrap=True, width=18)
    table.add_column("Type", style="yellow", no_wrap=True, width=12)
    table.add_column("Description", style="green")

    for name, info in items.items():
        method_id = f"method/{name}"
        method_type = info["type"]
        description = info["description"]
        table.add_row(method_id, method_type, description)

    console.print(table)
    console.print(f"\n[dim]Total: {len(items)} methods[/dim]")
    console.print()
    console.print("[dim]Method explanations:[/dim]")
    console.print("  [cyan]graph[/cyan] - Binary relation graph (entity-relationship)")
    console.print("  [cyan]hypergraph[/cyan] - N-ary hypergraph (multi-entity relations)")
    console.print()
    console.print("[dim]Tip: Use [bold]he parse <input> -m <method_name>[/bold] to extract with a method[/dim]")
