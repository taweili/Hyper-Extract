"""Config command for Hyper-Extract CLI."""

from typing import Optional
from rich.console import Console
from rich.table import Table

from ..config import ConfigManager, LLM_PROVIDERS, EMBEDDER_PROVIDERS
import typer

console = Console()

app = typer.Typer(
    name="config",
    help="Manage LLM and Embedder configuration",
)


def _show_config():
    """Show current configuration."""
    config = ConfigManager()
    cfg = config.show()
    
    table = Table(title="Hyper-Extract Configuration")
    table.add_column("Service", style="cyan", width=15)
    table.add_column("Provider", style="green", width=15)
    table.add_column("Model", style="yellow", width=25)
    table.add_column("API Key", style="magenta", width=20)

    llm_cfg = cfg["llm"]
    emb_cfg = cfg["embedder"]

    table.add_row(
        "LLM",
        llm_cfg["provider"],
        llm_cfg["model"],
        llm_cfg["api_key"][:10] + "..." if llm_cfg["api_key"] else "(not set)",
    )
    table.add_row(
        "Embedder",
        emb_cfg["provider"],
        emb_cfg["model"],
        emb_cfg["api_key"][:10] + "..." if emb_cfg["api_key"] else "(not set)",
    )

    console.print(table)


@app.command(name="show")
def show(
    show_all: bool = typer.Option(False, "--show", help="Show all configuration"),
):
    """Show current configuration."""
    _show_config()


@app.command(name="llm")
def llm(
    provider: str = typer.Option(
        None,
        "--provider",
        "-p",
        help=f"LLM provider ({'/'.join(LLM_PROVIDERS)})",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="LLM API key",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="LLM model name",
    ),
    base_url: Optional[str] = typer.Option(
        None,
        "--base-url",
        "-u",
        help="Custom API base URL",
    ),
    show: bool = typer.Option(False, "--show", help="Show current LLM configuration"),
    unset: bool = typer.Option(False, "--unset", help="Unset LLM configuration"),
):
    """Configure LLM settings."""
    config = ConfigManager()

    if show:
        cfg = config.get_llm_config()
        table = Table(title="LLM Configuration", show_header=False)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Provider", cfg.provider)
        table.add_row("Model", cfg.model)
        table.add_row("API Key", cfg.api_key[:10] + "..." if cfg.api_key else "(not set)")
        table.add_row("Base URL", cfg.base_url or "(default)")
        console.print(table)
        return

    if unset:
        config.unset_llm()
        console.print("[green]LLM configuration cleared[/green]")
        return

    config.set_llm(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
    )
    console.print("[green]LLM configuration updated[/green]")


@app.command(name="embedder")
def embedder(
    provider: str = typer.Option(
        None,
        "--provider",
        "-p",
        help=f"Embedder provider ({'/'.join(EMBEDDER_PROVIDERS)})",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="Embedder API key",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Embedder model name",
    ),
    base_url: Optional[str] = typer.Option(
        None,
        "--base-url",
        "-u",
        help="Custom API base URL",
    ),
    show: bool = typer.Option(False, "--show", help="Show current Embedder configuration"),
    unset: bool = typer.Option(False, "--unset", help="Unset Embedder configuration"),
):
    """Configure Embedder settings."""
    config = ConfigManager()

    if show:
        cfg = config.get_embedder_config()
        table = Table(title="Embedder Configuration", show_header=False)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Provider", cfg.provider)
        table.add_row("Model", cfg.model)
        table.add_row("API Key", cfg.api_key[:10] + "..." if cfg.api_key else "(not set)")
        table.add_row("Base URL", cfg.base_url or "(default)")
        console.print(table)
        return

    if unset:
        config.unset_embedder()
        console.print("[green]Embedder configuration cleared[/green]")
        return

    config.set_embedder(
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url,
    )
    console.print("[green]Embedder configuration updated[/green]")


@app.command(name="init")
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite existing config"),
):
    """Initialize configuration interactively."""
    config = ConfigManager()

    console.print("[bold blue]Hyper-Extract Configuration Setup[/bold blue]")
    console.print()

    console.print("[bold]Step 1: LLM Configuration[/bold]")
    provider = console.input("  Provider [openai]: ") or "openai"
    model = console.input("  Model [gpt-4o-mini]: ") or "gpt-4o-mini"
    api_key = console.input("  API Key: ", password=True)
    base_url = console.input("  Base URL (optional): ")

    config.set_llm(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url or None,
    )

    console.print()

    console.print("[bold]Step 2: Embedder Configuration[/bold]")
    emb_provider = console.input("  Provider [openai]: ") or "openai"
    emb_model = console.input("  Model [text-embedding-3-small]: ") or "text-embedding-3-small"
    emb_api_key = console.input("  API Key: ", password=True)
    emb_base_url = console.input("  Base URL (optional): ")

    config.set_embedder(
        provider=emb_provider,
        model=emb_model,
        api_key=emb_api_key,
        base_url=emb_base_url or None,
    )

    console.print()
    console.print("[bold green]Configuration saved successfully![/bold green]")
