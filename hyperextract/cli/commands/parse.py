"""Parse command for Hyper-Extract CLI."""

from pathlib import Path
from datetime import datetime

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils import (
    read_input,
    validate_config,
    create_template,
    get_template_config,
    get_auto_type_from_config,
)
from ..config import save_kb_metadata

console = Console()

app = typer.Typer(
    name="parse",
    help="Extract knowledge from text to a new directory",
)


@app.command()
def main(
    input: str = typer.Argument(..., help="Input file path or '-' for stdin"),
    output: str = typer.Option(..., "--output", "-o", help="Output directory"),
    template: str = typer.Option("knowledge_graph", "--template", "-t", help="Template"),
    lang: str = typer.Option("zh", "--lang", "-l", help="Language (zh/en)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite"),
):
    """Extract knowledge from text to a new directory."""
    validate_config()

    output_path = Path(output)

    if output_path.exists() and not force:
        if any(output_path.iterdir()):
            console.print(f"[red]Error:[/red] Output directory already exists and is not empty. Use --force to overwrite.")
            raise typer.Exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    console.print(f"[blue]Input:[/blue] {input}")
    console.print(f"[blue]Output:[/blue] {output}")
    console.print(f"[blue]Template:[/blue] {template}")
    console.print(f"[blue]Language:[/blue] {lang}")
    console.print()

    try:
        template_config = get_template_config(template, lang)
        if template_config is None:
            raise ValueError(f"Template '{template}' not found")
        console.print(f"[green]Template resolved:[/green] {template_config.name}")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Creating template instance...", total=None)
        
        kb = create_template(template, lang)
        
        progress.update(task, description="Reading input...")
        text = read_input(input)
        console.print(f"[dim]Input text: {len(text)} characters[/dim]")

        progress.update(task, description="Extracting knowledge...")
        kb.feed_text(text)

        progress.update(task, description="Saving data...")
        kb.dump(output_path)

        metadata = {
            "template": template,
            "lang": lang,
            "auto_type": get_auto_type_from_config(template_config),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        save_kb_metadata(output_path, metadata)

    console.print()
    console.print(f"[bold green]Success![/bold green] Knowledge extracted to {output_path}")
    console.print(f"[dim]Use 'he show {output}' to visualize[/dim]")
    console.print(f"[dim]Use 'he build-index {output}' to build search index[/dim]")
