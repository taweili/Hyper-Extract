"""重大事件时间线 - 从 8-K 申报文件中按时间顺序提取重大事件。

提取高管变动、并购公告、财务重述及其他重大事件，
按时间排序，用于事件驱动分析和监管监控。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class MaterialEventEntity(BaseModel):
    """
    参与重大公司事件的实体。
    """

    name: str = Field(
        description="实体名称（例如 公司名称、高管姓名、监管机构）。"
    )
    entity_type: str = Field(
        description="类型：'公司'、'高管'、'监管机构'、'交易对手'、'子公司'、'审计师'。"
    )
    description: Optional[str] = Field(
        None, description="角色或背景（例如 '首席执行官'、'收购方'、'SEC'）。"
    )


class MaterialEventEdge(BaseModel):
    """
    连接实体的重大事件及其时间背景。
    """

    source: str = Field(description="行为实体名称。")
    target: str = Field(description="受影响实体名称。")
    event_type: str = Field(
        description="类型：'高管任命'、'高管离职'、'收购'、'资产剥离'、"
        "'财务重述'、'破产'、'退市'、'重大协议'、'股息宣派'、"
        "'股票拆分'、'监管行动'。"
    )
    start_timestamp: Optional[str] = Field(
        None,
        description="事件发生或公告的日期（例如 '2024-03-15'、'2024年3月15日'）。",
    )
    end_timestamp: Optional[str] = Field(
        None,
        description="如适用的结束日期（例如 生效日期、交割日期）。",
    )
    description: Optional[str] = Field(
        None,
        description="重大事件的详细信息，包括财务条款、条件或监管背景。",
    )
    sec_item: Optional[str] = Field(
        None,
        description="8-K 条目编号（例如 'Item 5.02'、'Item 1.01'、'Item 2.01'）。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位专精于 8-K 即时报告和重大事件披露的监管申报分析师。"
    "提取参与重大事件的实体及其之间的时序关系。\n\n"
    "规则:\n"
    "- 识别涉及的公司、高管、监管机构和交易对手。\n"
    "- 提取每个重大事件及其具体日期。\n"
    "- 在可获取时按 8-K 条目编号对事件进行分类。\n"
    "- 捕获财务条款、条件和监管背景。\n"
    "- 保持时间顺序的准确性。"
)

_NODE_PROMPT = (
    "你是一位监管申报分析师。提取参与重大事件的所有实体（节点）。\n\n"
    "提取规则:\n"
    "- 识别公司、高管、监管机构、审计师和交易对手。\n"
    "- 按类型对每个实体进行分类。\n"
    "- 捕获角色描述。\n"
    "- 此阶段不提取事件或关系。"
)

_EDGE_PROMPT = (
    "你是一位监管申报分析师。在获得实体清单的基础上，提取所有带日期的重大事件（边）。\n\n"
    "提取规则:\n"
    "- 通过重大事件连接实体。\n"
    "- 提取每个事件的具体日期。\n"
    "- 按事件类型和 8-K 条目编号进行分类。\n"
    "- 捕获财务条款和条件。\n"
    "- 仅在提供的列表中存在的节点之间创建边。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class MaterialEventTimeline(AutoTemporalGraph[MaterialEventEntity, MaterialEventEdge]):
    """
    适用文档: SEC 8-K 即时报告、重大事件披露、
    8-K 附带的新闻稿、委托声明书（DEF 14A）。

    模板用于从 8-K 申报文件及相关披露中按时间顺序提取重大公司事件。
    支持事件驱动分析、监管监控和公司治理跟踪。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> timeline = MaterialEventTimeline(llm_client=llm, embedder=embedder)
        >>> filing = "Item 5.02：2024年3月15日，董事会任命张三为首席执行官..."
        >>> timeline.feed_text(filing)
        >>> timeline.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: str = "2024-01-01",
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化重大事件时间线模板。

        Args:
            llm_client (BaseChatModel): 用于事件提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            observation_time (str): 用于解析相对日期的参考时间。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoTemporalGraph 的其他参数。
        """
        super().__init__(
            node_schema=MaterialEventEntity,
            edge_schema=MaterialEventEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}|{x.event_type.lower()}|{x.target.strip().lower()}"
            ),
            time_in_edge_extractor=lambda x: x.start_timestamp or "",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
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
        使用 OntoSight 可视化重大事件时间线。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的事件数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的事件数。默认 3。
        """

        def node_label_extractor(node: MaterialEventEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: MaterialEventEdge) -> str:
            date = f" [{edge.start_timestamp}]" if edge.start_timestamp else ""
            return f"{edge.event_type}{date}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
