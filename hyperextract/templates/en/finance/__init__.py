"""
Finance domain templates for extracting structured knowledge from financial documents.

Includes templates for risk assessment, market sentiment, and supply chain analysis.
"""

from .risk_assessment import RiskAssessmentGraph
from .market_sentiment import MarketSentimentGraph
from .supply_chain import SupplyChainGraph

__all__ = [
    "RiskAssessmentGraph",
    "MarketSentimentGraph",
    "SupplyChainGraph",
]
