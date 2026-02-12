from typing import List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================

class ConceptNode(BaseModel):
    """
    可能属于多个学科的基础学术概念。
    """
    name: str = Field(description="概念的标准名称。")
    primary_field: str = Field(description="该概念原生所属的主要学科。")

class InterdisciplinaryEdge(BaseModel):
    """
    表示不同领域多个概念之间复杂联系的超边。
    """
    participants: List[str] = Field(
        description="参与该跨学科连接的所有节点名称列表。"
    )
    unifying_theme: str = Field(
        description="将这些概念连接在一起的跨学科主题（例如：'复杂性理论'、'通用设计'）。"
    )
    connectivity_insight: str = Field(
        description="将这些特定知识点连接起来所产生的科学或教学价值。"
    )

# ==============================================================================
# 2. Prompts 提示词
# ==============================================================================

_PROMPT = (
    "你是一位通才和跨学科研究专家。请识别不同学术领域概念之间的深层联系。\n\n"
    "提取规则：\n"
    "- 识别核心概念作为节点。\n"
    "- 创建超边，将多个概念归纳在一个统一的跨学科主题下。\n"
    "- 专注于发现令人惊讶但科学有效的桥梁连接（例如：通过博弈论连接生物学和经济学）。"
)

_NODE_PROMPT = (
    "识别具有跨学科潜力的基础学术概念。\n\n"
    "提取规则：\n"
    "- 提取对各自领域至关重要的名词/概念。\n"
    "- 标注其学科来源。"
)

_EDGE_PROMPT = (
    "识别连接一组概念的“纽带”或称之为超边。\n\n"
    "提取规则：\n"
    "- 只要可能，一个超边应涉及两个以上的节点。\n"
    "- 描述统一这些概念的主题以及这种连接提供的洞察力。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class InterdisciplinaryNexusHypergraph(AutoHypergraph[ConceptNode, InterdisciplinaryEdge]):
    """
    用于映射多点、非二元学术联系的教育领域模板。
    理想用于研究综述、课程跨学科设计以及跨学科知识管理。

    用法示例：
        >>> nexus = InterdisciplinaryNexusHypergraph(llm, embedder)
        >>> nexus.feed_text("‘熵’这一概念同时适用于热力学中的‘热’和信息论中的‘信息’。")
        >>> nexus.extract()
        >>> # 结果将包含一个通过“熵”这一主题连接“热”与“信息”的超边。
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化跨学科纽带超图模板。

        参数描述:
            llm_client (BaseChatModel): 用于提取的语言模型客户端。
            embedder (Embeddings): 用于节点去重的嵌入模型。
            extraction_mode (str): 提取模式。
            chunk_size (int): 文本分片大小。
            chunk_overlap (int): 分片重叠大小。
            max_workers (int): 并行处理进程数。
            verbose (bool): 是否打印日志。
            **kwargs: 透传给 AutoHypergraph 基类的其他参数（如一致性检查开关）。
        """
        super().__init__(
            node_schema=ConceptNode,
            edge_schema=InterdisciplinaryEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.unifying_theme.strip().lower()}_linking_{sorted(x.participants)}"
            ),
            nodes_in_edge_extractor=lambda x: [p.strip().lower() for p in x.participants],
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            **kwargs,
        )
    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ) -> None:
        """
        Visualize the graph using OntoSight.
    
        Args:
            top_k_nodes_for_search (int): Number of nodes to retrieve for search context. Default 3.
            top_k_edges_for_search (int): Number of edges to retrieve for search context. Default 3.
            top_k_nodes_for_chat (int): Number of nodes to retrieve for chat context. Default 3.
            top_k_edges_for_chat (int): Number of edges to retrieve for chat context. Default 3.
        """
        def node_label_extractor(node: ConceptNode) -> str:
            return f"{node.name}"
    
        def edge_label_extractor(edge: InterdisciplinaryEdge) -> str:
            return f"{edge.unifying_theme}"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
