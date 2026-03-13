"""CLI entry point for Hyper-Extract."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .commands.config import app as config_app
from .commands.list import app as list_app
from .commands.parse import app as parse_app
from .commands.feed import app as feed_app
from .commands.show import app as show_app
from .commands.build_index import app as build_index_app
from .commands.search import app as search_app
from .commands.talk import app as talk_app

console = Console()

app = typer.Typer(
    name="he",
    help="Hyper-Extract CLI - A command-line tool for knowledge extraction",
    add_completion=False,
    invoke_without_command=True,
)

app.add_typer(config_app, name="config")
app.add_typer(list_app, name="list")
app.add_typer(parse_app, name="parse")
app.add_typer(feed_app, name="feed")
app.add_typer(show_app, name="show")
app.add_typer(build_index_app, name="build-index")
app.add_typer(search_app, name="search")
app.add_typer(talk_app, name="talk")


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version information",
        is_eager=True,
    ),
):
    """Hyper-Extract CLI - Transform unstructured text into structured knowledge."""
    if version:
        from . import __version__
        console.print(f"[bold]Hyper-Extract CLI[/bold] version {__version__}")
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        welcome_text = Text("Welcome to Hyper-Extract CLI!", style="bold cyan")
        desc_text = Text("A command-line tool for knowledge extraction from unstructured text.")
        
        table = Table(box=None, show_header=False, pad_edge=False)
        table.add_column(style="green")
        table.add_column()
        
        table.add_row("he parse", "<input> -o <output>", "Extract knowledge from text")
        table.add_row("he list", "template", "List available templates")
        table.add_row("he show", "<kb_path>", "Visualize knowledge base")
        table.add_row("he search", "<query> -k <kb>", "Semantic search in knowledge base")
        table.add_row("he talk", "-k <kb>", "Chat with knowledge base")
        table.add_row("he config", "--help", "Manage LLM and Embedder configuration")
        table.add_row("he feed", "-k <kb>", "Feed knowledge into knowledge base")
        table.add_row("he build-index", "-k <kb>", "Build search index for knowledge base")
        
        panel = Panel(
            table,
            title="Quick Start",
            border_style="cyan",
            padding=(1, 2),
        )
        
        console.print()
        console.print(welcome_text)
        console.print()
        console.print(desc_text)
        console.print()
        console.print(panel)
        console.print()
        console.print("Run [bold]he --help[/bold] for more information.")
        raise typer.Exit()
