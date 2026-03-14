"""Talk command for Hyper-Extract CLI."""

from typing import Optional

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
    name="talk",
    help="Chat with knowledge base",
)


def chat_loop(kb):
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
    validate_config()

    path = validate_kb_with_index(kb_path)
    template, lang = get_template_from_kb(path)

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
            kb = create_template(template, lang)

            progress.update(task, description="Loading knowledge base...")
            kb.load(path)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if interactive:
        chat_loop(kb)
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
