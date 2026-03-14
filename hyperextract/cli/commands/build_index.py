"""Build-index command for Hyper-Extract CLI."""

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils import (
    validate_config,
    validate_kb_with_data,
    create_template,
    get_template_from_kb,
)

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
    validate_config()

    path = validate_kb_with_data(kb_path)

    index_dir = path / "index"
    if index_dir.exists() and any(index_dir.iterdir()) and not force:
        console.print(f"[yellow]Warning:[/yellow] Index already exists. Use --force to rebuild.")
        console.print(f"[dim]Index location: {index_dir}[/dim]")
        raise typer.Exit(0)

    template, lang = get_template_from_kb(path)

    console.print(f"[blue]Template:[/blue] {template}")
    console.print(f"[blue]Language:[/blue] {lang}")
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Initializing...", total=None)

        try:
            kb = create_template(template, lang)

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
