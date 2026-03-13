"""Build-index command for Hyper-Extract CLI."""

from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

app = typer.Typer(
    name="build-index",
    help="Build vector index for knowledge base",
)


@app.command()
def main(
    kb_path: str = typer.Argument(..., help="Knowledge base directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Force rebuild"),
):
    """Build vector index for knowledge base."""
    from ..config import ConfigManager, load_kb_metadata
    
    path = Path(kb_path)

    if not path.exists():
        console.print(f"[red]Error:[/red] Knowledge base not found: {kb_path}")
        raise typer.Exit(1)

    if not path.is_dir():
        console.print(f"[red]Error:[/red] Not a directory: {kb_path}")
        raise typer.Exit(1)

    data_file = path / "data.json"
    if not data_file.exists():
        console.print(f"[red]Error:[/red] Not a valid knowledge base: {kb_path} (no data.json)")
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

    index_dir = path / "index"
    if index_dir.exists() and any(index_dir.iterdir()) and not force:
        console.print(f"[yellow]Warning:[/yellow] Index already exists. Use --force to rebuild.")
        console.print(f"[dim]Index location: {index_dir}[/dim]")
        raise typer.Exit(0)

    console.print(f"[blue]Template:[/blue] {template}")
    console.print(f"[blue]Language:[/blue] {lang}")
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Initializing...", total=None)

        try:
            from ..templates import resolve_template

            kb = resolve_template(template, lang)

            progress.update(task, description="Loading knowledge base...")
            kb.load(path)

            progress.update(task, description="Building index...")
            kb.build_index()

            progress.update(task, description="Saving index...")
            kb.dump(path)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print()
    console.print(f"[bold green]Success![/bold green] Index built for {kb_path}")
