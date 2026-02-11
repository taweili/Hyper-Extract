"""Methods Layer - Algorithms and strategies for knowledge extraction.

This module organizes concrete algorithms and strategies that operate on
the AutoTypes primitives. It's divided into:
- rag: Retrieval-augmented generation strategies
- typical: Typical/canonical graph construction pipelines
"""

from . import rag
from . import typical

__all__ = ["rag", "typical"]

