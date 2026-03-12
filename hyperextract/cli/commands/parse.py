"""Parse command for Hyper-Extract CLI."""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import ConfigManager, save_kb_metadata
from ..templates import resolve_template, get_auto_type_from_template

console = Console()

app = typer.Typer(
    name="parse",
    help="Extract knowledge from text to a new directory",
)


def create_llm_client(config: ConfigManager):
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


def create_embedder(config: ConfigManager):
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
    template: str = typer.Option("knowledge_graph", "--template", "-t", help="Template"),
    lang: str = typer.Option("zh", "--lang", "-l", help="Language (zh/en)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite"),
):
    """Extract knowledge from text to a new directory."""
    from ..config import ConfigManager, save_kb_metadata
    from ..templates import resolve_template, get_auto_type_from_template
    
    config = ConfigManager()
    valid, msg = config.validate()
    if not valid:
        console.print(f"[red]Error:[/red] {msg}")
        raise typer.Exit(1)

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

        progress.update(task, description="Initializing template...")
        kb = template_class(llm_client=llm, embedder=embedder, verbose=True)

        progress.update(task, description="Extracting knowledge...")
        kb.feed_text(text)

        progress.update(task, description="Saving data...")
        kb.dump(output_path)

        metadata = {
            "template": template,
            "lang": lang,
            "auto_type": get_auto_type_from_template(template_class),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        save_kb_metadata(output_path, metadata)

    console.print()
    console.print(f"[bold green]Success![/bold green] Knowledge extracted to {output_path}")
    console.print(f"[dim]Use 'he show {output}' to visualize[/dim]")
    console.print(f"[dim]Use 'he build-index {output}' to build search index[/dim]")
