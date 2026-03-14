"""Template loading utilities for Hyper-Extract CLI."""

from typing import Optional, Any, Type

from hyperextract.utils.template_engine import Gallery, TemplateConfig


def resolve_template(template_str: str, lang: str = "zh") -> Type:
    """Resolve a template string to a template instance.
    
    Args:
        template_str: Template name (e.g., "knowledge_graph", "zh/finance/risk_assessment")
        lang: Language (zh/en)
        
    Returns:
        TemplateWrapper instance
        
    Raises:
        ValueError: If template not found
    """
    return Gallery.create(template_str, lang)


def resolve_template_config(template_str: str, lang: str = "zh") -> Optional[TemplateConfig]:
    """Resolve a template string to a TemplateConfig.
    
    Args:
        template_str: Template name
        lang: Language (zh/en)
        
    Returns:
        TemplateConfig if found, None otherwise
    """
    return Gallery._resolve_config(template_str, lang)


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
