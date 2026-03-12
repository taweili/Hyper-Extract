"""Talk command for Hyper-Extract CLI."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

app = typer.Typer(
    name="talk",
    help="Chat with knowledge base",
)


def chat_loop(kb, config):
    """Interactive chat loop."""
    console.print("\n[bold green]Entering interactive mode. Type 'exit' or 'quit' to stop.[/bold green]\n")
    while True:
        try:
            query = console.input("[bold cyan]>[/bold cyan] ")
            if query.lower() in ["exit", "quit", "q"]:
                console.print("[dim]Goodbye![/dim]")
                break
            if not query.strip():
                continue
            response = kb.chat(query)
            console.print()
            console.print(response.content)
            console.print()
        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye![/dim]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


@app.command()
def main(
    query: Optional[str] = typer.Argument(None, help="Question to ask"),
    kb_path: str = typer.Option(..., "--kb", "-k", help="Knowledge base directory"),
    top_k: int = typer.Option(3, "--top-k", "-n", help="Number of context items"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
):
    """Chat with knowledge base."""
    from ..config import ConfigManager, load_kb_metadata
    
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

    if interactive:
        console.print(f"[blue]Knowledge base:[/blue] {kb_path}")
        console.print(f"[blue]Template:[/blue] {template}")
        console.print(f"[blue]Top K:[/blue] {top_k}")
        console.print()
    elif query is None:
        console.print(f"[red]Error:[/red] Please provide a query or use --interactive mode")
        raise typer.Exit(1)
    else:
        console.print(f"[blue]Query:[/blue] {query}")
        console.print(f"[blue]Knowledge base:[/blue] {kb_path}")
        console.print(f"[blue]Top K:[/blue] {top_k}")
        console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Loading...", total=None)

        try:
            from ..templates import resolve_template
            from .feed import create_llm_client, create_embedder

            template_class = resolve_template(template, lang)
            llm = create_llm_client(config)
            embedder = create_embedder(config)

            progress.update(task, description="Loading knowledge base...")
            kb = template_class(llm_client=llm, embedder=embedder)
            kb.load(path)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if interactive:
        chat_loop(kb, config)
    else:
        with console.status("[bold blue]Thinking..."):
            try:
                response = kb.chat(query, top_k=top_k)
                console.print(response.content)

                if response.additional_kwargs.get("retrieved_items"):
                    console.print()
                    console.print("[dim]Retrieved context:[/dim]")
                    items = response.additional_kwargs["retrieved_items"]
                    for i, item in enumerate(items, 1):
                        console.print(f"[dim]{i}. {str(item)[:100]}...[/dim]")
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)
