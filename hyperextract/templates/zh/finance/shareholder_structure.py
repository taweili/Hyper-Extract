from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class OwnershipEntity(BaseModel):
    """
    股权结构中的实体。
    """

    name: str = Field(
        description="实体名称（例如个人、基金、控股公司、信托）。"
    )
    entity_type: str = Field(
        description='类型："个人"、"机构投资者"、"控股公司"、"风险投资"、'
        '"私募股权"、"信托"、"政府实体"、"发行公司"。'
    )
    description: Optional[str] = Field(
        None,
        description="附加信息（例如'联合创始人兼 CEO'、'B 轮领投机构'）。",
    )


class OwnershipEdge(BaseModel):
    """
    实体之间的持股或控制关系。
    """

    source: str = Field(description="持有方/母公司实体名称。")
    target: str = Field(description="被持有方/子公司实体名称。")
    relationship_type: str = Field(
        description='类型："直接持股"、"间接持股"、"实益所有权"、'
        '"投票权控制"、"董事会席位"、"母子公司"。'
    )
    ownership_percentage: Optional[str] = Field(
        None,
        description="持股比例（例如'15.3%'、'51%'、'控股权'）。",
    )
    share_class: Optional[str] = Field(
        None,
        description="股份类别（例如'A 类普通股'、'B 类（10 倍投票权）'、'C 轮优先股'）。",
    )
    shares_held: Optional[str] = Field(
        None,
        description="持有股份数量（例如'45,000,000 股'）。",
    )
    voting_power: Optional[str] = Field(
        None,
        description="投票权百分比（若与持股比例不同，例如'65% 投票权'）。",
    )
    lock_up_period: Optional[str] = Field(
        None,
        description="IPO 后锁定期（如适用，例如'180 天'）。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是公司治理分析师。从本招股说明书或委托声明文件中提取股权结构，包括股东、"
    "控股公司及其持股关系。\n\n"
    "规则:\n"
    "- 识别所有重要股东（5% 以上实益所有人）。\n"
    "- 提取持股比例和股份类别。\n"
    "- 映射母子公司和控股公司结构。\n"
    "- 注意双重股权结构和投票权差异。\n"
    "- 捕捉锁定期和 IPO 后限制条款。"
)

_NODE_PROMPT = (
    "你是公司治理分析师。提取所有股权实体（节点）。\n\n"
    "提取规则:\n"
    "- 识别个人、机构投资者、控股公司和信托。\n"
    "- 识别发行公司本身。\n"
    "- 按类型对每个实体进行分类。\n"
    "- 此阶段不提取持股关系。"
)

_EDGE_PROMPT = (
    "你是公司治理分析师。在获得实体清单的基础上，提取持股和控制关系（边）。\n\n"
    "提取规则:\n"
    "- 将持有方连接到其持有的资产。\n"
    "- 提取持股比例和股份类别。\n"
    "- 注意投票权差异。\n"
    "- 捕捉锁定期。\n"
    "- 仅在提供的列表中存在的节点之间创建边。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class ShareholderStructure(AutoGraph[OwnershipEntity, OwnershipEdge]):
    """
    适用文档: S-1 招股说明书、委托声明书（DEF 14A）、Schedule 13D/G 申报文件、
    年度报告（实益所有权部分）、IPO 申报文件。

    模板用于提取和映射公司股权结构。支持最终控制人分析、投票权评估和
    IPO 后锁定期跟踪。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> ownership = ShareholderStructure(llm_client=llm, embedder=embedder)
        >>> prospectus = "下表列示实益所有权情况：CEO 持有 15.3%..."
        >>> ownership.feed_text(prospectus)
        >>> ownership.show()
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
        初始化股东结构图谱模板。

        Args:
            llm_client (BaseChatModel): 用于股权提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=OwnershipEntity,
            edge_schema=OwnershipEdge,
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
        使用 OntoSight 可视化股东结构图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的关系数。默认 3。
        """

        def node_label_extractor(node: OwnershipEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: OwnershipEdge) -> str:
            pct = f" {edge.ownership_percentage}" if edge.ownership_percentage else ""
            return f"{edge.relationship_type}{pct}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
