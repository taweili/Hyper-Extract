"""HyperExtract - AI-powered data structure extraction from unstructured text.

This library provides Auto-prefixed intelligent data structures that automatically
extract structured information from text using Large Language Models (LLMs).
"""

from .core import AutoModel, AutoList, AutoSet

__version__ = "0.2.0"

__all__ = [
    "AutoModel",
    "AutoList",
    "AutoSet",
]
