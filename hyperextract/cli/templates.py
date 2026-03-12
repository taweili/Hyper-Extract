"""Template loading utilities for Hyper-Extract CLI."""

from typing import Type, Optional, Any
import importlib


TEMPLATE_ALIASES = {
    "kg": "knowledge_graph",
    "graph": "knowledge_graph",
    "list": "keyword_list",
    "entity": "entity_registry",
    "timeline": "chronological_event_chain",
    "risk": "risk_assessment",
    "summary": "encyclopedia_item",
}


def resolve_template(template_str: str, lang: str = "zh") -> Type:
    """
    Resolve a template string to a template class.

    Args:
        template_str: Template name or alias (e.g., "knowledge_graph", "kg", "zh/finance/risk_assessment")
        lang: Language (zh/en)

    Returns:
        Template class

    Raises:
        ValueError: If template not found
    """
    template_str = template_str.lower()

    if template_str in TEMPLATE_ALIASES:
        template_str = TEMPLATE_ALIASES[template_str]

    parts = template_str.split("/")

    if len(parts) == 1:
        template_name = parts[0]
        module_path = f"hyperextract.templates.{lang}.{template_name}"
    else:
        template_lang = parts[0]
        if template_lang not in ["zh", "en"]:
            template_lang = lang
        domain = parts[1]
        template_name = parts[2] if len(parts) > 2 else parts[1]
        module_path = f"hyperextract.templates.{template_lang}.{domain}.{template_name}"

    try:
        module = importlib.import_module(module_path)
        template_class = getattr(module, template_name)
        return template_class
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Template '{template_str}' not found: {e}")


def get_template_info(template_class: Type) -> dict:
    """Get template information."""
    return {
        "name": template_class.__name__,
        "module": template_class.__module__,
    }


def get_auto_type_from_template(template_class: Type) -> str:
    """Infer AutoType from template class."""
    module = template_class.__module__

    if ".templates.zh." in module or ".templates.en." in module:
        return "AutoGraph"

    return "AutoGraph"
