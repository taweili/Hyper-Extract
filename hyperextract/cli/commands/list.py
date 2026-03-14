"""List command for Hyper-Extract CLI."""

from typing import Optional
from rich.console import Console
from rich.table import Table
import typer

from hyperextract.utils.template_engine import Gallery, Template

from ..utils import (
    get_autotype_description,
    get_domain_description,
    AUTOTYPE_MAP,
)

console = Console()

app = typer.Typer(
    name="list",
    help="List available resources",
)


METHODS = [
    ("kg_gen", "Knowledge Graph Generation"),
    ("atom", "Atomic Information Extraction"),
    ("graphiti", "Graphiti - Temporal Knowledge Graph"),
    ("light_rag", "LightRAG - Lightweight Graph RAG"),
    ("hyper_rag", "HyperRAG - Hypergraph RAG"),
    ("cog_rag", "CogRAG - Cognitive RAG"),
    ("hypergraph_rag", "Hypergraph RAG"),
]


@app.command(name="autotype")
def autotype(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search autotypes"),
):
    """List all available AutoTypes."""
    autotypes = Gallery.list_autotypes()
    
    if search:
        search_lower = search.lower()
        autotypes = [a for a in autotypes if search_lower in a.lower()]
    
    table = Table(title="Available AutoTypes", show_header=True, header_style="bold magenta")
    table.add_column("AutoType", style="cyan", width=25)
    table.add_column("Description", style="green")
    
    for name in autotypes:
        display_name = AUTOTYPE_MAP.get(name, name)
        desc = get_autotype_description(display_name)
        table.add_row(display_name, desc)
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(autotypes)} AutoTypes[/dim]")


@app.command(name="template")
def template(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search templates by name"),
    autotype: Optional[str] = typer.Option(None, "--autotype", "-a", help="Filter by autotype"),
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Filter by language"),
):
    """List all available templates."""
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
    domains = Template.domains()
    
    items = []
    for name, count in domains:
        desc = get_domain_description(name)
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
