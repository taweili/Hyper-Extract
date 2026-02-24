"""管理层讨论与分析叙述图谱 - 从管理层讨论与分析中提取因果关系。

映射 SEC 申报文件 MD&A 部分中从业务驱动因素到财务结果的因果链
（例如"供应链中断 -> 营收下降 -> 利润率压缩"）。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class MDAFactor(BaseModel):
    """
    MD&A 中提及的业务驱动因素、财务结果或运营因素。
    """

    name: str = Field(
        description="因素名称（例如 '供应链中断'、'营收增长'、'利润率压缩'）。"
    )
    factor_type: str = Field(
        description="类型：'业务驱动因素'、'财务结果'、'运营因素'、'战略举措'、'外部因素'。"
    )
    description: Optional[str] = Field(
        None,
        description="管理层对该因素的解释或背景说明。",
    )


class MDANarrativeEdge(BaseModel):
    """
    两个 MD&A 因素之间的因果或解释性关系。
    """

    source: str = Field(description="原因或驱动因素名称。")
    target: str = Field(description="结果或影响因素名称。")
    relationship_type: str = Field(
        description="类型：'导致'、'促成'、'被抵消'、'引发'、'带来'、'被缓解'。"
    )
    magnitude: Optional[str] = Field(
        None,
        description="如有提及的量化影响（例如 '增加了23亿美元'、'300个基点'）。",
    )
    management_attribution: Optional[str] = Field(
        None,
        description="管理层自身的因果解释原文或转述。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位专精于 SEC 申报文件 MD&A（管理层讨论与分析）部分的财务分析师。"
    "提取管理层描述的业务驱动因素、财务结果及其之间的因果关系。\n\n"
    "规则:\n"
    "- 识别管理层讨论的各类因素：营收驱动因素、成本压力、战略变化、外部力量。\n"
    "- 按管理层呈现的方式提取因果链（例如 '需求增长带动了营收增长'）。\n"
    "- 在有说明时捕获量化影响。\n"
    "- 保留管理层的归因表述语言。"
)

_NODE_PROMPT = (
    "你是一位财务分析师。从 MD&A 文本中提取所有业务驱动因素、财务结果和运营因素（节点）。\n\n"
    "提取规则:\n"
    "- 识别营收驱动因素、成本因素、战略举措和外部力量。\n"
    "- 识别财务结果（营收变化、利润率变动、现金流影响）。\n"
    "- 按类型对每个因素进行分类。\n"
    "- 此阶段不建立因果关系。"
)

_EDGE_PROMPT = (
    "你是一位财务分析师。在获得 MD&A 因素清单的基础上，提取管理层描述的因果和解释性关系（边）。\n\n"
    "提取规则:\n"
    "- 按管理层呈现的方式将原因与结果连接。\n"
    "- 分类关系类型（导致、促成、被抵消等）。\n"
    "- 在可获取时提取量化幅度。\n"
    "- 捕获管理层自身的因果解释。\n"
    "- 仅在提供的列表中存在的节点之间创建边。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class MDANarrativeGraph(AutoGraph[MDAFactor, MDANarrativeEdge]):
    """
    适用文档: SEC 10-K/10-Q 第7项（管理层讨论与分析）、
    年度报告 MD&A 部分、中期管理报告。

    模板用于从管理层讨论与分析部分提取因果关系。映射管理层如何解释业务绩效驱动因素
    及其对财务的影响，支持叙述分析和驱动因素归因。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> mda = MDANarrativeGraph(llm_client=llm, embedder=embedder)
        >>> text = "营收增长12%，主要受益于云计算业务的强劲需求..."
        >>> mda.feed_text(text)
        >>> mda.show()
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
        初始化管理层讨论与分析叙述图谱模板。

        Args:
            llm_client (BaseChatModel): 用于因果关系提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=MDAFactor,
            edge_schema=MDANarrativeEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}--({x.relationship_type})-->{x.target.strip().lower()}"
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
        使用 OntoSight 可视化 MD&A 叙述图谱。

        Args:
            top_k_nodes_for_search (int): 检索的因素数。默认 3。
            top_k_edges_for_search (int): 检索的因果关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的因素数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的因果关系数。默认 3。
        """

        def node_label_extractor(node: MDAFactor) -> str:
            return f"{node.name} ({node.factor_type})"

        def edge_label_extractor(edge: MDANarrativeEdge) -> str:
            mag = f" [{edge.magnitude}]" if edge.magnitude else ""
            return f"{edge.relationship_type}{mag}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
