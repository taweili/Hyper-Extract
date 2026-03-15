"""Template API - Unified interface for template operations.

Provides a clean API for searching and creating knowledge extraction templates.
"""

from typing import List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from .gallery import Gallery
from .parsers import RawTemplateCfg


class Template:
    """Template API - Unified interface for template operations.

    Usage Examples:
        from hyperextract.utils.template_engine import Template

        # List all templates
        print(Template.list())

        # Search templates
        results = Template.search(query="财报", type_value="model")

        # Get template config
        config = Template.get("EarningsCallSummary")

        # Create template instance
        template = Template.create("KnowledgeGraph", llm_client=llm, embedder=emb)
        result = template.parse("your text here")

        # List available domains
        print(Template.domains())
    """

    @staticmethod
    def list() -> List[str]:
        """List all available template names.

        Returns:
            List of template names
        """
        return Gallery.list_all()

    @staticmethod
    def search(
        query: Optional[str] = None,
        type_value: Optional[str] = None,
        tag: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[RawTemplateCfg]:
        """Search templates by various criteria.

        Args:
            query: Search in template name/description
            type_value: Filter by type (e.g., "graph", "list", "model")
            tag: Filter by tag (e.g., "finance", "medicine")
            language: Filter by language (e.g., "zh", "en")

        Returns:
            List of matching RawTemplateCfg objects
        """
        return Gallery.search(
            query=query,
            type_value=type_value,
            tag=tag,
            language=language,
        )

    @staticmethod
    def get(name: str, lang: str = "zh") -> Optional[RawTemplateCfg]:
        """Get template configuration by name.

        Args:
            name: Template name (e.g., "KnowledgeGraph")
            lang: Language, default "zh"

        Returns:
            RawTemplateCfg or None if not found
        """
        return Gallery.get(name)

    @staticmethod
    def create(
        name: str,
        lang: str = "zh",
        llm_client: Optional[BaseChatModel] = None,
        embedder: Optional[Embeddings] = None,
        **kwargs,
    ):
        """Create template instance.

        Args:
            name: Template name (e.g., "KnowledgeGraph")
            lang: Language, default "zh"
            llm_client: LLM client (reads from global config if not provided)
            embedder: Embedder client (reads from global config if not provided)
            **kwargs: Additional parameters (e.g., observation_time, observation_location)

        Returns:
            TemplateWrapper instance

        Examples:
            # Basic usage (uses global config)
            template = Template.create("KnowledgeGraph")

            # With custom clients
            template = Template.create(
                "KnowledgeGraph",
                llm_client=my_llm,
                embedder=my_embedder
            )

            # For temporal/spatial templates
            template = Template.create(
                "FinancialTemporalGraph",
                observation_time="2024-06-15"
            )
        """
        return Gallery.create(
            name=name,
            lang=lang,
            llm_client=llm_client,
            embedder=embedder,
            **kwargs,
        )

    @staticmethod
    def domains() -> List[tuple]:
        """List all available domains with template count.

        Returns:
            List of (domain_name, template_count) tuples
        """
        return Gallery.list_domains()

    @staticmethod
    def types() -> List[str]:
        """List all available template types.

        Returns:
            List of type names (e.g., ["model", "list", "graph", ...])
        """
        return Gallery.list_types()

    @staticmethod
    def tags() -> List[str]:
        """List all available tags.

        Returns:
            List of tag names
        """
        return Gallery.list_tags()

    @staticmethod
    def languages() -> List[str]:
        """List all available languages.

        Returns:
            List of language codes (e.g., ["zh", "en"])
        """
        return Gallery.list_languages()
