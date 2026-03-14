"""Template Engine - Dynamically creates knowledge extraction templates from YAML configuration.

Main Components:
- Template: Unified API for template operations
- Gallery: Template library management
- TemplateFactory: Creates template instances from configuration
- TemplateConfig: Configuration model
- ConfigLoader: Loads YAML configuration
- SchemaBuilder: Dynamically generates Pydantic Schema
- PromptBuilder: Builds extraction prompts
- IdentifierResolver: Resolves identifier extractors
"""

from .template import Template
from .gallery import Gallery
from .factory import TemplateFactory, TemplateWrapper
from .builder import (
    TemplateConfig,
    ConfigLoader,
    SchemaBuilder,
    PromptBuilder,
    IdentifierResolver,
    OptionsBuilder,
)
from .builder.prompt import Guideline
from .builder.schema import OutputDefinition, FieldsDefinition


__all__ = [
    "Template",
    "Gallery",
    "TemplateFactory",
    "TemplateWrapper",
    "TemplateConfig",
    "ConfigLoader",
    "SchemaBuilder",
    "PromptBuilder",
    "IdentifierResolver",
    "OptionsBuilder",
    "Guideline",
    "OutputDefinition",
    "FieldsDefinition",
]
