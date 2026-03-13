"""Template Engine - Automatically generate templates from YAML configuration.

This module provides functionality to dynamically generate HyperExtract templates from YAML configuration files.

Usage Examples:
    >>> from hyperextract.utils.template_engine import Gallery, TemplateFactory
    >>>
    >>> # Get template (auto-loaded presets and customs)
    >>> config = Gallery.get("KnowledgeGraph")
    >>> template = TemplateFactory.create(config, llm_client, embedder)
    >>>
    >>> # List all templates
    >>> print(Gallery.list_all())
    >>>
    >>> # Add custom template directory (auto-loaded)
    >>> Gallery.add_path("/path/to/my/templates")
"""

from .config_loader import (
    TemplateConfig,
    ConfigLoader,
    FieldDescription,
    SchemaField,
    ExtractionGuide,
    Identifiers,
    Parameters,
    Display,
)

from .schema_builder import SchemaBuilder

from .identifier_resolver import IdentifierResolver

from .prompt_builder import PromptBuilder

from .template_factory import TemplateFactory

from .template_gallery import Gallery


__all__ = [
    "TemplateConfig",
    "ConfigLoader",
    "FieldDescription",
    "SchemaField",
    "ExtractionGuide",
    "Identifiers",
    "Parameters",
    "Display",
    "SchemaBuilder",
    "IdentifierResolver",
    "PromptBuilder",
    "TemplateFactory",
    "Gallery",
]
