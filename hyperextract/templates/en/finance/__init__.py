"""
Finance domain templates for extracting structured knowledge from financial documents.

Includes templates for SEC filings, equity research, prospectuses, earnings calls,
financial news, risk assessment, and supply chain analysis.
"""

# SEC Filings (10-K / 10-Q / 8-K)
from .filing_financial_snapshot import FilingFinancialSnapshot
from .mda_narrative_graph import MDANarrativeGraph
from .filing_risk_factor_set import FilingRiskFactorSet
from .material_event_timeline import MaterialEventTimeline
from .segment_performance_list import SegmentPerformanceList
from .financial_data_temporal_graph import FinancialDataTemporalGraph
from .risk_assessment import RiskAssessmentGraph
from .supply_chain import SupplyChainGraph

# Equity Research Reports
from .research_note_summary import ResearchNoteSummary
from .financial_forecast import FinancialForecast
from .valuation_logic_map import ValuationLogicMap
from .factor_influence_hypergraph import FactorInfluenceHypergraph
from .risk_factor_list import RiskFactorList

# Prospectuses / IPO Filings (S-1)
from .shareholder_structure import ShareholderStructure
from .proceeds_usage import ProceedsUsage
from .company_history_timeline import CompanyHistoryTimeline

# Earnings Call Transcripts
from .earnings_call_summary import EarningsCallSummary
from .management_guidance_list import ManagementGuidanceList
from .analyst_qa_graph import AnalystQAGraph
from .call_sentiment_hypergraph import CallSentimentHypergraph

# Financial News & Market Commentary
from .market_sentiment_model import MarketSentimentModel
from .financial_event_causal_graph import FinancialEventCausalGraph
from .multi_source_sentiment_hypergraph import MultiSourceSentimentHypergraph
from .market_narrative_timeline import MarketNarrativeTimeline

__all__ = [
    # SEC Filings
    "FilingFinancialSnapshot",
    "MDANarrativeGraph",
    "FilingRiskFactorSet",
    "MaterialEventTimeline",
    "SegmentPerformanceList",
    "FinancialDataTemporalGraph",
    "RiskAssessmentGraph",
    "SupplyChainGraph",
    # Equity Research
    "ResearchNoteSummary",
    "FinancialForecast",
    "ValuationLogicMap",
    "FactorInfluenceHypergraph",
    "RiskFactorList",
    # Prospectuses / IPO
    "ShareholderStructure",
    "ProceedsUsage",
    "CompanyHistoryTimeline",
    # Earnings Calls
    "EarningsCallSummary",
    "ManagementGuidanceList",
    "AnalystQAGraph",
    "CallSentimentHypergraph",
    # Financial News
    "MarketSentimentModel",
    "FinancialEventCausalGraph",
    "MultiSourceSentimentHypergraph",
    "MarketNarrativeTimeline",
]
