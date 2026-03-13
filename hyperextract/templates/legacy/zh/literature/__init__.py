"""文学与影视领域知识模板

本模块提供用于处理影视剧本、长篇小说和文学评论的模板。
"""

# 影视剧本模板
from .scene_event_hypergraph import SceneEventHypergraph
from .character_arc_timeline import NarrativeTimeline

# 长篇小说模板
from .complex_character_relation import ComplexCharacterRelation
from .story_entity_graph import StoryEntityGraph
from .narrative_event_chain import NarrativeEventChain

# 文学评论模板
from .motif_association_net import MotifAssociationNet
from .critique_argument_hypergraph import CritiqueArgumentHypergraph
from .narrative_structure_tree import NarrativeStructureTree

__all__ = [
    # 影视剧本模板
    "SceneEventHypergraph",
    "NarrativeTimeline",
    # 长篇小说模板
    "ComplexCharacterRelation",
    "StoryEntityGraph",
    "NarrativeEventChain",
    # 文学评论模板
    "MotifAssociationNet",
    "CritiqueArgumentHypergraph",
    "NarrativeStructureTree",
]
