from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================


class SupplyEntity(BaseModel):
    """农产品供应链中的参与者或资产（如农场、仓库、加工商、物流商、零售商）。"""

    name: str = Field(description="机构、设施的名称或批次ID。")
    category: str = Field(
        description="类别：'生产者/农场', '加工商', '分销商', '物流商', '零售商', '批次/产品'。"
    )
    location_or_cert: Optional[str] = Field(
        description="地理位置或质量认证（如：有机认证、ISO）。"
    )


class SupplyFlow(BaseModel):
    """供应链参与者之间的产品或信息流。"""

    source: str = Field(description="起始实体（发送方/生产者）。")
    target: str = Field(description="接收实体（购买方/加工商）。")
    flow_type: str = Field(
        description="类型：'发货至', '加工', '销售给', '检测', '认证'。"
    )
    specification: Optional[str] = Field(description="数量、运输方式或质量检测结果。")


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

AGRI_SUPPLY_CHAIN_PROMPT = (
    "你是一位专注于农业的供应链分析师。请从文本中提取溯源与物流图谱。\n\n"
    "提取指南：\n"
    "- 识别从农田到餐桌（生产者、加工商、分销商）涉及的所有参与者。\n"
    "- 映射特定批次或产品经过各个阶段的流动情况。\n"
    "- 捕获文本中提到的质量检测、认证和运输方式。"
)

AGRI_SUPPLY_CHAIN_NODE_PROMPT = "请提取供应链实体：识别特定的农场、工厂、物流枢纽和零售商。记录它们的角色、位置以及提及的任何质量认证。"

AGRI_SUPPLY_CHAIN_EDGE_PROMPT = "建立货物与信息的流动。连接生产者到加工商，以及加工商到零售商。使用'发货至'或'加工'等具体的关系类型，并包含运输方式或数量等细节。"

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================


class AgriSupplyChain(AutoGraph[SupplyEntity, SupplyFlow]):
    """
    用于农产品溯源、物流映射和供应链透明化的模板。

    适用于食品安全追踪、物流优化和贸易分析。

    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> graph = AgriSupplyChain(llm_client=llm, embedder=embedder)
        >>> text = "批次#A102通过冷链卡车从绿色农场（有机认证）运往中央处理厂。"
        >>> graph.feed_text(text)
        >>> print(graph.edges) # 提取物流流向
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
        初始化 AgriSupplyChain 模板。

        Args:
            llm_client: 用于提取的语言模型客户端。
            embedder: 用于去重的嵌入模型。
            extraction_mode: "one_stage" 或 "two_stage"。
            chunk_size: 每个分块的最大字符数。
            chunk_overlap: 分块间的重叠字符数。
            max_workers: 并行处理的最大 worker 数量。
            verbose: 是否开启进度日志。
            **kwargs: 传递给 AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=SupplyEntity,
            edge_schema=SupplyFlow,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.flow_type.lower()})-->{x.target.strip()}"
            ),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=AGRI_SUPPLY_CHAIN_PROMPT,
            prompt_for_node_extraction=AGRI_SUPPLY_CHAIN_NODE_PROMPT,
            prompt_for_edge_extraction=AGRI_SUPPLY_CHAIN_EDGE_PROMPT,
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
        Visualize the graph using OntoSight.

        Args:
            top_k_nodes_for_search (int): Number of nodes to retrieve for search context. Default 3.
            top_k_edges_for_search (int): Number of edges to retrieve for search context. Default 3.
            top_k_nodes_for_chat (int): Number of nodes to retrieve for chat context. Default 3.
            top_k_edges_for_chat (int): Number of edges to retrieve for chat context. Default 3.
        """

        def node_label_extractor(node: SupplyEntity) -> str:
            info = f" ({node.category})" if getattr(node, "category", None) else ""
            return f"{node.name}{info}"

        def edge_label_extractor(edge: SupplyFlow) -> str:
            return f"{edge.flow_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
