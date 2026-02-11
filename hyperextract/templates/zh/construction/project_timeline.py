from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class MilestoneTaskNode(BaseModel):
    """
    建筑项目进度计划中的特定任务、里程碑或阶段。
    """
    task_name: str = Field(description="任务操作名称（例如：'基础浇筑'）。")
    phase: str = Field(description="项目阶段：'前期准备'、'下部结构'、'主体结构'、'装修装饰'、'竣工验收'。")
    duration_estimate: Optional[str] = Field(None, description="预估时间（例如：'14天'、'2个月'）。")
    responsible_party: Optional[str] = Field(None, description="负责的分包商或团队负责人。")

class TemporalDependency(BaseModel):
    """
    表示任务权序的基于时间的连接。
    """
    source: str = Field(description="前置任务。")
    target: str = Field(description="后置任务。")
    timestamp: str = Field(
        description="时间标记或步骤编号（例如：'阶段1'、'步骤2'或具体日期/时间）。"
    )
    dependency_type: str = Field(
        "完成到开始",
        description="类型：'完成到开始 (FS)'、'开始到开始 (SS)'、'完成到完成 (FF)'、'开始到完成 (SF)'。"
    )
    lag_time: Optional[str] = Field(None, description="任务间的等待时间（例如：'混凝土养护3天'）。")

# ==============================================================================
# 2. Prompts
# ==============================================================================

CONSTRUCTION_TEMPORAL_CONSOLIDATED_PROMPT = (
    "你是一位资深项目管理计划员和计划工程师。请从文本中提取建筑项目的时间进度表。\n\n"
    "提取规则：\n"
    "- 识别细化的任务和重大里程碑作为节点。\n"
    "- 使用行业标准逻辑（FS, SS等）建立清晰的时间依赖关系（边）。\n"
    "- 捕获提到的持续时间和养护/滞后时间。\n"
    "- 重点关注关键路径和测序逻辑。"
)

CONSTRUCTION_TEMPORAL_NODE_PROMPT = (
    "识别所有任务、计划活动和项目里程碑。\n\n"
    "提取规则：\n"
    "- 提取以动词开头的任务名称。\n"
    "- 将任务归类到项目阶段并识别负责方。\n"
    "- 在此阶段不要识别顺序或依赖关系。"
)

CONSTRUCTION_TEMPORAL_EDGE_PROMPT = (
    "根据任务在时间上的逻辑顺序进行连接。\n\n"
    "提取规则：\n"
    "- 为每个链接定义前导任务和后续任务。\n"
    "- 分类链接类型（如果未指定，默认为FS）。\n"
    "- 识别任何要求的滞后时间（例如：等待检验或干燥）。\n"
    "- 仅在已识别的列表任务之间创建连接。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class ProjectSchedulingTimeline(AutoTemporalGraph[MilestoneTaskNode, TemporalDependency]):
    """
    用于提取项目计划和关键路径法（CPM）网络的模板。
    
    适用于进度风险分析、延期跟踪和进度监控。

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> timeline = ProjectSchedulingTimeline(llm_client=llm, embedder=embedder)
        >>> timeline.feed_text("土方开挖必须在浇筑基础底板之前完成。")
        >>> print(timeline.nodes)  # 获取任务和里程碑
        >>> print(timeline.edges)  # 获取时间依赖关系
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
        初始化项目进度时间轴模板。

        Args:
            llm_client (BaseChatModel): 用于进度提取的大模型客户端。
            embedder (Embeddings): 用于任务和依赖项去重的嵌入模型。
            extraction_mode (str, optional): 'one_stage' 为联合提取，
                'two_stage' 为分步提取。默认为 "one_stage"。
            chunk_size (int, optional): 单个文本块的最大字符数。默认为 2048。
            chunk_overlap (int, optional): 文本块之间的重叠字符数。默认为 256。
            max_workers (int, optional): 并行处理的工作线程数。默认为 10。
            verbose (bool, optional): 是否启用详细日记记录。默认为 False。
            **kwargs (Any): 传递给 AutoTemporalGraph 基类的其他参数。
        """
        super().__init__(
            node_schema=MilestoneTaskNode,
            edge_schema=TemporalDependency,
            node_key_extractor=lambda x: x.task_name.strip().lower(),
            edge_key_extractor=lambda x: f"{x.source.strip().lower()}--[{x.dependency_type}]-->{x.target.strip().lower()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip().lower(), x.target.strip().lower()),
            time_in_edge_extractor=lambda x: x.timestamp.strip(),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CONSTRUCTION_TEMPORAL_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=CONSTRUCTION_TEMPORAL_NODE_PROMPT,
            prompt_for_edge_extraction=CONSTRUCTION_TEMPORAL_EDGE_PROMPT,
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
        def node_label_extractor(node: MilestoneTaskNode) -> str:
            info = f" ({ node.phase })" if getattr(node, "phase", None) else ""
            return f"{ node.task_name }{info}"
    
        def edge_label_extractor(edge: TemporalDependency) -> str:
            info = f" ({ edge.timestamp })" if getattr(edge, "timestamp", None) else ""
            return f"{ edge.source }{info}"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )