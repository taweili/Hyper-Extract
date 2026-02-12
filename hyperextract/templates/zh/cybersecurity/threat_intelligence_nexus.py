from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class ThreatActorNode(BaseModel):
    """
    负责网络威胁的实体（个人、团体或国家级组织）。
    """

    actor_name: str = Field(
        description="别名或团体名称（例如：'APT28'、'Fancy Bear'、'Lazarus Group'）。"
    )
    origin_country: Optional[str] = Field(None, description="疑似地理来源。")
    motivation: Optional[str] = Field(
        None,
        description="主要驱动因素：'间谍活动'、'经济利益'、'破坏'、'黑客行动主义'。",
    )
    typical_targets: List[str] = Field(
        default_factory=list, description="通常的目标行业或地区。"
    )


class IntelligenceNexus(BaseModel):
    """
    连接攻击者、特定基础设施和战役主题的超边。
    """

    participants: List[str] = Field(
        description="涉及的实体：攻击者名称、工具名称、基础设施（IP/域名）、受害组织。"
    )
    campaign_name: str = Field(
        description="已知的行动名称（例如：'SolarWinds 供应链攻击'）。"
    )
    shared_ttp: str = Field(
        description="连接这些不同实体的共同战术、技术或过程（TTP）。"
    )
    confidence_level: str = Field("中", description="分析置信度：'高'、'中'、'低'。")


# ==============================================================================
# 2. Prompts
# ==============================================================================

CYBER_NEXUS_CONSOLIDATED_PROMPT = (
    "你是一位战略威胁情报分析师。请映射攻击者、基础设施及其战役之间的高层级关联。\n\n"
    "提取规则：\n"
    "- 识别威胁攻击者及其别名作为节点。\n"
    "- 创建超边 (Nexuses)，在命名的战役下，将攻击者与特定工具和基础设施关联起来。\n"
    "- 重点关注揭示协同行动的多点连接，而非简单的二元链接。\n"
    "- 突出显示统一该 Nexus 的共享 TTPs。"
)

CYBER_NEXUS_NODE_PROMPT = (
    "识别威胁攻击者、恶意软件家族和恶意基础设施实体。\n\n"
    "提取规则：\n"
    "- 提取攻击者别名和团体名称。\n"
    "- 识别攻击动机和目标行业。\n"
    "- 在此阶段不要建立战役关联。"
)

CYBER_NEXUS_EDGE_PROMPT = (
    "识别统一了攻击者、工具和目标的行动战役 (Campaigns) 或关联 (Nexuses)。\n\n"
    "提取规则：\n"
    "- 每个超边必须描述一个单一的战役或行动。\n"
    "- 将攻击者关联到在该行动中使用的特定基础设施和工具。\n"
    "- 仅在已识别的列表实体之间创建连接。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class ThreatIntelligenceNexusHypergraph(
    AutoHypergraph[ThreatActorNode, IntelligenceNexus]
):
    """
    用于战略威胁情报映射的模板。
    
    适用于在复杂战役中连接基础设施、攻击者和恶意软件。

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> nexus = ThreatIntelligenceNexusHypergraph(llm_client=llm, embedder=embedder)
        >>> nexus.feed_text("APT28 在 'Fancy-Phish' 行动中使用了 X-Tunnel。")
        >>> print(nexus.nodes)  # 获取威胁攻击者
        >>> print(nexus.edges)  # 获取战役超边
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
        初始化威胁情报关联超图模板。

        Args:
            llm_client (BaseChatModel): 用于关联提取的大模型客户端。
            embedder (Embeddings): 用于攻击者去重的嵌入模型。
            extraction_mode (str, optional): 'one_stage' 为联合提取，
                'two_stage' 为分步提取。默认为 "one_stage"。
            chunk_size (int, optional): 单个文本块的最大字符数。默认为 2048。
            chunk_overlap (int, optional): 文本块之间的重叠字符数。默认为 256。
            max_workers (int, optional): 并行处理的工作线程数。默认为 10。
            verbose (bool, optional): 是否启用详细日记记录。默认为 False。
            **kwargs (Any): 传递给 AutoHypergraph 基类的其他参数。
        """
        super().__init__(
            node_schema=ThreatActorNode,
            edge_schema=IntelligenceNexus,
            node_key_extractor=lambda x: x.actor_name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.campaign_name.strip().lower()}_linking_{sorted(x.participants)}"
            ),
            nodes_in_edge_extractor=lambda x: [
                p.strip().lower() for p in x.participants
            ],
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CYBER_NEXUS_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=CYBER_NEXUS_NODE_PROMPT,
            prompt_for_edge_extraction=CYBER_NEXUS_EDGE_PROMPT,
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
        def node_label_extractor(node: ThreatActorNode) -> str:
            return f"{node.actor_name}"
    
        def edge_label_extractor(edge: IntelligenceNexus) -> str:
            return f"{edge.campaign_name}"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
