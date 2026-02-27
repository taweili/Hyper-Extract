"""
金融领域模板，用于从财务文档中提取结构化知识。

包含 SEC 文件、股票研究报告、招股说明书、财报电话会议、
金融新闻、风险评估和供应链分析等模板。
"""

# SEC 文件 (10-K / 10-Q / 8-K)
from .filing_financial_snapshot import FilingFinancialSnapshot
from .mda_narrative_graph import MDANarrativeGraph
from .filing_risk_factor_set import FilingRiskFactorSet
from .material_event_timeline import MaterialEventTimeline
from .segment_performance_list import SegmentPerformanceList
from .financial_data_temporal_graph import FinancialDataTemporalGraph
from .risk_assessment import RiskAssessmentGraph
from .supply_chain import SupplyChainGraph

# 股票研究报告
from .research_note_summary import ResearchNoteSummary
from .financial_forecast import FinancialForecast
from .valuation_logic_map import ValuationLogicMap
from .factor_influence_hypergraph import FactorInfluenceHypergraph
from .risk_factor_list import RiskFactorList

# 招股说明书 / IPO 文件 (S-1)
from .shareholder_structure import ShareholderStructure
from .proceeds_usage import ProceedsUsage
from .company_history_timeline import CompanyHistoryTimeline

# 财报电话会议记录
from .earnings_call_summary import EarningsCallSummary
from .management_guidance_list import ManagementGuidanceList
from .discussion_graph import DiscussionGraph
from .call_sentiment_hypergraph import CallSentimentHypergraph

# 金融新闻与市场评论
from .market_sentiment_model import MarketSentimentModel
from .financial_event_causal_graph import FinancialEventCausalGraph
from .multi_source_sentiment_hypergraph import MultiSourceSentimentHypergraph
from .market_narrative_timeline import MarketNarrativeTimeline

__all__ = [
    # SEC 文件
    "FilingFinancialSnapshot",
    "MDANarrativeGraph",
    "FilingRiskFactorSet",
    "MaterialEventTimeline",
    "SegmentPerformanceList",
    "FinancialDataTemporalGraph",
    "RiskAssessmentGraph",
    "SupplyChainGraph",
    # 股票研究报告
    "ResearchNoteSummary",
    "FinancialForecast",
    "ValuationLogicMap",
    "FactorInfluenceHypergraph",
    "RiskFactorList",
    # 招股说明书 / IPO
    "ShareholderStructure",
    "ProceedsUsage",
    "CompanyHistoryTimeline",
    # 财报电话会议
    "EarningsCallSummary",
    "ManagementGuidanceList",
    "DiscussionGraph",
    "CallSentimentHypergraph",
    # 金融新闻
    "MarketSentimentModel",
    "FinancialEventCausalGraph",
    "MultiSourceSentimentHypergraph",
    "MarketNarrativeTimeline",
]
