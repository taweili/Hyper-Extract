"""多源情绪超图 - 整合多个来源的情绪信号。

整合多个来源的情绪信号：{新闻文章, 社交媒体帖子, 分析师报告}
-> 聚合情绪 -> 受影响实体，用于集成评分。
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class SentimentSource(BaseModel):
    """
    情绪信号的来源或受影响的市场实体。
    """

    name: str = Field(
        description='来源或实体的名称（例如"彭博社文章"、"高盛分析师报告"、"AAPL"、"科技板块"）。'
    )
    source_type: str = Field(
        description='类型："新闻文章"、"分析师报告"、"社交媒体"、"市场数据"、"公司公告"、'
        '"受影响实体"、"板块"、"指数"。'
    )
    sentiment_signal: Optional[str] = Field(
        None,
        description='该来源的个别情绪："看涨"、"看跌"、"中性"。',
    )
    credibility: Optional[str] = Field(
        None,
        description='来源可信度评估："一级"、"二级"、"未验证"。',
    )


class AggregatedSentiment(BaseModel):
    """
    融合多个来源的聚合情绪信号，针对受影响实体。
    """

    fusion_name: str = Field(
        description='描述性名称（例如"AAPL 来自 3 个来源的看涨共识"）。'
    )
    participating_sources: List[str] = Field(
        description='参与此融合的所有来源和受影响实体的名称。'
    )
    aggregated_polarity: str = Field(
        description='融合情绪："强烈看涨"、"看涨"、"中性"、"看跌"、"强烈看跌"、"冲突"。'
    )
    agreement_level: str = Field(
        description='来源一致性："一致"、"多数"、"分裂"、"矛盾"。'
    )
    affected_entity: Optional[str] = Field(
        None,
        description='情绪适用的主要实体（股票代码或板块）。',
    )
    signal_strength: Optional[str] = Field(
        None,
        description='交易用的整体信号强度："可操作"、"参考性"、"噪音"。',
    )
    conflicting_views: Optional[str] = Field(
        None,
        description='任何不同或冲突的情绪信号摘要。',
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是多源情绪融合分析师。从不同来源提取情绪信号并创建聚合情绪视图。\n\n"
    "规则:\n"
    "- 识别每个不同的情绪来源（新闻、分析师报告、社交媒体）。\n"
    "- 提取每个来源的个别情绪信号。\n"
    "- 创建连接来源到受影响实体的聚合情绪超边。\n"
    "- 评估各来源之间的一致性。\n"
    "- 记录冲突观点和信号强度。"
)

_NODE_PROMPT = (
    "你是情绪融合分析师。提取所有情绪来源和受影响实体（节点）。\n\n"
    "提取规则:\n"
    "- 识别新闻文章、分析师报告和社交媒体帖子。\n"
    "- 识别受影响实体（股票代码、板块、指数）。\n"
    "- 捕捉每个来源的个别情绪。\n"
    "- 此阶段不创建聚合视图。"
)

_EDGE_PROMPT = (
    "你是情绪融合分析师。在获得来源和实体清单的基础上，创建聚合情绪融合（超边）。\n\n"
    "提取规则:\n"
    "- 每条超边连接多个来源到一个受影响实体。\n"
    "- 评估聚合情绪极性和一致性水平。\n"
    "- 评估交易用途的信号强度。\n"
    "- 记录任何冲突观点。\n"
    "- 仅引用提供列表中存在的元素。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class MultiSourceSentimentHypergraph(
    AutoHypergraph[SentimentSource, AggregatedSentiment]
):
    """
    适用文档: 财经新闻流、分析师报告合集、社交媒体数据流、多源市场情报。

    模板用于整合多个来源的情绪信号。使用超边将多个来源连接到聚合情绪视图，
    支持集成情绪评分和虚假信号过滤。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> fusion = MultiSourceSentimentHypergraph(llm_client=llm, embedder=embedder)
        >>> text = "彭博社报道科技股上涨。同时高盛上调 AAPL 评级。推特情绪看涨。"
        >>> fusion.feed_text(text)
        >>> fusion.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化多源情绪超图模板。

        Args:
            llm_client (BaseChatModel): 用于情绪融合的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoHypergraph 的其他参数。
        """
        super().__init__(
            node_schema=SentimentSource,
            edge_schema=AggregatedSentiment,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: x.fusion_name.strip().lower(),
            nodes_in_edge_extractor=lambda x: tuple(
                s.strip().lower() for s in x.participating_sources
            ),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
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
        使用 OntoSight 可视化多源情绪超图。

        Args:
            top_k_nodes_for_search (int): 检索的来源数。默认 3。
            top_k_edges_for_search (int): 检索的融合数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的来源数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的融合数。默认 3。
        """

        def node_label_extractor(node: SentimentSource) -> str:
            signal = f" [{node.sentiment_signal}]" if node.sentiment_signal else ""
            return f"{node.name} ({node.source_type}){signal}"

        def edge_label_extractor(edge: AggregatedSentiment) -> str:
            return f"[{edge.aggregated_polarity}] {edge.fusion_name}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
