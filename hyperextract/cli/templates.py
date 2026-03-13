"""Template loading utilities for Hyper-Extract CLI."""

from typing import Optional, Any, Type

from hyperextract.utils.template_engine import Gallery, TemplateFactory, TemplateConfig


def resolve_template(template_str: str, lang: str = "zh") -> Type:
    """
    Resolve a template string to a template instance.

    Args:
        template_str: Template name (e.g., "KnowledgeGraph", "zh/finance/risk_assessment")
        lang: Language (zh/en)

    Returns:
        TemplateWrapper instance

    Raises:
        ValueError: If template not found
    """
    original_str = template_str

    config = Gallery.get(template_str)
    if config is not None:
        return _create_template_from_config(config)

    parts = template_str.split("/")
    if len(parts) == 1:
        template_name = parts[0]
        search_name = f"{lang}/{template_name}"
        config = Gallery.get(search_name)
        if config is not None:
            return _create_template_from_config(config)
    else:
        template_lang = parts[0]
        if template_lang not in ["zh", "en"]:
            template_lang = lang
        template_name = parts[-1]

        full_name = f"{template_lang}/{template_name}"
        config = Gallery.get(full_name)
        if config is not None:
            return _create_template_from_config(config)

    available = Gallery.list_all()
    raise ValueError(f"Template '{original_str}' not found. Available templates: {available[:10]}...")


def resolve_template_config(template_str: str, lang: str = "zh") -> Optional[TemplateConfig]:
    """
    Resolve a template string to a TemplateConfig.

    Args:
        template_str: Template name
        lang: Language (zh/en)

    Returns:
        TemplateConfig if found, None otherwise
    """
    original_str = template_str

    config = Gallery.get(template_str)
    if config is not None:
        return config

    parts = template_str.split("/")
    if len(parts) == 1:
        template_name = parts[0]
        search_name = f"{lang}/{template_name}"
        config = Gallery.get(search_name)
        if config is not None:
            return config
    else:
        template_lang = parts[0]
        if template_lang not in ["zh", "en"]:
            template_lang = lang
        template_name = parts[-1]
        full_name = f"{template_lang}/{template_name}"
        return Gallery.get(full_name)


def _create_template_from_config(config: TemplateConfig):
    """Create a template instance from config using TemplateFactory."""
    from .config import ConfigManager

    config_manager = ConfigManager()
    llm_config = config_manager.get_llm_config()
    embedder_config = config_manager.get_embedder_config()

    if llm_config.provider == "openai":
        from langchain_openai import ChatOpenAI
        llm_client = ChatOpenAI(
            model=llm_config.model,
            api_key=llm_config.api_key,
            base_url=llm_config.base_url or None,
            temperature=0,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_config.provider}")

    if embedder_config.provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        embedder = OpenAIEmbeddings(
            model=embedder_config.model,
            api_key=embedder_config.api_key,
            base_url=embedder_config.base_url or None,
        )
    else:
        raise ValueError(f"Unsupported Embedder provider: {embedder_config.provider}")

    return TemplateFactory.create(config, llm_client, embedder)


def get_auto_type_from_template(template_or_config: Any) -> str:
    """Infer AutoType from template class or config."""
    if isinstance(template_or_config, TemplateConfig):
        autotype = template_or_config.autotype
        autotype_map = {
            "model": "AutoModel",
            "list": "AutoList",
            "set": "AutoSet",
            "graph": "AutoGraph",
            "hypergraph": "AutoHypergraph",
            "temporal_graph": "AutoTemporalGraph",
            "spatial_graph": "AutoSpatialGraph",
            "spatio_temporal_graph": "AutoSpatioTemporalGraph",
        }
        return autotype_map.get(autotype, "AutoGraph")

    return "AutoGraph"


def get_domains() -> list:
    """Get available domains from configs directory."""
    return Gallery.list_domains()
