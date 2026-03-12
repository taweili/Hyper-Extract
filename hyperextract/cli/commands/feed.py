"""Feed command for Hyper-Extract CLI."""

from pathlib import Path
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

app = typer.Typer(
    name="feed",
    help="Append knowledge to an existing directory",
)


def create_llm_client(config):
    """Create LLM client from config."""
    llm_config = config.get_llm_config()
    if llm_config.provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=llm_config.model,
            api_key=llm_config.api_key,
            base_url=llm_config.base_url or None,
            temperature=0,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_config.provider}")


def create_embedder(config):
    """Create embedder from config."""
    emb_config = config.get_embedder_config()
    if emb_config.provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=emb_config.model,
            api_key=emb_config.api_key,
            base_url=emb_config.base_url or None,
        )
    else:
        raise ValueError(f"Unsupported Embedder provider: {emb_config.provider}")


def read_input(input_path: str) -> str:
    """Read input from file or stdin."""
    import sys
    if input_path == "-":
        return sys.stdin.read()
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@app.command()
def main(
    input: str = typer.Argument(..., help="Input file path or '-' for stdin"),
    output: str = typer.Option(..., "--output", "-o", help="Output directory"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Template"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l", help="Language"),
):
    """Append knowledge to an existing directory."""
    from ..config import ConfigManager, load_kb_metadata
    from ..templates import resolve_template
    
    config = ConfigManager()
    valid, msg = config.validate()
    if not valid:
        console.print(f"[red]Error:[/red] {msg}")
        raise typer.Exit(1)

    output_path = Path(output)

    if not output_path.exists():
        console.print(f"[red]Error:[/red] Output directory does not exist: {output}")
        raise typer.Exit(1)

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
        template_class = resolve_template(template, lang)
        console.print(f"[green]Template resolved:[/green] {template_class.__name__}")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Initializing LLM client...", total=None)
        llm = create_llm_client(config)
        embedder = create_embedder(config)

        progress.update(task, description="Reading input...")
        text = read_input(input)
        console.print(f"[dim]Input text: {len(text)} characters[/dim]")

        progress.update(task, description="Loading existing knowledge...")
        kb = template_class(llm_client=llm, embedder=embedder, verbose=True)
        kb.load(output_path)

        progress.update(task, description="Appending knowledge...")
        kb.feed_text(text)

        progress.update(task, description="Saving data...")
        kb.dump(output_path)

        metadata["updated_at"] = datetime.now().isoformat()
        from ..config import save_kb_metadata
        save_kb_metadata(output_path, metadata)

    console.print()
    console.print(f"[bold green]Success![/bold green] Knowledge appended to {output_path}")
