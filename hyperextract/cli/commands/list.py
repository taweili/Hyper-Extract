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
    ("finance", "Financial documents"),
    ("medicine", "Medical documents"),
    ("legal", "Legal documents"),
    ("history", "Historical documents"),
    ("literature", "Literature works"),
    ("tcm", "Traditional Chinese Medicine"),
    ("news", "News articles"),
    ("biology", "Biological documents"),
    ("industry", "Industrial documents"),
    ("agriculture", "Agricultural documents"),
    ("food", "Food and culinary"),
    ("general", "General purpose"),
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


def _get_domains_from_configs() -> list:
    """Get domains from configs directory."""
    try:
        from ..templates import get_domains
        return get_domains()
    except Exception:
        return []


@app.command(name="autotype")
def autotype(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search autotypes"),
):
    """List all available AutoTypes."""
    from hyperextract.utils.template_engine import Gallery
    
    autotypes = Gallery.list_autotypes()
    
    if search:
        search_lower = search.lower()
        autotypes = [a for a in autotypes if search_lower in a.lower()]
    
    table = Table(title="Available AutoTypes", show_header=True, header_style="bold magenta")
    table.add_column("AutoType", style="cyan", width=25)
    table.add_column("Description", style="green")
    
    autotype_descriptions = dict(AUTOTYPES)
    for name in autotypes:
        desc = autotype_descriptions.get(name, "")
        table.add_row(name, desc)
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(autotypes)} AutoTypes[/dim]")


@app.command(name="template")
def template(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search templates by name"),
    autotype: Optional[str] = typer.Option(None, "--autotype", "-a", help="Filter by autotype"),
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Filter by language"),
):
    """List all available templates."""
    from hyperextract.utils.template_engine import Gallery
    
    results = Gallery.search(query=search, autotype=autotype, language=language)
    
    templates = []
    for cfg in results:
        full_name = cfg.name
        languages = cfg.language if cfg.language else ["zh"]
        if isinstance(languages, str):
            languages = [languages]
        
        for lang in languages:
            templates.append((full_name, full_name, lang))
    
    table = Table(title="Available Templates", show_header=True, header_style="bold magenta")
    table.add_column("Template ID", style="cyan", width=30)
    table.add_column("Name", style="green", width=30)
    table.add_column("Language", style="yellow", width=10)
    
    for tid, name, lang in templates:
        table.add_row(tid, name, lang)
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(templates)} templates[/dim]")
    console.print("\n[dim]Tip: Use -t/--template to specify a template.[/dim]")


@app.command(name="domain")
def domain(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search domains"),
):
    """List all available domains."""
    domains = _get_domains_from_configs()
    
    domain_descriptions = dict(DOMAINS)
    
    items = []
    for name, count in domains:
        desc = domain_descriptions.get(name, f"{name} documents")
        items.append((name, f"{desc} ({count} templates)"))
    
    if search:
        search_lower = search.lower()
        items = [
            item for item in items
            if search_lower in item[0].lower() or search_lower in item[1].lower()
        ]
    
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
    items = METHODS
    
    if search:
        search_lower = search.lower()
        items = [
            item for item in items
            if search_lower in item[0].lower() or search_lower in item[1].lower()
        ]
    
    table = Table(title="Available Methods", show_header=True, header_style="bold magenta")
    table.add_column("Method", style="cyan", width=20)
    table.add_column("Description", style="green")
    
    for name, desc in items:
        table.add_row(name, desc)
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(items)} methods[/dim]")
