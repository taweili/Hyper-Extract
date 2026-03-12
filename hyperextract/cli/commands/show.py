"""Show command for Hyper-Extract CLI."""

from pathlib import Path
import json

import typer
from rich.console import Console

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

    console.print(f"[blue]Template:[/blue] {template}")
    console.print(f"[blue]Language:[/blue] {lang}")
    console.print()

    config = ConfigManager()
    valid, msg = config.validate()
    if not valid and build_index:
        console.print(f"[red]Error:[/red] {msg}")
        raise typer.Exit(1)

    with console.status("[bold blue]Loading knowledge base..."):
        try:
            from ..templates import resolve_template

            template_class = resolve_template(template, lang)
            llm = None
            embedder = None

            if build_index:
                valid, msg = config.validate()
                if not valid:
                    console.print(f"[yellow]Warning:[/yellow] Skipping index build: {msg}")
                else:
                    from .feed import create_llm_client, create_embedder
                    llm = create_llm_client(config)
                    embedder = create_embedder(config)

            kb = template_class(llm_client=llm, embedder=embedder)
            kb.load(path)

            if build_index:
                console.print("[blue]Building index...[/blue]")
                kb.build_index()
                kb.dump(path)

        except Exception as e:
            console.print(f"[red]Error loading knowledge base:[/red] {e}")
            raise typer.Exit(1)

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
