from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. 模式定义 (Schema)
# ==============================================================================

class MaintenanceItem(BaseModel):
    """保养项目或车辆零部件（机油、刹车片、正时皮带）。"""
    item_name: str = Field(description="零部件名称或保养服务名称。")
    category: str = Field(description="类别：'油液'、'易损件'、'检查项'、'软件更新'。")
    interval: Optional[str] = Field(description="建议的里程或时间间隔（如：5,000公里）。")

class MaintenanceSequence(BaseModel):
    """保养行动的依赖或序列关系。"""
    source: str = Field(description="触发保养的部件或初始状态。")
    target: str = Field(description="保养任务或更换的零部件。")
    action: str = Field(description="动作：'更换'、'检查'、'清洗'、'校准'。")
    precaution: Optional[str] = Field(description="安全警告或所需工具。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

MAINTENANCE_GRAPH_PROMPT = (
    "你是一位资深技师和售后顾问。请提取车辆保养与维修图谱。\n\n"
    "准则：\n"
    "- 识别手册或日志中提到的具体保养项目和零部件。\n"
    "- 映射触发保养的条件（如：里程、报警灯、视觉检查结果）。\n"
    "- 将零部件连接到对应的系统及所需的维保动作。"
)

MAINTENANCE_NODE_PROMPT = (
    "提取保养任务、零部件和油液类型。如果指定了建议间隔，请一并记录。"
)

MAINTENANCE_EDGE_PROMPT = (
    "将触发条件与动作联系起来。展示哪些部件需要更换或检查。记录每项任务的具体注意事项。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class CarMaintenanceGraph(AutoGraph[MaintenanceItem, MaintenanceSequence]):
    """
    汽车保养图谱模板，用于处理车辆服务手册、维修指南和保养日志。
    
    有助于整理维保计划和零部件兼容性信息。
    
    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI()
        >>> embedder = OpenAIEmbeddings()
        >>> graph = CarMaintenanceGraph(llm_client=llm, embedder=embedder)
        >>> text = "每10,000公里更换发动机机油和机滤，使用 0W-20 全合成机油。"
        >>> graph.feed_text(text)
        >>> print(graph.nodes) # 保养项目详情
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
        **kwargs: Any
    ):
        """
        初始化汽车保养图谱模板。

        Args:
            llm_client: 语言模型客户端。
            embedder: 嵌入模型。
            extraction_mode: 提取模式，"one_stage" 或 "two_stage"。
            chunk_size: 分块大小。
            chunk_overlap: 分块重叠大小。
            max_workers: 最大并行工作线程数。
            verbose: 是否开启详细日志。
            **kwargs: 传递给 AutoGraph 的额外参数。
        """
        super().__init__(
            node_schema=MaintenanceItem,
            edge_schema=MaintenanceSequence,
            node_key_extractor=lambda x: x.item_name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.action.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=MAINTENANCE_GRAPH_PROMPT,
            prompt_for_node_extraction=MAINTENANCE_NODE_PROMPT,
            prompt_for_edge_extraction=MAINTENANCE_EDGE_PROMPT,
            **kwargs
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
        def node_label_extractor(node: MaintenanceItem) -> str:
            info = f" ({ node.category })" if getattr(node, "category", None) else ""
            return f"{ node.item_name }{info}"
    
        def edge_label_extractor(edge: MaintenanceSequence) -> str:
            return f"{ edge.action }"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
