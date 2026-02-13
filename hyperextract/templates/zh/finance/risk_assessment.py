from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class RiskFactor(BaseModel):
    """
    从企业披露文件中识别的具体风险因子。
    """

    name: str = Field(
        description='风险名称或类别，例如"供应链中断"、"汇率波动"等。'
    )
    category: str = Field(
        description='风险类别："市场"、"运营"、"监管"、"声誉"、"地缘政治"。'
    )
    description: Optional[str] = Field(
        None, description="风险的详细解释。"
    )


class FinancialImpact(BaseModel):
    """
    可能受风险不利影响的财务或业务指标。
    """

    name: str = Field(
        description='财务指标或业务领域，例如"营业利润率"、"收入"、"股价"等。'
    )
    metric_type: str = Field(
        description='指标类型："收入"、"盈利能力"、"流动性"、"估值"、"声誉"。'
    )


class RiskTransmissionEdge(BaseModel):
    """
    表示从风险因子到财务影响的传导链。
    """

    source: str = Field(description="风险因子名称。")
    target: str = Field(description="受影响的财务指标或业务领域名称。")
    impact_description: str = Field(
        description='风险可能如何不利影响目标，例如"可能降低"、"可能增加"等。'
    )
    likelihood: str = Field(
        description='概率特征："可能"、"较可能"、"不确定"、"罕见"。'
    )
    severity: str = Field(
        description='严重程度："重要"、"显著"、"严重"、"灾难性"。'
    )
    mitigation: Optional[str] = Field(
        None, description="任何公开的缓解策略或控制措施。"
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是专业的金融风险分析师，专门研究企业风险披露。请从 SEC 财报和招股说明书中提取风险因子及其对财务影响的传导路径。\n\n"
    "规则:\n"
    "- 识别风险披露部分（如 Item 1A）中明确提及的风险因子。\n"
    "- 对每项风险，提取其对财务/运营指标的因果链。\n"
    "- 使用源文本中确切的严重程度和概率语言。\n"
    "- 捕捉任何公开的缓解策略。"
)

_NODE_PROMPT = (
    "你是专业的金融风险分析师。从文本中提取所有风险因子和财务指标（节点）。\n\n"
    "提取规则:\n"
    "- 识别并分类风险因子（市场、运营、监管、声誉、地缘政治）。\n"
    "- 识别可能受影响的财务或运营指标（收入、利润率、估值）。\n"
    "- 使用源文本中的确切名称和描述。\n"
    "- 此阶段不建立风险与影响之间的因果关系。"
)

_EDGE_PROMPT = (
    "你是专业的金融风险分析师。在获得风险因子和财务指标清单的基础上，提取因果传导路径（边）。\n\n"
    "提取规则:\n"
    "- 将每个风险因子连接到它可能不利影响的具体财务指标。\n"
    "- 提取确切的影响描述，使用'可能对...产生重大不利影响'等语言。\n"
    "- 使用公开的表述分类概率和严重程度。\n"
    "- 记录与风险相关联的任何缓解策略。\n"
    "- 仅在提供的列表中存在的节点之间创建边。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class RiskAssessmentGraph(AutoGraph[RiskFactor, RiskTransmissionEdge]):
    """
    适用文档: SEC 10-K/10-Q Item 1A（风险因子）、招股说明书风险部分（S-1）、债券评级报告、风险披露文件。

    模板用于系统地从企业披露中提取和映射风险因子及其财务影响。支持结构化风险监测和多份财报的对比分析。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> risk_graph = RiskAssessmentGraph(llm_client=llm, embedder=embedder)
        >>> filing_text = "Item 1A. 风险因子：汇率波动可能对利润率造成重大不利影响..."
        >>> risk_graph.feed_text(filing_text)
        >>> risk_graph.show()
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
        初始化风险评估图谱模板。

        Args:
            llm_client (BaseChatModel): 用于风险和影响提取的 LLM。
            embedder (Embeddings): 用于实体去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=RiskFactor,
            edge_schema=RiskTransmissionEdge,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.likelihood}/{x.severity})-->{x.target.strip()}"
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
        使用 OntoSight 可视化风险传导图。

        Args:
            top_k_nodes_for_search (int): 检索的风险节点数。默认 3。
            top_k_edges_for_search (int): 检索的传导路径数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的节点数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的边数。默认 3。
        """

        def node_label_extractor(node: RiskFactor) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: RiskTransmissionEdge) -> str:
            return f"[{edge.likelihood}/{edge.severity}]"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
