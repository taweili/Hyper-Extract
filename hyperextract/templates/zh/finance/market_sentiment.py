from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class MarketDriver(BaseModel):
    """
    影响市场前景的宏观经济或公司特定因素。
    """

    name: str = Field(
        description='驱动因素名称，例如"AI 需求"、"降息预期"、"监管明确化"等。'
    )
    driver_type: str = Field(
        description='类型："宏观"、"行业"、"公司特定"、"催化剂"。'
    )
    description: Optional[str] = Field(
        None, description="为什么这个驱动因素重要的详细解释。"
    )


class MarketTarget(BaseModel):
    """
    受市场驱动因素影响的交易资产或财务指标。
    """

    ticker: str = Field(description='股票代码，例如"AAPL"、"AI 指数"。')
    asset_type: str = Field(
        description='类型："股票"、"指数"、"债券"、"商品"、"货币"。'
    )
    metric: Optional[str] = Field(
        None, description='具体指标（如适用），例如"EPS"、"P/E 比率"。'
    )


class AnalystInfluence(BaseModel):
    """
    表示市场驱动因素如何影响资产前景。
    """

    source: str = Field(description="市场驱动因素名称。")
    target: str = Field(description="受影响资产/指标的股票代码。")
    sentiment: str = Field(
        description='情绪方向："正面"、"负面"、"中性"。'
    )
    strength: str = Field(
        description='影响力强度："强"、"中等"、"弱"。'
    )
    analyst_view: str = Field(
        description='分析师建议或目标调整，例如"升级为买入"、"将目标价上调至 150 美元"等。'
    )
    time_horizon: Optional[str] = Field(
        None, description='预期时间框架，例如"FY24"、"6-12 个月"、"长期"。'
    )
    source_firm: Optional[str] = Field(
        None, description="研究机构或分析师来源的名称。"
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是股票研究分析师。从研究报告和宏观经济评论中提取市场驱动因素、目标资产和分析师观点。\n\n"
    "规则:\n"
    "- 识别市场驱动因素（催化剂、政策变化、行业趋势）。\n"
    "- 识别哪些资产（股票、指数、债券）受影响。\n"
    "- 提取情绪方向和分析师建议。\n"
    "- 记录时间框架和来源归属。"
)

_NODE_PROMPT = (
    "你是股票研究分析师。从文本中提取所有市场驱动因素和目标资产（节点）。\n\n"
    "提取规则:\n"
    "- 识别宏观经济因素、政策变化和催化剂事件。\n"
    "- 识别被讨论的股票代码和具体财务指标。\n"
    "- 按类型分类每个节点（宏观、公司特定等）。\n"
    "- 此阶段不建立驱动因素如何影响资产的关系。"
)

_EDGE_PROMPT = (
    "你是股票研究分析师。在获得市场驱动因素和目标资产清单的基础上，提取影响关系（边）。\n\n"
    "提取规则:\n"
    "- 将每个驱动因素连接到它影响的具体资产。\n"
    "- 提取分析师观点（升级/降级语言、目标价变化）。\n"
    "- 分类情绪方向和影响力强度。\n"
    "- 记录机构/分析师来源和预期时间框架。\n"
    "- 仅在提供的列表中存在的节点之间创建边。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class MarketSentimentGraph(AutoGraph[MarketDriver, AnalystInfluence]):
    """
    适用文档: 股票研究报告、宏观策略观点、财报电话会议记录、宏观经济评论、分析师警报和更新。

    模板用于提取和映射市场驱动因素到其对资产估值和分析师建议的预期影响。支持跟踪投资主题演变和共识转变。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> sentiment = MarketSentimentGraph(llm_client=llm, embedder=embedder)
        >>> report = "AI 需求加速是关键驱动因素。我们将科技股升级为增持..."
        >>> sentiment.feed_text(report)
        >>> sentiment.show()
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
        初始化市场观点图谱模板。

        Args:
            llm_client (BaseChatModel): 用于驱动因素和观点提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=MarketDriver,
            edge_schema=AnalystInfluence,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.sentiment})-->{x.target.strip()}"
            ),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
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
        使用 OntoSight 可视化市场观点图。

        Args:
            top_k_nodes_for_search (int): 检索的驱动因素数。默认 3。
            top_k_edges_for_search (int): 检索的影响关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的驱动因素数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的影响关系数。默认 3。
        """

        def node_label_extractor(node: MarketDriver) -> str:
            return f"{node.name} ({node.driver_type})"

        def edge_label_extractor(edge: AnalystInfluence) -> str:
            return f"[{edge.sentiment}/{edge.strength}] {edge.analyst_view}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
