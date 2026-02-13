from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class SupplyEntity(BaseModel):
    """
    供应链中的参与者（公司、供应商、客户、分销商）。
    """

    name: str = Field(description="实体名称（公司或供应商）。")
    entity_type: str = Field(
        description='类型："客户"、"供应商"、"战略伙伴"、"分销商"、"本公司"。'
    )
    jurisdiction: Optional[str] = Field(
        None, description="地理位置或总部所在地。"
    )
    notes: Optional[str] = Field(
        None, description='其他详情，例如"有机认证"、"ISO 合规"等。'
    )


class SupplyTransaction(BaseModel):
    """
    实体间的供应链关系。
    """

    source: str = Field(description="上游供应商或提供方。")
    target: str = Field(description="下游买方或需求方。")
    transaction_type: str = Field(
        description='类型："供应"、"采购"、"分销"、"战略合作"。'
    )
    product_service: str = Field(
        description='被供应或交易的内容，例如"锂芯片"、"物流服务"等。'
    )
    dependency: str = Field(
        description='依赖程度："关键"、"高"、"中等"、"低"。'
    )
    volume_percentage: Optional[str] = Field(
        None, description='如有披露，总供应或收入的百分比，例如"80%"。'
    )
    geographic_origin: Optional[str] = Field(
        None, description="来源地区或地缘政治考量。"
    )
    risks: Optional[str] = Field(
        None,
        description='披露的风险或脆弱性，例如"单一来源供应商"、"关税暴露"。'
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是供应链分析师。从企业财报和供应链审计中提取供应链实体及其关系。\n\n"
    "规则:\n"
    "- 识别提及的关键供应商、客户和战略伙伴。\n"
    "- 提取交易类型和产品/服务描述。\n"
    "- 根据披露的数量或重要性评估依赖程度。\n"
    "- 记录任何地缘政治或监管风险。"
)

_NODE_PROMPT = (
    "你是供应链分析师。从文本中提取所有供应链参与者（节点）。\n\n"
    "提取规则:\n"
    "- 识别公司、供应商、客户和分销合作伙伴。\n"
    "- 对每个实体在供应链中的角色进行分类。\n"
    "- 记录司法管辖区和任何认证或合规说明。\n"
    "- 此阶段不建立交易关系。"
)

_EDGE_PROMPT = (
    "你是供应链分析师。在获得供应链实体清单的基础上，提取交易关系（边）。\n\n"
    "提取规则:\n"
    "- 将供应商连接到买方，说明具体的产品/服务。\n"
    "- 根据披露的数量百分比或重要性关键词评估依赖程度。\n"
    "- 提取地理来源和任何披露的风险（关税、单一来源）。\n"
    "- 仅连接提供列表中存在的实体。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class SupplyChainGraph(AutoGraph[SupplyEntity, SupplyTransaction]):
    """
    适用文档: 10-K 财报中的业务概览部分、供应商审计报告、供应链韧性披露（10-K Item 1A）、环境社会治理报告、供应商管理文件。

    模板用于映射企业供应链依赖和伙伴关系。支持识别关键供应商、地缘政治敞口和供应链韧性风险。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> supply_chain = SupplyChainGraph(llm_client=llm, embedder=embedder)
        >>> filing = "供应商 XYZ 提供我们 70% 的零部件。我们还依赖于..."
        >>> supply_chain.feed_text(filing)
        >>> supply_chain.show()
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
        初始化供应链图谱模板。

        Args:
            llm_client (BaseChatModel): 用于实体和关系提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=SupplyEntity,
            edge_schema=SupplyTransaction,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.product_service})-->{x.target.strip()}"
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
        使用 OntoSight 可视化供应链图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的关系数。默认 3。
        """

        def node_label_extractor(node: SupplyEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: SupplyTransaction) -> str:
            vol = f" {edge.volume_percentage}" if edge.volume_percentage else ""
            return f"{edge.product_service}{vol} [{edge.dependency}]"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
