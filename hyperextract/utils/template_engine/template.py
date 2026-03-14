"""Template - Unified template API."""

from .gallery import Gallery


class Template:
    """Unified template API for searching and creating templates.
    
    Examples:
        # List all templates
        Template.list()
        
        # Search templates
        Template.search("知识图谱")
        Template.search(autotype="graph")
        
        # Get template config
        config = Template.get("knowledge_graph")
        
        # Create template (auto reads from global config)
        template = Template.create("knowledge_graph")
        
        # Create with custom clients
        template = Template.create("knowledge_graph", llm_client=llm, embedder=emb)
    """
    
    @staticmethod
    def list():
        """List all available template names."""
        return Gallery.list_all()
    
    @staticmethod
    def search(query=None, autotype=None, tag=None, language=None):
        """Search templates by criteria.
        
        Args:
            query: Search in template name/description
            autotype: Filter by autotype (e.g., "graph", "list")
            tag: Filter by tag
            language: Filter by language (e.g., "zh", "en")
            
        Returns:
            List of TemplateConfig
        """
        return Gallery.search(query, autotype, tag, language)
    
    @staticmethod
    def get(name, lang="zh"):
        """Get template config by name.
        
        Args:
            name: Template name
            lang: Language
            
        Returns:
            TemplateConfig
        """
        return Gallery._resolve_config(name, lang)
    
    @staticmethod
    def create(name, lang="zh", llm_client=None, embedder=None):
        """Create template instance.
        
        If llm_client or embedder is not provided, automatically reads
        from global config (~/.he/config.toml).
        
        Args:
            name: Template name (e.g., "knowledge_graph", "zh/finance/risk_assessment")
            lang: Language, default "zh"
            llm_client: LLM client, optional
            embedder: Embedder client, optional
            
        Returns:
            TemplateWrapper instance
        """
        return Gallery.create(name, lang, llm_client, embedder)
    
    @staticmethod
    def domains():
        """List available domains with template count.
        
        Returns:
            List of (domain_name, template_count) tuples
        """
        return Gallery.list_domains()


__all__ = ["Template"]
