"""估值逻辑图谱 - 映射驱动股票表现的因果链。

提取股票研究报告中从业务驱动因素到估值结论的逻辑链
（例如 新市场 -> 增长 -> 估值倍数扩张）。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class ValuationDriver(BaseModel):
    """
    分析师估值逻辑链中的一个因素。
    """

    name: str = Field(
        description="估值驱动因素名称（例如 '市场份额增长'、'估值倍数扩张'、'DCF 假设'）。"
    )
    driver_type: str = Field(
        description="类型：'基本面'、'估值指标'、'增长驱动因素'、'可比公司'、'折现率'、'终值'。"
    )
    value: Optional[str] = Field(
        None,
        description="量化值或指标（例如 '25 倍前瞻市盈率'、'WACC 9.5%'、'TAM 150 亿美元'）。",
    )
    description: Optional[str] = Field(
        None,
        description="分析师对该驱动因素在估值中所起作用的解释。",
    )


class ValuationEdge(BaseModel):
    """
    分析师估值逻辑中的因果链接。
    """

    source: str = Field(description="原因或输入驱动因素名称。")
    target: str = Field(description="结果或输出驱动因素名称。")
    logic: str = Field(
        description="分析师连接源到目标的推理逻辑"
        "（例如 '更高的云计算采用率推动经常性收入增长'）。"
    )
    direction: str = Field(
        description="影响方向：'正面'、'负面'、'中性'。"
    )
    confidence: Optional[str] = Field(
        None,
        description="分析师的确信度：'高'、'中等'、'低'。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一名股票研究分析师。从本研究报告中提取估值逻辑链：即从业务基本面到估值结论的因果推理。\n\n"
    "规则:\n"
    "- 识别基本面驱动因素、增长催化剂和估值指标。\n"
    "- 提取从业务驱动因素到目标价的因果链。\n"
    "- 捕获分析师在每个链接处的具体推理。\n"
    "- 记录影响方向和确信度。"
)

_NODE_PROMPT = (
    "你是一名股票研究分析师。提取所有估值驱动因素和指标（节点）。\n\n"
    "提取规则:\n"
    "- 识别基本面驱动因素（收入增长、市场份额、TAM）。\n"
    "- 识别估值指标（P/E、EV/EBITDA、DCF、可比倍数）。\n"
    "- 在提及时捕获量化值。\n"
    "- 此阶段不建立因果链接。"
)

_EDGE_PROMPT = (
    "你是一名股票研究分析师。在获得估值驱动因素的基础上，提取连接它们的逻辑推理链（边）。\n\n"
    "提取规则:\n"
    "- 将业务驱动因素连接到财务结果再到估值结论。\n"
    "- 捕获每个链接处的具体推理。\n"
    "- 记录每个链接是正面、负面还是中性影响。\n"
    "- 仅在提供的列表中存在的节点之间创建边。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class ValuationLogicMap(AutoGraph[ValuationDriver, ValuationEdge]):
    """
    适用文档: 股票研究报告、首次覆盖报告、估值分析、分部加总分析、DCF 模型摘要。

    模板用于映射分析师估值逻辑中的因果链。将业务基本面连接到增长驱动因素，
    再到估值指标和目标价，支持投资策略映射和论点比较。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> valuation = ValuationLogicMap(llm_client=llm, embedder=embedder)
        >>> report = "云计算采用推动经常性收入，支撑 30 倍前瞻市盈率..."
        >>> valuation.feed_text(report)
        >>> valuation.show()
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
        初始化估值逻辑图谱模板。

        Args:
            llm_client (BaseChatModel): 用于估值逻辑提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=ValuationDriver,
            edge_schema=ValuationEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}--({x.direction})-->{x.target.strip().lower()}"
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
        使用 OntoSight 可视化估值逻辑图谱。

        Args:
            top_k_nodes_for_search (int): 检索的驱动因素数。默认 3。
            top_k_edges_for_search (int): 检索的逻辑链接数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的驱动因素数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的逻辑链接数。默认 3。
        """

        def node_label_extractor(node: ValuationDriver) -> str:
            val = f": {node.value}" if node.value else ""
            return f"{node.name}{val}"

        def edge_label_extractor(edge: ValuationEdge) -> str:
            return f"[{edge.direction}] {edge.logic[:60]}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
