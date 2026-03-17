"""Template API - Unified interface for template operations.

Provides a clean API for searching and creating knowledge extraction templates.
"""

from typing import Dict, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from .gallery import Gallery
from .parsers import TemplateCfg


class Template:
    """Template API - Unified interface for template operations.

    Usage Examples:
        from hyperextract.utils.template_engine import Template

        # Create template instance (2 ways)
        template = Template.create("general/knowledge_graph", llm, emb)
        template = Template.create("/path/to/template.yaml", llm, emb)

        # Get template config by path
        config = Template.get("general/knowledge_graph")

        # List all templates (returns Dict[str, TemplateCfg])
        all_templates = Template.list()

        # List templates with filters
        graph_templates = Template.list(filter_by_type="graph")
        zh_templates = Template.list(filter_by_language="zh")
    """

    @staticmethod
    def create(
        source: str,
        language: str,
        llm_client: Optional[BaseChatModel] = None,
        embedder: Optional[Embeddings] = None,
        **kwargs,
    ):
        """Create template instance.

        Args:
            source: Template path (e.g., "general/knowledge_graph") or file path
            language: Language code (e.g., "zh", "en") - required
            llm_client: LLM client (reads from global config if not provided)
            embedder: Embedder client (reads from global config if not provided)
            **kwargs: Additional parameters

        Returns:
            AutoType instance

        Examples:
            # By path
            template = Template.create("general/knowledge_graph", "zh", llm, emb)

            # By file path
            template = Template.create("/path/to/template.yaml", "zh", llm, emb)

            # For temporal/spatial templates
            template = Template.create(
                "finance/financial_data_temporal_graph",
                "zh",
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

        return TemplateFactory.create(source, language, llm_client, embedder, **kwargs)

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
    def list(
        filter_by_query: Optional[str] = None,
        filter_by_type: Optional[str] = None,
        filter_by_tag: Optional[str] = None,
        filter_by_language: Optional[str] = None,
    ) -> Dict[str, TemplateCfg]:
        """List templates with optional filters.

        Args:
            filter_by_query: Search in template name/description
            filter_by_type: Filter by autotype (e.g., "graph", "list", "model")
            filter_by_tag: Filter by tag
            filter_by_language: Filter by language (e.g., "zh", "en")

        Returns:
            Dict mapping template name to TemplateCfg
        """
        return Gallery.list(
            filter_by_query=filter_by_query,
            filter_by_type=filter_by_type,
            filter_by_tag=filter_by_tag,
            filter_by_language=filter_by_language,
        )


