"""Feed command for Hyper-Extract CLI."""

from pathlib import Path
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils import (
    read_input,
    validate_config,
    validate_kb_path,
    create_template,
    get_template_from_kb,
)
from ..config import load_kb_metadata, save_kb_metadata

console = Console()

app = typer.Typer(
    name="feed",
    help="Append knowledge to an existing directory",
)


@app.command()
def main(
    input: str = typer.Argument(..., help="Input file path or '-' for stdin"),
    output: str = typer.Option(..., "--output", "-o", help="Output directory"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Template"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l", help="Language"),
):
    """Append knowledge to an existing directory."""
    validate_config()

    output_path = validate_kb_path(output)

    metadata = load_kb_metadata(output_path)
    if not metadata:
        console.print(f"[red]Error:[/red] Not a valid knowledge base directory: {output}")
        raise typer.Exit(1)

    if template is None:
        template = metadata.get("template", "knowledge_graph")
    if lang is None:
        lang = metadata.get("lang", "zh")

    console.print(f"[blue]Input:[/blue] {input}")
    console.print(f"[blue]Output:[/blue] {output}")
    console.print(f"[blue]Template:[/blue] {template} (from metadata)")
    console.print(f"[blue]Language:[/blue] {lang} (from metadata)")
    console.print()

    try:
        kb = create_template(template, lang)
        console.print(f"[green]Template loaded:[/green] {template}")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Loading existing knowledge...", total=None)
        
        kb.load(output_path)

        progress.update(task, description="Reading input...")
        text = read_input(input)
        console.print(f"[dim]Input text: {len(text)} characters[/dim]")

        progress.update(task, description="Appending knowledge...")
        kb.feed_text(text)

        progress.update(task, description="Saving data...")
        kb.dump(output_path)

        metadata["updated_at"] = datetime.now().isoformat()
        save_kb_metadata(output_path, metadata)

    console.print()
    console.print(f"[bold green]Success![/bold green] Knowledge appended to {output_path}")
