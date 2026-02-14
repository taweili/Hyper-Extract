"""
食品与农业领域模板，用于从食品工业文档中提取结构化知识。

包含 HACCP 安全、食谱流程、风味配对和烹饪菜谱集等模板。
"""

from .haccp_safety import FoodSafetyHACCPGraph
from .recipe_process import RecipeProcessGraph
from .culinary_dish import CulinaryDishSet

__all__ = [
    "FoodSafetyHACCPGraph",
    "RecipeProcessGraph",
    "CulinaryDishSet",
]
