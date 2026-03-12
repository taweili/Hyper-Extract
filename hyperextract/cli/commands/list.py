"""List command for Hyper-Extract CLI."""

from typing import Optional
from rich.console import Console
from rich.table import Table
import typer

console = Console()

app = typer.Typer(
    name="list",
    help="List available resources",
)


AUTOTYPES = [
    ("AutoModel", "Extract into a complete data model"),
    ("AutoList", "Extract as a list (keywords, items)"),
    ("AutoSet", "Extract and deduplicate (entity registry)"),
    ("AutoGraph", "Extract as a knowledge graph (relations)"),
    ("AutoTemporalGraph", "Extract as timeline (events over time)"),
    ("AutoSpatialGraph", "Extract as spatial graph (locations)"),
    ("AutoSpatioTemporalGraph", "Extract as spatiotemporal graph (time + space)"),
    ("AutoHypergraph", "Extract as hypergraph (multi-party relations)"),
]

DOMAINS = [
    ("finance", "Financial documents (25+ templates)"),
    ("medicine", "Medical documents (20+ templates)"),
    ("legal", "Legal documents (15+ templates)"),
    ("history", "Historical documents (12+ templates)"),
    ("literature", "Literature works (10+ templates)"),
    ("tcm", "Traditional Chinese Medicine (15+ templates)"),
    ("news", "News articles (12+ templates)"),
    ("biology", "Biological documents (10+ templates)"),
    ("industry", "Industrial documents (18+ templates)"),
    ("agriculture", "Agricultural documents (8+ templates)"),
    ("food", "Food and culinary (8+ templates)"),
    ("general", "General purpose (20+ templates)"),
]

METHODS = [
    ("kg_gen", "Knowledge Graph Generation"),
    ("atom", "Atomic Information Extraction"),
    ("graphiti", "Graphiti - Temporal Knowledge Graph"),
    ("light_rag", "LightRAG - Lightweight Graph RAG"),
    ("hyper_rag", "HyperRAG - Hypergraph RAG"),
    ("cog_rag", "CogRAG - Cognitive RAG"),
    ("hypergraph_rag", "Hypergraph RAG"),
]


def _get_all_templates() -> list:
    """Get all available templates from hyperextract."""
    templates = []
    try:
        from hyperextract.templates import zh, en
        for name in dir(zh):
            if not name.startswith("_"):
                templates.append((f"zh/{name}", name, "Chinese"))
        for name in dir(en):
            if not name.startswith("_"):
                templates.append((f"en/{name}", name, "English"))
        return templates
    except ImportError:
        return []


def _filter_items(items: list, search: Optional[str]) -> list:
    """Filter items by search keyword."""
    if not search:
        return items
    search_lower = search.lower()
    return [
        item for item in items
        if any(search_lower in str(field).lower() for field in item)
    ]


@app.command(name="autotype")
def autotype(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search autotypes"),
):
    """List all available AutoTypes."""
    items = _filter_items(AUTOTYPES, search)
    
    table = Table(title="Available AutoTypes", show_header=True, header_style="bold magenta")
    table.add_column("AutoType", style="cyan", width=25)
    table.add_column("Description", style="green")
    
    for name, desc in items:
        table.add_row(name, desc)
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(items)} AutoTypes[/dim]")


@app.command(name="template")
def template(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search templates"),
):
    """List all available templates."""
    templates = _get_all_templates()
    items = _filter_items(templates, search)
    
    table = Table(title="Available Templates", show_header=True, header_style="bold magenta")
    table.add_column("Template ID", style="cyan", width=30)
    table.add_column("Name", style="green", width=30)
    table.add_column("Language", style="yellow", width=10)
    
    for tid, name, lang in items:
        table.add_row(tid, name, lang)
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(items)} templates[/dim]")
    console.print("\n[dim]Tip: Use -t/--template to specify a template.[/dim]")


@app.command(name="domain")
def domain(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search domains"),
):
    """List all available domains."""
    items = _filter_items(DOMAINS, search)
    
    table = Table(title="Available Domains", show_header=True, header_style="bold magenta")
    table.add_column("Domain", style="cyan", width=20)
    table.add_column("Description", style="green")
    
    for name, desc in items:
        table.add_row(name, desc)
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(items)} domains[/dim]")


@app.command(name="method")
def method(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search methods"),
):
    """List all available extraction methods."""
    items = _filter_items(METHODS, search)
    
    table = Table(title="Available Methods", show_header=True, header_style="bold magenta")
    table.add_column("Method", style="cyan", width=20)
    table.add_column("Description", style="green")
    
    for name, desc in items:
        table.add_row(name, desc)
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(items)} methods[/dim]")
