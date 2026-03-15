"""Template Engine - Dynamically creates knowledge extraction templates from YAML configuration.

Main Components:
- Template: Unified API for template operations
- Gallery: Template library management
- TemplateFactory: Creates template instances from configuration
- RawTemplateCfg: Raw YAML config (multilingual) for validation
- TemplateCfg: Single-language config for actual use
- ConfigLoader: Loads YAML configuration
- SchemaParser: Parses output schemas based on template type
- GuidelineParser: Parses prompts based on template type
- IdentifierResolver: Resolves identifier extractors
"""

from .template import Template
from .gallery import Gallery
from .factory import TemplateFactory, TemplateWrapper
from .builder import (
    RawTemplateCfg,
    TemplateCfg,
    ConfigLoader,
    SchemaBuilder,
    SchemaParser,
    GuidelineParser,
    PromptParser,
    IdentifierResolver,
    OptionsBuilder,
    parse_multi_lang,
    GuidelineSchema,
    GuidelineSchemaMono,
    OutputSchema,
    OutputSchemaMono,
    DisplaySchema,
    DisplaySchemaMono,
    IdentifiersSchema,
    FieldSchema,
    FieldsDefinition,
)


__all__ = [
    "Template",
    "Gallery",
    "TemplateFactory",
    "TemplateWrapper",
    "RawTemplateCfg",
    "TemplateCfg",
    "ConfigLoader",
    "SchemaBuilder",
    "SchemaParser",
    "GuidelineParser",
    "PromptParser",
    "IdentifierResolver",
    "OptionsBuilder",
    "parse_multi_lang",
    "GuidelineSchema",
    "GuidelineSchemaMono",
    "OutputSchema",
    "OutputSchemaMono",
    "DisplaySchema",
    "DisplaySchemaMono",
    "IdentifiersSchema",
    "FieldSchema",
    "FieldsDefinition",
]
