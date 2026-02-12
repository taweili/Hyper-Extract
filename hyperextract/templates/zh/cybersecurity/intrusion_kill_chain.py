from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class AttackStageNode(BaseModel):
    """
    网络攻击中的特定阶段或行动（符合 MITRE ATT&CK 或 Lockheed Kill Chain）。
    """

    stage_name: str = Field(
        description="攻击阶段名称（例如：'初始访问'、'权限维持'、'横向移动'）。"
    )
    tactics_used: List[str] = Field(
        default_factory=list,
        description="所使用的具体技术或战术（例如：'鱼叉式网络钓鱼'、'哈希传递'）。",
    )
    adversary_tools: List[str] = Field(
        default_factory=list,
        description="该阶段使用的恶意软件或工具（例如：'Cobalt Strike'、'Mimikatz'）。",
    )
    timestamp: Optional[str] = Field(None, description="行动的时间点或顺序标记。")


class KillChainLink(BaseModel):
    """
    表示攻击从一个阶段向另一个阶段演进的有向链接。
    """

    source: str = Field(description="前置攻击阶段。")
    target: str = Field(description="后续攻击阶段。")
    causality: str = Field(
        "演进",
        description="类型：'演进' (标准)、'触发' (自动执行)、'跳转' (基础设施切换)。",
    )
    observables: List[str] = Field(
        default_factory=list, description="连接各阶段的入侵指标 (IOCs，如IP、Hash)。"
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

CYBER_KILL_CHAIN_CONSOLIDATED_PROMPT = (
    "你是一位数字取证专家和事件响应人员。请从事件报告中重建攻击时间线和杀伤链。\n\n"
    "提取规则：\n"
    "- 识别不同的攻击阶段作为节点。\n"
    "- 映射攻击在时间上和逻辑上的演进过程（边）。\n"
    "- 捕获每个阶段的具体战术、工具 (TTPs) 和时间戳。\n"
    "- 重点关注攻击者是如何移动以及在何时移动的。"
)

CYBER_KILL_CHAIN_NODE_PROMPT = (
    "识别所有可疑活动和网络入侵的不同阶段。\n\n"
    "提取规则：\n"
    "- 提取以行动为导向的阶段（例如：'投放载荷'、'建立C2'）。\n"
    "- 识别与每个发现相关的工具和技术。\n"
    "- 在此阶段不要建立各阶段之间的连接。"
)

CYBER_KILL_CHAIN_EDGE_PROMPT = (
    "建立已识别攻击阶段之间的顺序和演进关系。\n\n"
    "提取规则：\n"
    "- 定义哪个阶段导致或促成了下一个阶段。\n"
    "- 识别连接这些阶段的入侵指标（IP、哈希等）。\n"
    "- 仅在已识别的列表阶段之间创建连接。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class IntrusionKillChainGraph(AutoGraph[AttackStageNode, KillChainLink]):
    """
    用于重建网络攻击生命周期的模板。
    
    适用于事件响应 (IR)、取证报告和威胁狩猎。

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> kill_chain = IntrusionKillChainGraph(llm_client=llm, embedder=embedder)
        >>> kill_chain.feed_text("攻击者通过鱼叉式网络钓鱼邮件获得了初始访问。")
        >>> print(kill_chain.nodes)  # 获取攻击阶段
        >>> print(kill_chain.edges)  # 获取演进链接
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
        初始化入侵杀伤链图谱模板。

        Args:
            llm_client (BaseChatModel): 用于杀伤链提取的大模型客户端。
            embedder (Embeddings): 用于阶段去重的嵌入模型。
            extraction_mode (str, optional): 'one_stage' 为联合提取，
                'two_stage' 为分步提取。默认为 "one_stage"。
            chunk_size (int, optional): 单个文本块的最大字符数。默认为 2048。
            chunk_overlap (int, optional): 文本块之间的重叠字符数。默认为 256。
            max_workers (int, optional): 并行处理的工作线程数。默认为 10。
            verbose (bool, optional): 是否启用详细日记记录。默认为 False。
            **kwargs (Any): 传递给 AutoGraph 基类的其他参数。
        """
        super().__init__(
            node_schema=AttackStageNode,
            edge_schema=KillChainLink,
            node_key_extractor=lambda x: x.stage_name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}->{x.target.strip().lower()}"
            ),
            nodes_in_edge_extractor=lambda x: (
                x.source.strip().lower(),
                x.target.strip().lower(),
            ),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CYBER_KILL_CHAIN_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=CYBER_KILL_CHAIN_NODE_PROMPT,
            prompt_for_edge_extraction=CYBER_KILL_CHAIN_EDGE_PROMPT,
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
        def node_label_extractor(node: AttackStageNode) -> str:
            return f"{node.stage_name}"
    
        def edge_label_extractor(edge: KillChainLink) -> str:
            return f"{edge.causality}"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
