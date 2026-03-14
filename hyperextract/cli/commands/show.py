"""Show command for Hyper-Extract CLI."""

import json

import typer
from rich.console import Console

from ..utils import (
    validate_config,
    validate_kb_with_data,
    create_template,
    get_template_from_kb,
)

console = Console()

app = typer.Typer(
    name="show",
    help="Show knowledge base visualization",
)


@app.command()
def main(
    kb_path: str = typer.Argument(..., help="Knowledge base directory"),
    build_index: bool = typer.Option(False, "--build-index", "-b", help="Build index"),
):
    """Show knowledge base visualization."""
    path = validate_kb_with_data(kb_path)

    template, lang = get_template_from_kb(path)

    console.print(f"[blue]Template:[/blue] {template}")
    console.print(f"[blue]Language:[/blue] {lang}")
    console.print()

    if build_index:
        validate_config()

    with console.status("[bold blue]Loading knowledge base..."):
        try:
            kb = create_template(template, lang)
            kb.load(path)

            if build_index:
                console.print("[blue]Building index...[/blue]")
                kb.build_index()
                kb.dump(path)

        except Exception as e:
            console.print(f"[red]Error loading knowledge base:[/red] {e}")
            raise typer.Exit(1)

    data_file = path / "data.json"
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    console.print(f"[green]Loaded {len(str(data))} chars of data[/green]")
    console.print()

    console.print("[bold blue]Visualizing...[/bold blue]")
    try:
        kb.show(
            node_label_extractor=lambda n: getattr(n, "name", str(n)),
            edge_label_extractor=lambda e: getattr(e, "relation", str(e)),
        )
    except Exception as e:
        console.print(f"[yellow]Warning: Could not show graph:[/yellow] {e}")
        console.print()
        console.print("[bold]Data preview:[/bold]")
        console.print_json(json.dumps(data, indent=2, ensure_ascii=False))
