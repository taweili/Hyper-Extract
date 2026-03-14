"""Search command for Hyper-Extract CLI."""

import json

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils import (
    validate_config,
    validate_kb_with_index,
    create_template,
    get_template_from_kb,
)

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
    validate_config()

    path = validate_kb_with_index(kb_path)
    template, lang = get_template_from_kb(path)

    console.print(f"[blue]Query:[/blue] {query}")
    console.print(f"[blue]Knowledge base:[/blue] {kb_path}")
    console.print(f"[blue]Top K:[/blue] {top_k}")
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Searching...", total=None)

        try:
            kb = create_template(template, lang)

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
                console.print_json(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
            elif hasattr(result, "dict"):
                console.print_json(json.dumps(result.dict(), indent=2, ensure_ascii=False))
            else:
                console.print(str(result))
            console.print()
