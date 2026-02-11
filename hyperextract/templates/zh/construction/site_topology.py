from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSpatialGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class PhysicalElementNode(BaseModel):
    """
    建筑工地内的特定物理构件或区域。
    """
    name: str = Field(description="元素的唯一标识符或名称（例如：'A1柱'、'B区'）。")
    element_type: str = Field(description="类型：'结构件'、'机电构件'、'建筑构件'、'临时设施'、'安全区域'。")
    location_coordinates: Optional[str] = Field(None, description="空间坐标或相对轴线位置（例如：'X:10, Y:20, Z:5'）。")
    material_properties: Optional[str] = Field(None, description="关键材料信息（例如：'C30混凝土'、'S355钢材'）。")

class SpatialRelation(BaseModel):
    """
    两个物理元素之间的空间或拓扑连接关系。
    """
    source: str = Field(description="参考元素。")
    target: str = Field(description="关联元素。")
    location_marker: str = Field(
        description="该关系所在的物理位置或区域（例如：'3层'、'北翼'、'A-1轴线'）。"
    )
    relation_type: str = Field(
        description="类型：'支撑'、'相邻'、'包含于'、'相交'、'对齐'。"
    )
    offset_distance: Optional[float] = Field(None, description="元素间的物理距离（单位：米）。")

# ==============================================================================
# 2. Prompts
# ==============================================================================

CONSTRUCTION_SPATIAL_CONSOLIDATED_PROMPT = (
    "你是一位资深BIM（建筑信息模型）工程师。请从文本中提取建筑项目的空间拓扑结构。\n\n"
    "提取规则：\n"
    "- 识别固定的物理构件及其属性作为节点。\n"
    "- 映射这些构件之间的结构和空间关系（边）。\n"
    "- 如果文本提到了坐标和距离，请务必捕获。\n"
    "- 重点关注物体是如何物理连接或相对定位的。"
)

CONSTRUCTION_SPATIAL_NODE_PROMPT = (
    "识别所有物理建筑构件和工地区域。\n\n"
    "提取规则：\n"
    "- 提取明确的结构、机械或建筑构件。\n"
    "- 捕获任何提到的位置、楼层或材料信息。\n"
    "- 在此阶段不要识别连接关系。"
)

CONSTRUCTION_SPATIAL_EDGE_PROMPT = (
    "映射已识别建筑构件之间的空间和结构关系。\n\n"
    "提取规则：\n"
    "- 确定元素A与元素B的关系（例如：A支撑B，A与B相邻）。\n"
    "- 提取提供的物理偏移或距离。\n"
    "- 仅在已识别的列表元素之间创建连接。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class SiteTopologyGraph(AutoSpatialGraph[PhysicalElementNode, SpatialRelation]):
    """
    用于构建建筑工地空间数字孪生的模板。
    
    适用于结构分析、BIM转图谱以及工地物流规划。

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> graph = SiteTopologyGraph(llm_client=llm, embedder=embedder)
        >>> graph.feed_text("基础底板支撑着四个主要的转角柱。")
        >>> print(graph.nodes)  # 获取结构构件
        >>> print(graph.edges)  # 获取空间关系
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
        初始化工地拓扑图谱模板。

        Args:
            llm_client (BaseChatModel): 用于拓扑提取的大模型客户端。
            embedder (Embeddings): 用于元素去重的嵌入模型。
            extraction_mode (str, optional): 'one_stage' 为联合提取，
                'two_stage' 为分步提取。默认为 "one_stage"。
            chunk_size (int, optional): 单个文本块的最大字符数。默认为 2048。
            chunk_overlap (int, optional): 文本块之间的重叠字符数。默认为 256。
            max_workers (int, optional): 并行处理的工作线程数。默认为 10。
            verbose (bool, optional): 是否启用详细日记记录。默认为 False。
            **kwargs (Any): 传递给 AutoSpatialGraph 基类的其他参数。
        """
        super().__init__(
            node_schema=PhysicalElementNode,
            edge_schema=SpatialRelation,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: f"{x.source.strip().lower()}--{x.relation_type.lower()}--{x.target.strip().lower()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip().lower(), x.target.strip().lower()),
            location_in_edge_extractor=lambda x: x.location_marker.strip(),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CONSTRUCTION_SPATIAL_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=CONSTRUCTION_SPATIAL_NODE_PROMPT,
            prompt_for_edge_extraction=CONSTRUCTION_SPATIAL_EDGE_PROMPT,
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
        def node_label_extractor(node: PhysicalElementNode) -> str:
            return f"{ node.name }"
    
        def edge_label_extractor(edge: SpatialRelation) -> str:
            return f"{ edge.source }"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )