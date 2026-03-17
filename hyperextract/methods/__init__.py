"""Methods Layer - Algorithms and strategies for knowledge extraction.

This module organizes concrete algorithms and strategies that operate on
the AutoTypes primitives. It's divided into:
- rag: Retrieval-augmented generation strategies
- typical: Typical/canonical graph construction pipelines
"""

from . import rag
from . import typical
from .registry import (
    register_method,
    get_method,
    list_methods,
    get_method_cfg,
    list_method_cfgs,
    MethodCfg,
)

__all__ = [
    "rag",
    "typical",
    "register_method",
    "get_method",
    "list_methods",
    "get_method_cfg",
    "list_method_cfgs",
    "MethodCfg",
]

