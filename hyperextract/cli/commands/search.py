"""Search command for Hyper-Extract CLI."""

from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

app = typer.Typer(
    name="search",
    help="Semantic search in knowledge base",
)


@app.command()
def main(
    query: str = typer.Argument(..., help="Search query"),
    kb_path: str = typer.Option(..., "--kb", "-k", help="Knowledge base directory"),
    top_k: int = typer.Option(3, "--top-k", "-n", help="Number of results"),
):
    """Semantic search in knowledge base."""
    from ..config import ConfigManager, load_kb_metadata
    from ..templates import resolve_template
    
    path = Path(kb_path)

    if not path.exists():
        console.print(f"[red]Error:[/red] Knowledge base not found: {kb_path}")
        raise typer.Exit(1)

    if not path.is_dir():
        console.print(f"[red]Error:[/red] Not a directory: {kb_path}")
        raise typer.Exit(1)

    index_dir = path / "index"
    if not index_dir.exists() or not any(index_dir.iterdir()):
        console.print(f"[red]Error:[/red] Index not found. Please run 'he build-index {kb_path}' first.")
        raise typer.Exit(1)

    metadata = load_kb_metadata(path)
    if not metadata:
        console.print(f"[yellow]Warning:[/yellow] No metadata found, assuming knowledge_graph")
        template = "knowledge_graph"
        lang = "zh"
    else:
        template = metadata.get("template", "knowledge_graph")
        lang = metadata.get("lang", "zh")

    config = ConfigManager()
    valid, msg = config.validate()
    if not valid:
        console.print(f"[red]Error:[/red] {msg}")
        raise typer.Exit(1)

    console.print(f"[blue]Query:[/blue] {query}")
    console.print(f"[blue]Knowledge base:[/blue] {kb_path}")
    console.print(f"[blue]Top K:[/blue] {top_k}")
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Searching...", total=None)

        try:
            kb = resolve_template(template, lang)

            progress.update(task, description="Loading knowledge base...")
            kb.load(path)

            progress.update(task, description="Searching...")
            results = kb.search(query, top_k=top_k)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print()
    if not results:
        console.print("[yellow]No results found.[/yellow]")
    else:
        console.print(f"[bold green]Found {len(results)} result(s):[/bold green]")
        console.print()

        for i, result in enumerate(results, 1):
            console.print(f"[bold cyan]Result {i}:[/bold cyan]")
            if hasattr(result, "model_dump"):
                import json
                console.print_json(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
            elif hasattr(result, "dict"):
                import json
                console.print_json(json.dumps(result.dict(), indent=2, ensure_ascii=False))
            else:
                console.print(str(result))
            console.print()
