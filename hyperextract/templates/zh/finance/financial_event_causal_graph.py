"""金融事件因果图谱 - 将金融事件映射到市场反应。

将金融事件映射到受影响的实体和下游市场反应
（例如"美联储加息 -> 银行板块上涨 -> 债券收益率上升"），用于事件驱动策略。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class FinancialEventNode(BaseModel):
    """
    事件链中的金融事件、市场实体或市场反应。
    """

    name: str = Field(
        description='事件或实体的名称（例如"美联储加息"、"银行板块"、"美元走强"）。'
    )
    node_type: str = Field(
        description='类型："事件"、"实体"、"市场反应"、"政策"、"经济指标"、"板块"。'
    )
    description: Optional[str] = Field(
        None,
        description='关于该事件/实体的背景或详细信息。',
    )


class EventCausalEdge(BaseModel):
    """
    从金融事件到市场反应的因果关系。
    """

    source: str = Field(description='原因事件或实体名称。')
    target: str = Field(description='结果或下游反应名称。')
    causal_mechanism: str = Field(
        description='原因如何导致目标效果'
        '（例如"更高利率降低借贷成本敏感性"）。'
    )
    direction: str = Field(
        description='影响方向："正面"、"负面"、"不确定"。'
    )
    magnitude: Optional[str] = Field(
        None,
        description='陈述或隐含的幅度（例如"标普 500 上涨 2%"、"50 个基点的影响"）。',
    )
    timing: Optional[str] = Field(
        None,
        description='反应时间："即时"、"当日"、"多日"、"滞后"。',
    )
    confidence: Optional[str] = Field(
        None,
        description='因果关系的置信度："已确立"、"可能"、"推测性"。',
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是宏观策略师和财经新闻分析师。从这篇新闻或评论中提取金融事件、受影响的市场实体"
    "以及连接它们的因果链。\n\n"
    "规则:\n"
    "- 识别触发事件（政策决议、财报、经济数据发布）。\n"
    "- 识别受影响的实体（板块、个股、指数、大宗商品）。\n"
    "- 映射从事件到市场反应的因果链。\n"
    "- 捕捉反应的幅度和时间。\n"
    "- 记录每条因果关系的置信度。"
)

_NODE_PROMPT = (
    "你是宏观策略师。提取所有金融事件、实体和市场反应（节点）。\n\n"
    "提取规则:\n"
    "- 识别触发事件和政策决议。\n"
    "- 识别市场板块、指数和大宗商品。\n"
    "- 识别市场反应和价格变动。\n"
    "- 此阶段不建立因果关系。"
)

_EDGE_PROMPT = (
    "你是宏观策略师。在获得事件和实体清单的基础上，提取因果链（边）。\n\n"
    "提取规则:\n"
    "- 将事件连接到其下游市场效果。\n"
    "- 描述每条链路的因果机制。\n"
    "- 记录影响方向、幅度和时间。\n"
    "- 仅在提供的列表中存在的节点之间创建边。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class FinancialEventCausalGraph(AutoGraph[FinancialEventNode, EventCausalEdge]):
    """
    适用文档: 财经新闻文章、市场评论、宏观策略报告、经济数据发布、
    央行沟通文件、地缘政治新闻。

    模板用于将金融事件映射到其下游市场反应。通过从新闻和评论中提取因果链，
    支持事件驱动策略开发和宏观影响分析。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> causal = FinancialEventCausalGraph(llm_client=llm, embedder=embedder)
        >>> news = "美联储加息 25 个基点，推动银行股上涨，同时科技股遭到抛售..."
        >>> causal.feed_text(news)
        >>> causal.show()
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
        初始化金融事件因果图谱模板。

        Args:
            llm_client (BaseChatModel): 用于事件链提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=FinancialEventNode,
            edge_schema=EventCausalEdge,
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
        使用 OntoSight 可视化金融事件因果图。

        Args:
            top_k_nodes_for_search (int): 检索的事件/实体数。默认 3。
            top_k_edges_for_search (int): 检索的因果关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的事件/实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的因果关系数。默认 3。
        """

        def node_label_extractor(node: FinancialEventNode) -> str:
            return f"{node.name} ({node.node_type})"

        def edge_label_extractor(edge: EventCausalEdge) -> str:
            mag = f" [{edge.magnitude}]" if edge.magnitude else ""
            return f"[{edge.direction}]{mag} {edge.causal_mechanism[:50]}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
