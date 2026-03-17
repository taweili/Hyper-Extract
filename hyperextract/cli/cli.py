"""CLI entry point for Hyper-Extract."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from hyperextract.utils.template_engine import Gallery, Template

from .utils import (
    read_input,
    validate_config,
    validate_kb_path,
    validate_kb_with_data,
    validate_kb_with_index,
    get_template_from_kb,
)
from .config import (
    load_kb_metadata,
)

from .commands import list_app, config_app

console = Console()

app = typer.Typer(
    name="he",
    help="Hyper-Extract CLI - A command-line tool for knowledge extraction",
    add_completion=False,
    invoke_without_command=True,
)

app.add_typer(list_app, name="list")
app.add_typer(config_app, name="config")


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
        table.add_column()

        table.add_row("he parse", "<input> -o <output>", "Extract knowledge (auto-builds index)")
        table.add_row("he list", "template", "List available templates")
        table.add_row("he list", "method", "List extraction methods")
        table.add_row("he show", "<kb_path>", "Visualize knowledge base")
        table.add_row("he info", "<kb_path>", "View knowledge base info")
        table.add_row("he search", "<query> -k <kb>", "Semantic search in knowledge base")
        table.add_row("he talk", "<kb_path>", "Chat with knowledge base")
        table.add_row("he config", "--help", "Manage LLM and Embedder configuration")
        table.add_row("he feed", "-k <kb>", "Feed knowledge into knowledge base")
        table.add_row("he build-index", "<kb_path>", "Build search index for knowledge base")

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


def select_template_interactive() -> Optional[str]:
    """Interactive template selection when user doesn't specify one."""
    templates = Gallery.list()

    if not templates:
        console.print("[yellow]No templates available.[/yellow]")
        return None

    template_list = list(templates.items())

    console.print()
    console.print("[bold cyan]Select a template:[/bold cyan]")
    console.print()

    for i, (path, cfg) in enumerate(template_list, 1):
        desc = cfg.description if cfg.description else ""
        if isinstance(desc, dict):
            desc = desc.get("zh", desc.get("en", ""))
        console.print(f"  [{i}] {path}")
        if desc:
            console.print(f"      {desc}")

    console.print()

    while True:
        choice = Prompt.ask(
            "Enter number or search keyword",
            default="1",
            show_default=True,
        )

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(template_list):
                return template_list[idx][0]
            else:
                console.print(f"[red]Invalid number. Please choose 1-{len(template_list)}[/red]")
        else:
            query_lower = choice.lower()
            matches = [(i, p, c) for i, (p, c) in enumerate(template_list)
                      if query_lower in p.lower() or
                      (c.description and query_lower in str(c.description).lower())]

            if len(matches) == 1:
                return matches[0][1]
            elif len(matches) > 1:
                console.print(f"[yellow]Found {len(matches)} matches:[/yellow]")
                for i, path, cfg in matches:
                    console.print(f"  [{i+1}] {path}")
                continue
            else:
                console.print("[yellow]No matches found. Try another keyword.[/yellow]")


