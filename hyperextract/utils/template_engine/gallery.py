"""Template Gallery - Manages discovery and loading of knowledge extraction templates.

Auto-loads templates from presets directory.
"""

from pathlib import Path
from typing import Dict, List, Optional

from .parsers import TemplateCfg, load_template


class Gallery:
    """Template Gallery.

    Usage Examples:
        from hyperextract.utils.template_engine import Gallery

        # Get template by path
        config = Gallery.get("general/knowledge_graph")

        # List all templates
        print(Gallery.list())

        # List domains
        print(Gallery.list_domains())

        # Search templates
        results = Gallery.search(type="graph")
    """

    _instance: Optional["Gallery"] = None

    def __init__(self):
        self._configs: Dict[str, TemplateCfg] = {}

    @classmethod
    def get(cls, path: str) -> Optional[TemplateCfg]:
        """Get template configuration by path.

        Args:
            path: Template path
                If no domain is specified, "general/" is assumed. 
                Only templates in the "general/" domain are supported.
                Other domains are not supported.
                (e.g., "general/knowledge_graph" or "knowledge_graph") 

        Returns:
            TemplateCfg or None if not found
        """
        if "/" in path:
            return cls._instance._configs.get(path)

        return cls._instance._configs.get(f"general/{path}")

    @classmethod
    def list(cls) -> List[str]:
        """List all available template names.

        Returns:
            List of template names
        """
        return list(cls._instance._configs.keys()) if cls._instance else []

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
            q = query.lower() if query else None

            if q and q not in config.name.lower():
                desc = config.description
                if isinstance(desc, str) and q not in desc.lower():
                    continue
                if isinstance(desc, dict) and not any(
                    q in v.lower() for v in desc.values()
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

    def _load_config(self, file_path: Path, presets_dir: Path) -> None:
        try:
            config = load_template(file_path)
            domain = file_path.parent.relative_to(presets_dir).parts[0]
            key = f"{domain}/{config.name}"
            self._configs[key] = config
        except Exception as e:
            print(f"Failed to load config {file_path}: {e}")


def _init_gallery() -> Gallery:
    gallery = Gallery()
    Gallery._instance = gallery

    presets_dir = Path(__file__).parent.parent.parent / "templates" / "presets"

    if presets_dir.exists():
        for file_path in presets_dir.rglob("*.yaml"):
            gallery._load_config(file_path, presets_dir)

    return gallery


Gallery._instance = _init_gallery()
