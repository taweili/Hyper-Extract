"""财务数据时序图谱 - 跨报告期追踪财务指标变化。

从 SEC 申报文件中提取财务实体（公司、分部、科目）及其跨期的
量化关系，支持多期趋势分析、分部级追踪和跨期财务对比。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class FinancialDataEntity(BaseModel):
    """
    SEC 申报文件中出现的财务实体：公司、业务分部或财务指标/科目。
    """

    name: str = Field(
        description="实体的规范名称（例如 '苹果公司'、'云服务分部'、'营业收入'、'净利润'）。"
    )
    entity_type: str = Field(
        description="类型：'公司'、'分部'、'财务指标'、'会计科目'、'外部因素'。"
    )
    description: Optional[str] = Field(
        None,
        description="简要背景说明（例如 '消费电子业务板块'、'GAAP 收入确认口径'）。",
    )


class FinancialDataEdge(BaseModel):
    """
    锚定于特定报告期的时序财务关系，将实体与指标、指标与指标关联起来。
    """

    source: str = Field(
        description="报告主体或贡献因素（例如 '苹果公司'、'服务分部'）。"
    )
    target: str = Field(
        description="财务指标或会计科目（例如 '营业收入'、'经营利润'）。"
    )
    relationship: str = Field(
        description="关系类型：'报告'、'贡献'、'衍生'、'同比变化'、'比率'、'受影响于'。"
    )
    value: Optional[str] = Field(
        None,
        description="报告金额或百分比（例如 '3943亿美元'、'+7.8%'、'45.6%'）。",
    )
    unit: Optional[str] = Field(
        None,
        description="金额单位或币种（例如 '百万美元'、'百分比'）。",
    )
    fiscal_period: Optional[str] = Field(
        None,
        description="财务期间标签（例如 'FY2024'、'Q3 2024'、'截至2024年12月31日的年度'）。",
    )
    start_timestamp: Optional[str] = Field(
        None,
        description="报告期开始日期（例如 '2024-01-01'、'2024年1月1日'）。",
    )
    end_timestamp: Optional[str] = Field(
        None,
        description="报告期结束日期（例如 '2024-12-31'、'2024年12月31日'）。",
    )
    description: Optional[str] = Field(
        None,
        description="补充说明，如对比备注、重述标记或会计处理方式等。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位资深财务分析师，擅长多期 SEC 申报文件分析。"
    "从文本中提取财务实体及其跨时间的量化关系。\n\n"
    "规则:\n"
    "- 将公司、业务分部和财务指标/会计科目识别为实体。\n"
    "- 对每个报告数据，创建连接报告主体与指标的边，附带精确数值和财务期间。\n"
    "- 将同比变化、衍生比率和分部贡献分别作为独立的边提取。\n"
    "- 保留源文本中的精确金额和单位。\n"
    "- 统一使用一致的财务期间标签（例如 'FY2024'、'Q3 2024'）。\n"
    "- 在可获取时提取多期对比数据。\n"
    "- 不要计算文本中未明确给出的数值。"
)

_NODE_PROMPT = (
    "你是一位资深财务分析师。从文本中提取所有财务实体（节点）。\n\n"
    "提取规则:\n"
    "- 识别申报公司及其子公司或关联方。\n"
    "- 识别文中提到的业务分部或地理区域。\n"
    "- 识别财务指标和会计科目（营业收入、净利润、每股收益、总资产等）。\n"
    "- 识别文中明确提及的影响财务的外部因素（例如 '汇率逆风'、'关税影响'）。\n"
    "- 按类型分类：公司、分部、财务指标、会计科目、外部因素。\n"
    "- 不要将日期、时间期间或纯数值提取为实体。"
)

_EDGE_PROMPT = (
    "你是一位资深财务分析师。在获得实体清单的基础上，提取所有带时间上下文的财务数据关系（边）。\n\n"
    "提取规则:\n"
    "- 对每个报告数据，连接报告主体/分部与相应的财务指标。\n"
    "- 每条边必须包含精确数值、单位和财务期间。\n"
    "- 将同比变化单独提取为边（例如 source='营业收入', target='收入增长率', "
    "relationship='同比变化', value='+7.8%'）。\n"
    "- 提取分部贡献（例如 source='服务分部', target='营业收入', "
    "relationship='贡献', value='852亿美元'）。\n"
    "- 提取文中明确列出的衍生比率（例如 source='毛利润', target='毛利率', "
    "relationship='比率', value='45.6%'）。\n"
    "- 根据财务期间的起止边界赋值 start_timestamp 和 end_timestamp。\n"
    "- 仅在提供的实体列表中存在的节点之间创建边。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class FinancialDataTemporalGraph(
    AutoTemporalGraph[FinancialDataEntity, FinancialDataEdge]
):
    """
    适用文档: SEC 10-K 年度报告、10-Q 季度报告、20-F 外国发行人年报、
    包含多期财务报表的年度报告、分部披露。

    模板用于从 SEC 申报文件构建财务数据时序知识图谱。
    与 FilingFinancialSnapshot（单期扁平提取）不同，本模板保留了**时间维度**——
    将公司、业务分部和财务指标建模为节点，通过带有精确数值和财务期间标签的
    时序边进行连接，支持多期趋势分析和跨期对比。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> graph = FinancialDataTemporalGraph(llm_client=llm, embedder=embedder)
        >>> filing = "FY2024年度，苹果公司报告营收3943亿美元，较FY2023年的3658亿美元增长7.8%..."
        >>> graph.feed_text(filing)
        >>> graph.show()
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
        初始化财务数据时序图谱模板。

        Args:
            llm_client (BaseChatModel): 用于财务数据提取的 LLM。
            embedder (Embeddings): 用于去重和语义检索的嵌入模型。
            observation_time (str): 用于解析相对时间表达式的参考日期。
            extraction_mode (str): "one_stage" 或 "two_stage"（默认 "two_stage"）。
            chunk_size (int): 每个文本分块的最大字符数。
            chunk_overlap (int): 相邻分块之间的重叠字符数。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoTemporalGraph 的其他参数。
        """
        super().__init__(
            node_schema=FinancialDataEntity,
            edge_schema=FinancialDataEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}|{x.relationship.lower()}|{x.target.strip().lower()}"
            ),
            time_in_edge_extractor=lambda x: x.fiscal_period or x.start_timestamp or "",
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
        使用 OntoSight 可视化财务数据时序图谱。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的数据边数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的数据边数。默认 3。
        """

        def node_label_extractor(node: FinancialDataEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: FinancialDataEdge) -> str:
            parts = [edge.relationship]
            if edge.value:
                parts.append(edge.value)
            if edge.fiscal_period:
                parts.append(f"[{edge.fiscal_period}]")
            elif edge.start_timestamp:
                parts.append(f"[{edge.start_timestamp}]")
            return " ".join(parts)

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
