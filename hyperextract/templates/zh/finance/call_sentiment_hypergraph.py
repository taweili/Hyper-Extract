from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class CallTopic(BaseModel):
    """
    财报电话会议中讨论的主题、发言人或情绪驱动因素。
    """

    name: str = Field(
        description="主题元素名称（例如'收入增长'、'CEO 蒂姆·库克'、'AI 投资周期'、'谨慎'）。"
    )
    element_type: str = Field(
        description='类型："主题"、"发言人"、"情绪"、"驱动因素"。'
    )
    description: Optional[str] = Field(
        None, description="该元素的上下文或说明。"
    )


class SentimentCluster(BaseModel):
    """
    连接主题、发言人、情绪和驱动因素的多维情绪聚类。
    """

    cluster_name: str = Field(
        description="描述性名称（例如'CEO 看好 AI 收入'、'CFO 对利润率持谨慎态度'）。"
    )
    participating_elements: List[str] = Field(
        description="此情绪聚类中所有元素的名称（主题 + 发言人 + 情绪 + 驱动因素）。"
    )
    sentiment_polarity: str = Field(
        description='整体情绪方向："看多"、"看空"、"中性"、"混合"。'
    )
    intensity: str = Field(
        description='情绪强度："强"、"中等"、"轻微"。'
    )
    evidence: Optional[str] = Field(
        None,
        description="支持情绪判断的关键引述或意译。",
    )
    shift_from_prior: Optional[str] = Field(
        None,
        description="与前一季度基调的变化（如显著，例如'比第二季度更为谨慎'、'从中性上调'）。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是财报电话会议情绪分析专家。提取主题、发言人、"
    "情绪信号及其多维关系。\n\n"
    "规则:\n"
    "- 识别讨论的关键主题（收入、利润率、指引、战略）。\n"
    "- 识别发言人及其角色。\n"
    "- 评估每个主题-发言人组合的情绪方向和强度。\n"
    "- 超边连接 主题 + 发言人 + 情绪 + 驱动因素。\n"
    "- 记录与前一季度基调的变化。"
)

_NODE_PROMPT = (
    "你是情绪分析专家。从财报电话会议中提取所有主题、发言人、情绪和"
    "驱动因素（节点）。\n\n"
    "提取规则:\n"
    "- 识别讨论的财务主题。\n"
    "- 识别发言人（分析师、管理层）。\n"
    "- 识别情绪标签和驱动因素。\n"
    "- 此阶段不创建情绪聚类。"
)

_EDGE_PROMPT = (
    "你是情绪分析专家。在获得元素清单的基础上，创建多维"
    "情绪聚类（超边）。\n\n"
    "提取规则:\n"
    "- 每个聚类连接 主题 + 发言人 + 情绪 + 驱动因素。\n"
    "- 评估整体情绪方向和强度。\n"
    "- 捕捉支撑证据。\n"
    "- 记录与前几个季度的基调变化。\n"
    "- 仅引用提供列表中存在的元素。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class CallSentimentHypergraph(AutoHypergraph[CallTopic, SentimentCluster]):
    """
    适用文档: 财报电话会议记录、投资者日活动记录、
    管理层报告、行业会议记录。

    模板用于财报电话会议的多维情绪分析。使用超边建模
    {主题, 发言人, 情绪, 驱动因素} 聚类，支持情绪驱动的交易信号和基调变化检测。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> sentiment = CallSentimentHypergraph(llm_client=llm, embedder=embedder)
        >>> transcript = "CEO：我们对 AI 收入增长感到非常兴奋..."
        >>> sentiment.feed_text(transcript)
        >>> sentiment.show()
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
        初始化电话会议情绪超图模板。

        Args:
            llm_client (BaseChatModel): 用于情绪提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoHypergraph 的其他参数。
        """
        super().__init__(
            node_schema=CallTopic,
            edge_schema=SentimentCluster,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: x.cluster_name.strip().lower(),
            nodes_in_edge_extractor=lambda x: tuple(
                e.strip().lower() for e in x.participating_elements
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
        使用 OntoSight 可视化电话会议情绪超图。

        Args:
            top_k_nodes_for_search (int): 检索的元素数。默认 3。
            top_k_edges_for_search (int): 检索的情绪聚类数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的元素数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的聚类数。默认 3。
        """

        def node_label_extractor(node: CallTopic) -> str:
            return f"{node.name} [{node.element_type}]"

        def edge_label_extractor(edge: SentimentCluster) -> str:
            return f"[{edge.sentiment_polarity}/{edge.intensity}] {edge.cluster_name}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
