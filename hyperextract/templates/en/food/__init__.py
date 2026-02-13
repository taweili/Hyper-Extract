"""
Food & Agriculture domain templates for extracting structured knowledge from food industry documents.

Includes templates for HACCP safety, recipe processes, flavor pairing, and culinary collections.
"""

from .haccp_safety import FoodSafetyHACCPGraph
from .recipe_process import RecipeProcessGraph
from .flavor_pairing import FlavorPairingGraph
from .culinary_dish import CulinaryDishSet

__all__ = [
    "FoodSafetyHACCPGraph",
    "RecipeProcessGraph",
    "FlavorPairingGraph",
    "CulinaryDishSet",
]
