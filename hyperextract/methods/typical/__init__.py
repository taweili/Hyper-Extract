"""Typical/Canonical Pipelines.

This module contains typical and canonical methods for constructing knowledge graphs
from text, including iText2KG, and other established graph-building techniques.
"""

from .itext2kg import iText2KG
from .itext2kg_star import iText2KG_Star
from .kg_gen import KG_Gen
from .atom import Atom

__all__ = [
    "iText2KG",
    "iText2KG_Star",
    "KG_Gen",
    "Atom",
]
