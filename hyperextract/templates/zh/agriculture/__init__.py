"""
农业领域模板，用于从农业文档中提取结构化知识。

包含作物技术手册、巡田报告、土壤分析报告等模板。
"""

# 农业技术手册
from .crop_growth_cycle import CropGrowthCycle
from .pest_control_hypergraph import PestControlHypergraph

# 巡田报告
from .field_observation_list import FieldObservationList

# 土壤分析报告
from .soil_nutrient_model import SoilNutrientModel
from .amendment_plan import AmendmentPlan

__all__ = [
    # 农业技术手册
    "CropGrowthCycle",
    "PestControlHypergraph",
    # 巡田报告
    "FieldObservationList",
    # 土壤分析报告
    "SoilNutrientModel",
    "AmendmentPlan",
]