@app.command(name="parse")
def parse(
    input: str = typer.Argument(..., help="Input file path, directory, or '-' for stdin"),
    output: str = typer.Option(..., "--output", "-o", help="Output directory"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Template (omit for interactive selection)"),
    method: Optional[str] = typer.Option(None, "--method", "-m", help="Method template (e.g., light_rag, hyper_rag)"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l", help="Language (zh/en). Required for knowledge templates, optional for methods (default: en)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite"),
    no_index: bool = typer.Option(False, "--no-index", help="Skip building search index"),
):
    """Extract knowledge from text to a new directory."""
    validate_config()

    if method:
        template = f"method/{method}"
    elif template is None:
        template = select_template_interactive()
        if template is None:
            console.print("[red]No template selected. Exiting.[/red]")
            raise typer.Exit(1)

    is_method_template = template.startswith("method/")

    if is_method_template:
        if lang is not None:
            console.print("[dim]Note: Method templates use English prompts. --lang parameter is ignored.[/dim]")
        lang = "en"
    elif lang is None:
        console.print("[red]Error:[/red] --lang is required for knowledge templates. Use --lang en or --lang zh.")
        raise typer.Exit(1)

    output_path = Path(output)

    if output_path.exists() and not force:
        if any(output_path.iterdir()):
            console.print("[red]Error:[/red] Output directory already exists and is not empty. Use --force to overwrite.")
            raise typer.Exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    console.print(f"[blue]Input:[/blue] {input}")
    console.print(f"[blue]Output:[/blue] {output}")
    console.print(f"[blue]Template:[/blue] {template}")
    console.print(f"[blue]Language:[/blue] {lang}")
    console.print(f"[blue]Build Index:[/blue] {'No' if no_index else 'Yes'}")
    console.print()

    try:
        template_config = Template.get(template)
        if template_config is None:
            raise ValueError(f"Template '{template}' not found")
        console.print(f"[green]Template resolved:[/green] {template_config.name}")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    input_path = Path(input)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Creating template instance...", total=None)

        kb = Template.create(template, lang)

        if input_path.is_dir():
            progress.update(task, description="Processing directory...")
            text_files = list(input_path.glob("*.txt")) + list(input_path.glob("*.md"))
            if not text_files:
                console.print(f"[red]Error:[/red] No .txt or .md files found in {input}")
                raise typer.Exit(1)

            all_text = []
            for file_path in text_files:
                text = read_input(str(file_path))
                all_text.append(text)
                console.print(f"[dim]Loaded {file_path.name}: {len(text)} chars[/dim]")

            combined_text = "\n\n".join(all_text)
            console.print(f"[dim]Total input: {len(combined_text)} characters[/dim]")

            progress.update(task, description="Extracting knowledge...")
            kb.feed_text(combined_text)
        else:
            progress.update(task, description="Reading input...")
            text = read_input(input)
            console.print(f"[dim]Input text: {len(text)} characters[/dim]")

            progress.update(task, description="Extracting knowledge...")
            kb.feed_text(text)

        progress.update(task, description="Saving data...")
        kb.dump(output_path)

        if not no_index:
            progress.update(task, description="Building search index...")
            kb.build_index()
            progress.update(task, description="Saving index...")
            kb.dump(output_path)

    console.print()
    console.print(f"[bold green]Success![/bold green] Knowledge extracted to {output_path}")
    if no_index:
        console.print(f"[dim]Note: Index was not built. Run 'he build-index {output}' to enable search/talk.[/dim]")
    else:
        console.print("[dim]Index built. You can now use 'he search' and 'he talk'.[/dim]")
    console.print(f"[dim]Use 'he show {output}' to visualize[/dim]")


@app.command(name="show")
def show(kb_path: str = typer.Argument(..., help="Knowledge base directory")):
    """Visualize knowledge base using OntoSight."""
    path = validate_kb_with_data(kb_path)

    template, lang = get_template_from_kb(path)

    console.print(f"[blue]Template:[/blue] {template}")
    console.print(f"[blue]Language:[/blue] {lang}")
    console.print()

    validate_config()

    with console.status("[bold blue]Loading knowledge base..."):
        try:
            kb = Template.create(template, lang)
            kb.load(path)

        except Exception as e:
            console.print(f"[red]Error loading knowledge base:[/red] {e}")
            raise typer.Exit(1)

    console.print("[bold blue]Visualizing with OntoSight...[/bold blue]")

    try:
        kb.show(
            node_label_extractor=lambda n: getattr(n, "name", str(n)),
            edge_label_extractor=lambda e: getattr(e, "relation", str(e)),
        )
    except Exception as e:
        console.print(f"[red]Error during visualization:[/red] {e}")
        raise typer.Exit(1)


@app.command(name="info")
def info(kb_path: str = typer.Argument(..., help="Knowledge base directory")):
    """View knowledge base information and statistics."""
    import json

    path = validate_kb_with_data(kb_path)

    metadata = load_kb_metadata(path)

    data_file = path / "data.json"
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        node_count = len(data.get("nodes", data.get("entities", [])))
        edge_count = len(data.get("edges", data.get("relations", [])))
    elif isinstance(data, list):
        node_count = len(data)
        edge_count = 0
    else:
        node_count = 0
        edge_count = 0

    index_exists = (path / "index").exists() and any((path / "index").iterdir())

    table = Table(title="Knowledge Base Info", show_header=False, box=None)
    table.add_column("Key", style="cyan", width=15)
    table.add_column("Value", style="green")

    table.add_row("Path", str(path))

    if metadata:
        table.add_row("Template", metadata.get("template", "unknown"))
        table.add_row("Language", metadata.get("lang", "unknown"))
        table.add_row("Created", metadata.get("created_at", "unknown"))
        table.add_row("Updated", metadata.get("updated_at", "unknown"))
    else:
        table.add_row("Template", "[yellow]unknown[/yellow]")
        table.add_row("Language", "[yellow]unknown[/yellow]")

    table.add_row("Nodes", str(node_count))
    table.add_row("Edges", str(edge_count))
    table.add_row("Index", "[green]Built[/green]" if index_exists else "[red]Not Built[/red]")

    console.print(table)


@app.command(name="search")
def search(
    query: str = typer.Argument(..., help="Search query"),
    kb_path: str = typer.Option(..., "--kb", "-k", help="Knowledge base directory"),
    top_k: int = typer.Option(3, "--top-k", "-n", help="Number of results"),
):
    """Semantic search in knowledge base."""
    import json

    validate_config()

    path = validate_kb_with_index(kb_path)
    template, lang = get_template_from_kb(path)

    console.print(f"[blue]Query:[/blue] {query}")
    console.print(f"[blue]Knowledge base:[/blue] {kb_path}")
    console.print(f"[blue]Top K:[/blue] {top_k}")
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Searching...", total=None)

        try:
            kb = Template.create(template, lang)

            progress.update(task, description="Loading knowledge base...")
            kb.load(path)

            progress.update(task, description="Searching...")
            results = kb.search(query, top_k=top_k)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print()
    if not results:
        console.print("[yellow]No results found.[/yellow]")
    else:
        console.print(f"[bold green]Found {len(results)} result(s):[/bold green]")
        console.print()

        for i, result in enumerate(results, 1):
            console.print(f"[bold cyan]Result {i}:[/bold cyan]")
            if hasattr(result, "model_dump"):
                console.print_json(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
            elif hasattr(result, "dict"):
                console.print_json(json.dumps(result.dict(), indent=2, ensure_ascii=False))
            else:
                console.print(str(result))
            console.print()


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


@app.command(name="talk")
def talk(
    kb_path: str = typer.Argument(..., help="Knowledge base directory"),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Question to ask"),
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
        console.print("[red]Error:[/red] Please provide a query or use --interactive mode")
        raise typer.Exit(1)
    else:
        console.print(f"[blue]Query:[/blue] {query}")
        console.print(f"[blue]Knowledge base:[/blue] {kb_path}")
        console.print(f"[blue]Top K:[/blue] {top_k}")
        console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Loading...", total=None)

        try:
            kb = Template.create(template, lang)

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


@app.command(name="feed")
def feed(
    input: str = typer.Argument(..., help="Input file path or '-' for stdin"),
    output: str = typer.Option(..., "--output", "-o", help="Knowledge base directory"),
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
        kb = Template.create(template, lang)
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

    console.print()
    console.print(f"[bold green]Success![/bold green] Knowledge appended to {output_path}")


@app.command(name="build-index")
def build_index(
    kb_path: str = typer.Argument(..., help="Knowledge base directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Force rebuild"),
):
    """Build vector index for knowledge base."""
    validate_config()

    path = validate_kb_with_data(kb_path)

    index_dir = path / "index"
    if index_dir.exists() and any(index_dir.iterdir()) and not force:
        console.print("[yellow]Warning:[/yellow] Index already exists. Use --force to rebuild.")
        console.print(f"[dim]Index location: {index_dir}[/dim]")
        raise typer.Exit(0)

    template, lang = get_template_from_kb(path)

    console.print(f"[blue]Template:[/blue] {template}")
    console.print(f"[blue]Language:[/blue] {lang}")
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Initializing...", total=None)

        try:
            kb = Template.create(template, lang)

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
