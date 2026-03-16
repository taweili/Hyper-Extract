"""Template API - Unified interface for template operations.

Provides a clean API for searching and creating knowledge extraction templates.
"""

from typing import List, Optional, Union
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from .gallery import Gallery
from .parsers import TemplateCfg


class Template:
    """Template API - Unified interface for template operations.

    Usage Examples:
        from hyperextract.utils.template_engine import Template

        # Create template instance (3 ways)
        template = Template.create("general/knowledge_graph", llm, emb)
        template = Template.create("/path/to/template.yaml", llm, emb)
        template = Template.create(config, llm, emb)

        # Get template config by path
        config = Template.get("general/knowledge_graph")

        # Search templates
        results = Template.search(type="graph")
        results = Template.search(tag="finance")
        results = Template.search(query="知识图谱")

        # List all templates
        names = Template.list()

        # List domains
        domains = Template.list_domains()
    """

    @staticmethod
    def create(
        source: Union[str, Path, TemplateCfg],
        llm_client: Optional[BaseChatModel] = None,
        embedder: Optional[Embeddings] = None,
        language: str = "zh",
        **kwargs,
    ):
        """Create template instance.

        Args:
            source: Template source - can be:
                - str: Template path (e.g., "general/knowledge_graph") or file path
                - Path: YAML file path
                - TemplateCfg: Template configuration instance
            llm_client: LLM client (reads from global config if not provided)
            embedder: Embedder client (reads from global config if not provided)
            language: Language code (e.g., "zh", "en")
            **kwargs: Additional parameters

        Returns:
            AutoType instance

        Examples:
            # By path
            template = Template.create("general/knowledge_graph", llm, emb)

            # By file path
            template = Template.create("/path/to/template.yaml", llm, emb)

            # By config instance
            template = Template.create(config, llm, emb)

            # For temporal/spatial templates
            template = Template.create(
                "finance/financial_data_temporal_graph",
                llm,
                emb,
                observation_time="2024-06-15"
            )
        """
        from .factory import TemplateFactory

        if llm_client is None or embedder is None:
            from hyperextract.utils import get_client

            default_llm, default_emb = get_client()
            llm_client = llm_client or default_llm
            embedder = embedder or default_emb

        return TemplateFactory.create(source, llm_client, embedder, language=language, **kwargs)

    @staticmethod
    def get(path: str) -> Optional[TemplateCfg]:
        """Get template configuration by path.

        Args:
            path: Template path (e.g., "general/knowledge_graph")

        Returns:
            TemplateCfg or None if not found
        """
        return Gallery.get(path)

    @staticmethod
    def search(
        query: Optional[str] = None,
        type: Optional[str] = None,
        tag: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[TemplateCfg]:
        """Search templates by various criteria.

        Args:
            query: Search in template name/description
            type: Filter by autotype (e.g., "graph", "list", "model")
            tag: Filter by tag (e.g., "finance", "medicine")
            language: Filter by language (e.g., "zh", "en")

        Returns:
            List of matching TemplateCfg objects
        """
        return Gallery.search(
            query=query,
            type=type,
            tag=tag,
            language=language,
        )

    @staticmethod
    def list() -> List[str]:
        """List all available template names.

        Returns:
            List of template names
        """
        return Gallery.list()

    @staticmethod
    def list_domains() -> List[str]:
        """List all available domains (folder names in presets).

        Returns:
            List of domain names
        """
        return Gallery.list_domains()
