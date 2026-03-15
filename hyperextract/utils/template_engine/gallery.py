"""Template Gallery - Manages discovery and loading of knowledge extraction templates.

Supports auto-loading presets and customs directories.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from .parsers import RawTemplateCfg, ConfigLoader


class Gallery:
    """Template Gallery.

    Usage Examples:
        from hyperextract.utils.template_engine import Gallery

        # Get template (auto-loaded)
        config = Gallery.get("KnowledgeGraph")

        # List all templates
        print(Gallery.list_all())

        # Add custom template directory (auto-loaded)
        Gallery.add_path("/path/to/my/templates")

        # Add single YAML file
        Gallery.add("/path/to/my_template.yaml")
    """

    _instance: Optional["Gallery"] = None

    def __init__(self):
        self._configs: Dict[str, RawTemplateCfg] = {}
        self._configs_by_type: Dict[str, List[str]] = {}
        self._configs_by_tag: Dict[str, List[str]] = {}

    @classmethod
    def get(cls, name: str) -> Optional[RawTemplateCfg]:
        return cls._instance._configs.get(name) if cls._instance else None

    @classmethod
    def list_all(cls) -> List[str]:
        return list(cls._instance._configs.keys()) if cls._instance else []

    @classmethod
    def add_path(cls, path: str) -> None:
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
        if not cls._instance:
            return
        path = Path(file_path)
        if path.exists() and path.is_file() and path.suffix in (".yaml", ".yml"):
            cls._instance._load_config(path)

    @classmethod
    def get_by_type(cls, type_value: str) -> List[RawTemplateCfg]:
        if not cls._instance:
            return []
        names = cls._instance._configs_by_type.get(type_value, [])
        return [cls._instance._configs[name] for name in names if name in cls._instance._configs]

    @classmethod
    def get_by_tag(cls, tag: str) -> List[RawTemplateCfg]:
        if not cls._instance:
            return []
        names = cls._instance._configs_by_tag.get(tag, [])
        return [cls._instance._configs[name] for name in names if name in cls._instance._configs]

    @classmethod
    def search(cls, query: str = None, type_value: str = None, tag: str = None, language: str = None) -> List[RawTemplateCfg]:
        """Search templates by query, type, tag, or language.
        
        Args:
            query: Search in template name/description
            type_value: Filter by type (e.g., "graph", "list")
            tag: Filter by tag
            language: Filter by language (e.g., "zh", "en")
        
        Returns:
            List of matching RawTemplateCfg
        """
        if not cls._instance:
            return []
        
        results = []
        
        for config in cls._instance._configs.values():
            if query:
                query_lower = query.lower()
                name_match = config.name.lower()
                desc_match = getattr(config, 'description', None)
                desc_value = desc_match.zh if hasattr(desc_match, 'zh') else desc_match
                if query_lower not in name_match and (desc_value and query_lower not in str(desc_value).lower()):
                    continue
            
            if type_value and config.type != type_value:
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
    def list_languages(cls) -> List[str]:
        """List all available languages."""
        if not cls._instance:
            return []
        languages = set()
        for config in cls._instance._configs.values():
            lang = config.language
            if isinstance(lang, list):
                languages.update(lang)
            elif lang:
                languages.add(lang)
        return sorted(languages)

    @classmethod
    def list_types(cls) -> List[str]:
        """List all available types."""
        if not cls._instance:
            return []
        return list(cls._instance._configs_by_type.keys())

    @classmethod
    def list_tags(cls) -> List[str]:
        """List all available tags."""
        if not cls._instance:
            return []
        return list(cls._instance._configs_by_tag.keys())

    @classmethod
    def list_domains(cls) -> List[tuple]:
        """List all available domains with template count.
        
        Returns:
            List of (domain_name, template_count) tuples
        """
        base_dir = Path(__file__).parent.parent.parent / "templates" / "presets"
        domains = []
        if base_dir.exists():
            for item in base_dir.iterdir():
                if item.is_dir() and not item.name.startswith('_'):
                    count = len(list(item.glob("*.yaml")))
                    domains.append((item.name, count))
        return domains

    @classmethod
    def create(
        cls,
        name: str,
        lang: str = "zh",
        llm_client=None,
        embedder=None,
        **kwargs,
    ):
        """Create template instance.
        
        Args:
            name: Template name (e.g., "knowledge_graph", "zh/finance/risk_assessment")
            lang: Language, default "zh"
            llm_client: LLM client, optional, reads from global config if not provided
            embedder: Embedder client, optional, reads from global config if not provided
            **kwargs: Additional parameters (e.g., observation_time, observation_location)
            
        Returns:
            TemplateWrapper instance
            
        Examples:
            # Method 1: Use global config (recommended)
            template = Gallery.create("knowledge_graph")
            
            # Method 2: Custom client
            from hyperextract.utils import get_client
            llm, emb = get_client()
            template = Gallery.create("knowledge_graph", llm_client=llm, embedder=emb)
            
            # Method 3: Mixed usage
            template = Gallery.create("knowledge_graph", llm_client=my_llm)
            
            # Method 4: With additional parameters
            template = Gallery.create("FinancialTemporalGraph", observation_time="2024-06-15")
        """
        config = cls._resolve_config(name, lang)
        
        if llm_client is None or embedder is None:
            from hyperextract.utils import get_client
            default_llm, default_emb = get_client()
            llm_client = llm_client or default_llm
            embedder = embedder or default_emb
        
        from .factory import TemplateFactory
        return TemplateFactory.create(config, llm_client, embedder, **kwargs)

    @classmethod
    def _resolve_config(cls, name: str, lang: str = "zh") -> RawTemplateCfg:
        """Resolve template name to config object."""
        config = cls.get(name)
        if config is not None:
            return config
        
        parts = name.split("/")
        if len(parts) == 1:
            search_name = f"{lang}/{name}"
            config = cls.get(search_name)
            if config is not None:
                return config
        else:
            template_lang = parts[0]
            if template_lang not in ["zh", "en"]:
                template_lang = lang
            template_name = parts[-1]
            full_name = f"{template_lang}/{template_name}"
            config = cls.get(full_name)
            if config is not None:
                return config
        
        available = cls.list_all()
        raise ValueError(f"Template '{name}' not found. Available: {available[:10]}...")

    def _load_config(self, file_path: Path) -> None:
        try:
            config = ConfigLoader.load_config(file_path)
            self._register(config)
        except Exception as e:
            print(f"Failed to load config {file_path}: {e}")

    def _register(self, config: RawTemplateCfg) -> None:
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
