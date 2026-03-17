"""Common utilities for Hyper-Extract CLI."""

import sys
import typer
from pathlib import Path
from typing import Tuple
from rich.console import Console

from .config import ConfigManager

console = Console()


def read_input(input_path: str) -> str:
    """Read input from file or stdin."""
    if input_path == "-":
        return sys.stdin.read()
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def validate_kb_path(kb_path: str) -> Path:
    """Validate knowledge base path.

    Args:
        kb_path: Knowledge base directory path

    Returns:
        Path object

    Raises:
        typer.Exit: If path is invalid
    """
    path = Path(kb_path)

    if not path.exists():
        console.print(f"[red]Error:[/red] Knowledge base not found: {kb_path}")
        raise typer.Exit(1)

    if not path.is_dir():
        console.print(f"[red]Error:[/red] Not a directory: {kb_path}")
        raise typer.Exit(1)

    return path


def validate_kb_with_data(kb_path: str) -> Path:
    """Validate knowledge base path with data.json.

    Args:
        kb_path: Knowledge base directory path

    Returns:
        Path object

    Raises:
        typer.Exit: If path is invalid or missing data.json
    """
    path = validate_kb_path(kb_path)

    data_file = path / "data.json"
    if not data_file.exists():
        console.print(
            f"[red]Error:[/red] Not a valid knowledge base: {kb_path} (no data.json)"
        )
        raise typer.Exit(1)

    return path


def validate_kb_with_index(kb_path: str) -> Path:
    """Validate knowledge base path with index.

    Args:
        kb_path: Knowledge base directory path

    Returns:
        Path object

    Raises:
        typer.Exit: If path is invalid or missing index
    """
    path = validate_kb_path(kb_path)

    index_dir = path / "index"
    if not index_dir.exists() or not any(index_dir.iterdir()):
        console.print(
            f"[red]Error:[/red] Index not found. Please run 'he build-index {kb_path}' first."
        )
        raise typer.Exit(1)

    return path


def get_template_from_kb(kb_path: Path) -> Tuple[str, str]:
    """Get template name and language from knowledge base metadata.

    Args:
        kb_path: Knowledge base directory path

    Returns:
        Tuple of (template_name, language)
    """
    from .config import load_kb_metadata

    metadata = load_kb_metadata(kb_path)

    template = metadata.get("template")
    lang = metadata.get("lang")

    return template, lang


def validate_config() -> "ConfigManager":
    """Validate configuration.

    Returns:
        ConfigManager instance

    Raises:
        typer.Exit: If configuration is invalid
    """

    config = ConfigManager()
    valid, msg = config.validate()

    if not valid:
        console.print(f"[red]Error:[/red] {msg}")
        raise typer.Exit(1)

    return config
