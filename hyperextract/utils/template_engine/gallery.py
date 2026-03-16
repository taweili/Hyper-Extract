"""Template Gallery - Manages discovery and loading of knowledge extraction templates.

Supports auto-loading presets and customs directories.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from .parsers import TemplateCfg, load_template


class Gallery:
    """Template Gallery.

    Usage Examples:
        from hyperextract.utils.template_engine import Gallery

        # Get template (auto-loaded)
        config = Gallery.get("general/knowledge_graph")

        # List all templates
        print(Gallery.list())

        # List domains
        print(Gallery.list_domains())

        # Search templates
        results = Gallery.search(type="graph")

        # Add custom template directory (auto-loaded)
        Gallery.add_path("/path/to/my/templates")

        # Add single YAML file
        Gallery.add("/path/to/my_template.yaml")
    """

    _instance: Optional["Gallery"] = None

    def __init__(self):
        self._configs: Dict[str, TemplateCfg] = {}
        self._configs_by_type: Dict[str, List[str]] = {}
        self._configs_by_tag: Dict[str, List[str]] = {}

    @classmethod
    def get(cls, path: str) -> Optional[TemplateCfg]:
        """Get template configuration by path.

        Args:
            path: Template path (e.g., "general/knowledge_graph")

        Returns:
            TemplateCfg or None if not found
        """
        return cls._instance._configs.get(path) if cls._instance else None

    @classmethod
    def list(cls) -> List[str]:
        """List all available template names.

        Returns:
            List of template names
        """
        return list(cls._instance._configs.keys()) if cls._instance else []

    @classmethod
    def add_path(cls, path: str) -> None:
        """Add a directory of template files.

        Args:
            path: Directory path containing YAML template files
        """
        if not cls._instance:
            return
        dir_path = Path(path)
        if not dir_path.exists() or not dir_path.is_dir():
            return
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith((".yaml", ".yml")):
                    cls._instance._load_config(Path(root) / file)

    @classmethod
    def add(cls, file_path: str) -> None:
        """Add a single template file.

        Args:
            file_path: Path to YAML template file
        """
        if not cls._instance:
            return
        path = Path(file_path)
        if path.exists() and path.is_file() and path.suffix in (".yaml", ".yml"):
            cls._instance._load_config(path)

    @classmethod
    def search(
        cls,
        query: str = None,
        type: str = None,
        tag: str = None,
        language: str = None,
    ) -> List[TemplateCfg]:
        """Search templates by query, type, tag, or language.

        Args:
            query: Search in template name/description
            type: Filter by autotype (e.g., "graph", "list", "model")
            tag: Filter by tag
            language: Filter by language (e.g., "zh", "en")

        Returns:
            List of matching TemplateCfg
        """
        if not cls._instance:
            return []

        results = []

        for config in cls._instance._configs.values():
            if query:
                query_lower = query.lower()
                name_match = config.name.lower()
                desc_match = getattr(config, "description", None)
                desc_value = desc_match.zh if hasattr(desc_match, "zh") else desc_match
                if query_lower not in name_match and (
                    desc_value and query_lower not in str(desc_value).lower()
                ):
                    continue

            if type and config.type != type:
                continue

            if tag and (not config.tags or tag not in config.tags):
                continue

            if language:
                config_lang = config.language
                if isinstance(config_lang, list):
                    if language not in config_lang:
                        continue
                elif config_lang != language:
                    continue

            results.append(config)

        return results

    @classmethod
    def list_domains(cls) -> List[str]:
        """List all available domains (folder names in presets).

        Returns:
            List of domain names
        """
        base_dir = Path(__file__).parent.parent.parent / "templates" / "presets"
        domains = []
        if base_dir.exists():
            for item in base_dir.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    domains.append(item.name)
        return sorted(domains)

    def _load_config(self, file_path: Path) -> None:
        try:
            config = load_template(file_path)
            self._register(config)
        except Exception as e:
            print(f"Failed to load config {file_path}: {e}")

    def _register(self, config: TemplateCfg) -> None:
        self._configs[config.name] = config

        if config.type not in self._configs_by_type:
            self._configs_by_type[config.type] = []
        if config.name not in self._configs_by_type[config.type]:
            self._configs_by_type[config.type].append(config.name)

        if config.tags:
            for tag in config.tags:
                if tag not in self._configs_by_tag:
                    self._configs_by_tag[tag] = []
                if config.name not in self._configs_by_tag[tag]:
                    self._configs_by_tag[tag].append(config.name)


def _init_gallery() -> Gallery:
    gallery = Gallery()
    Gallery._instance = gallery

    base_dir = Path(__file__).parent.parent.parent / "templates"
    presets_dir = base_dir / "presets"
    customs_dir = base_dir / "customs"

    if presets_dir.exists():
        Gallery.add_path(str(presets_dir))

    if customs_dir.exists():
        Gallery.add_path(str(customs_dir))

    return gallery


Gallery._instance = _init_gallery()
