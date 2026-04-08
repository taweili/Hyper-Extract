"""HyperExtract - AI-powered data structure extraction from unstructured text.

This library provides Auto-prefixed intelligent data structures that automatically
extract structured information from text using Large Language Models (LLMs).

Architecture:
- types: Core data structure primitives (AutoModel, AutoList, AutoSet, AutoGraph, etc.)
- methods: Algorithms and strategies (rag, typical graph construction methods)
- templates: Domain-specific extraction templates

Usage:
    from hyperextract import Template

    # List available templates
    Template.list()

    # 1. Create knowledge template (auto reads config from ~/.he/config.toml)
    template = Template.create("general/graph", language="zh")

    # 2. Create method template (language always "en")
    template = Template.create("method/light_rag")
"""

# Core AutoType primitives
from .types import (
    BaseAutoType,
    AutoModel,
    AutoList,
    AutoSet,
    AutoGraph,
    AutoHypergraph,
    AutoTemporalGraph,
    AutoSpatialGraph,
    AutoSpatioTemporalGraph,
)

# Template engine API
from .utils.template_engine import Template

# Logging utilities
from .utils.logging import configure_logging, get_logger, set_log_level


from importlib.metadata import version

__version__ = version("hyperextract")
__author__ = "Yifan Feng"
__email__ = "evanfeng97@gmail.com"

__all__ = [
    # Base class
    "BaseAutoType",
    # Scalar types
    "AutoModel",
    "AutoList",
    "AutoSet",
    # Graph types
    "AutoGraph",
    "AutoHypergraph",
    "AutoTemporalGraph",
    "AutoSpatialGraph",
    "AutoSpatioTemporalGraph",
    # Template engine
    "Template",
    # Logging utilities
    "configure_logging",
    "get_logger",
    "set_log_level",
]
