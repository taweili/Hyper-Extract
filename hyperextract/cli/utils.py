"""Common utilities for Hyper-Extract CLI."""

import sys
import typer
from pathlib import Path
from rich.console import Console
from typing import Optional, Tuple

from hyperextract.utils.template_engine import Template, TemplateCfg
from .config import ConfigManager

console = Console()


AUTOTYPE_MAP = {
    "model": "AutoModel",
    "list": "AutoList",
    "set": "AutoSet",
    "graph": "AutoGraph",
    "hypergraph": "AutoHypergraph",
    "temporal_graph": "AutoTemporalGraph",
    "spatial_graph": "AutoSpatialGraph",
    "spatio_temporal_graph": "AutoSpatioTemporalGraph",
}

AUTOTYPE_DESCRIPTIONS = {
    "AutoModel": "Extract into a complete data model",
    "AutoList": "Extract as a list (keywords, items)",
    "AutoSet": "Extract and deduplicate (entity registry)",
    "AutoGraph": "Extract as a knowledge graph (relations)",
    "AutoTemporalGraph": "Extract as timeline (events over time)",
    "AutoSpatialGraph": "Extract as spatial graph (locations)",
    "AutoSpatioTemporalGraph": "Extract as spatiotemporal graph (time + space)",
    "AutoHypergraph": "Extract as hypergraph (multi-party relations)",
}

DOMAIN_DESCRIPTIONS = {
    "finance": "Financial documents",
    "medicine": "Medical documents",
    "legal": "Legal documents",
    "history": "Historical documents",
    "literature": "Literature works",
    "tcm": "Traditional Chinese Medicine",
    "news": "News articles",
    "biology": "Biological documents",
    "industry": "Industrial documents",
    "agriculture": "Agricultural documents",
    "food": "Food and culinary",
    "general": "General purpose",
}


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

    if not metadata:
        console.print(
            "[yellow]Warning:[/yellow] No metadata found, assuming knowledge_graph"
        )
        return "knowledge_graph", "zh"

    template = metadata.get("template", "knowledge_graph")
    lang = metadata.get("lang", "zh")

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


def create_template(template: str, lang: str = "zh"):
    """Create template instance.

    Args:
        template: Template name
        lang: Language (zh/en)

    Returns:
        TemplateWrapper instance
    """
    return Template.create(template, lang)


def get_template_config(template: str, lang: str = "zh") -> Optional[TemplateCfg]:
    """Get template config.

    Args:
        template: Template name
        lang: Language (zh/en)

    Returns:
        TemplateCfg if found
    """
    return Template.get(template, lang)


def get_auto_type_from_config(config: TemplateCfg) -> str:
    """Infer AutoType from template config.

    Args:
        config: TemplateCfg instance

    Returns:
        AutoType string (e.g., "AutoGraph")
    """
    autotype = config.autotype
    return AUTOTYPE_MAP.get(autotype, "AutoGraph")


def get_autotype_description(autotype: str) -> str:
    """Get description for AutoType.

    Args:
        autotype: AutoType name (e.g., "AutoGraph")

    Returns:
        Description string
    """
    return AUTOTYPE_DESCRIPTIONS.get(autotype, "")


def get_domain_description(domain: str) -> str:
    """Get description for domain.

    Args:
        domain: Domain name (e.g., "finance")

    Returns:
        Description string
    """
    return DOMAIN_DESCRIPTIONS.get(domain, f"{domain} documents")
