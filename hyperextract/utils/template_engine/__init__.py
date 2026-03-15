"""Template Engine - Dynamically creates knowledge extraction templates from YAML configuration.

Main Components:
- Template: Unified API for template operations
- Gallery: Template library management
- TemplateFactory: Creates template instances from configuration
- TemplateCfg: Template config (supports multilingual)
- ConfigLoader: Loads YAML configuration
- localize_template: Converts multilingual config to single-language config
- SchemaParser: Parses output schemas based on template type
- GuidelineParser: Parses prompts based on template type
- IdentifierResolver: Resolves identifier extractors
"""

from .template import Template
from .gallery import Gallery
from .factory import TemplateFactory, TemplateWrapper
from .parsers import (
    TemplateCfg,
    OutputParser,
    GuidelineParser,
    PromptParser,
    IdentifierResolver,
    OptionsBuilder,
    _localize_data,
    localize_template,
)


__all__ = [
    "Template",
    "Gallery",
    "TemplateFactory",
    "TemplateWrapper",
    "TemplateCfg",
    "OutputParser",
    "GuidelineParser",
    "PromptParser",
    "IdentifierResolver",
    "OptionsBuilder",
    "_localize_data",
    "localize_template",
]
