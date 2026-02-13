"""
金融领域模板，用于从财务文档中提取结构化知识。

包含风险评估、市场观点和供应链分析等模板。
"""

from .risk_assessment import RiskAssessmentGraph
from .market_sentiment import MarketSentimentGraph
from .supply_chain import SupplyChainGraph

__all__ = [
    "RiskAssessmentGraph",
    "MarketSentimentGraph",
    "SupplyChainGraph",
]
