"""Template Engine - Automatically generate templates from YAML configuration.

This module provides functionality to dynamically generate HyperExtract templates from YAML configuration files.

Usage:
    # Recommended: use Template class
    from hyperextract.utils import Template
    
    Template.list()
    Template.search("知识图谱")
    template = Template.create("knowledge_graph")
    
    # Advanced: use Gallery and Factory directly
    from hyperextract.utils.template_engine import Gallery, TemplateFactory
"""

from .template import Template
from .gallery import Gallery
from .factory import TemplateFactory
from .builder import (
    TemplateConfig,
    ConfigLoader,
    SchemaBuilder,
    PromptBuilder,
    IdentifierResolver,
)

__all__ = [
    "Template",
    "Gallery",
    "TemplateFactory",
    "TemplateConfig",
    "ConfigLoader",
    "SchemaBuilder",
    "PromptBuilder",
    "IdentifierResolver",
]
