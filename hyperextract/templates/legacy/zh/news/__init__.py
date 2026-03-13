"""
新闻领域模板，用于从新闻文档中提取结构化知识。

包含深度调查报道、突发新闻与电讯、政策解读与社论等模板。
"""

# 深度调查报道
from .investigative_context_graph import InvestigativeContextGraph
from .complex_relation_net import ComplexRelationNet
from .key_event_sequence import KeyEventSequence

# 突发新闻与电讯
from .news_entity_graph import NewsEntityGraph
from .news_summary_model import NewsSummaryModel
from .live_update_timeline import LiveUpdateTimeline

# 政策解读与社论
from .viewpoint_structure import ViewpointStructure
from .impact_chain import ImpactChain

__all__ = [
    # 深度调查报道
    "InvestigativeContextGraph",
    "ComplexRelationNet",
    "KeyEventSequence",
    # 突发新闻与电讯
    "NewsEntityGraph",
    "NewsSummaryModel",
    "LiveUpdateTimeline",
    # 政策解读与社论
    "ViewpointStructure",
    "ImpactChain",
]
