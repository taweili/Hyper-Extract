from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSpatialGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class AtomNode(BaseModel):
    """
    化学结构中的单个原子。
    """
    name: str = Field(description="原子标识符（如：'C1'、'O2'）或元素符号。")
    element: str = Field(description="化学元素（如：'碳'、'H'）。")
    hybridization: Optional[str] = Field(None, description="电子状态：'sp3'、'sp2'、'sp'。")
    formal_charge: int = Field(0, description="分配给原子的形式电荷。")

class ChemicalBond(BaseModel):
    """
    两个原子之间的化学键，包括空间/位置元数据。
    """
    source: str = Field(description="起始原子（如：'C1'）。")
    target: str = Field(description="连接原子（如：'C2'）。")
    bond_type: str = Field(description="类型：'单键'、'双键'、'三键'、'芳香键'、'氢键'。")
    spatial_position: str = Field(description="在分子中的物理或逻辑位置（如：'C4位'、'轴向'、'赤道向'）。")
    bond_length: Optional[float] = Field(None, description="原子间的距离（单位：埃）。")

# ==============================================================================
# 2. Prompts
# ==============================================================================

MOLECULAR_CONSOLIDATED_PROMPT = (
    "你是一位计算化学家和晶体学家。请提取 3D 分子拓扑结构。\n\n"
    "规则：\n"
    "- 将每个原子识别为一个节点。\n"
    "- 定义化学键，包括它们的特定空间取向（例如：'Alpha'、'Beta'、'顺式'、'反式'）。\n"
    "- 捕获每个原子的形式电荷和杂化轨道。"
)

MOLECULAR_NODE_PROMPT = (
    "你是一位计算化学家。你的任务是从分子结构中识别并提取所有单个原子（节点）。\n\n"
    "提取规则：\n"
    "- 识别唯一的原子标识符（如：C1）及其化学元素符号。\n"
    "- 捕捉每个原子的电子杂化状态（sp, sp2, sp3）和形式电荷。\n"
    "- 专注于保持源文本中出现的准确命名方式。\n"
    "- 在此阶段请勿识别化学键或空间连接性。"
)

MOLECULAR_EDGE_PROMPT = (
    "你是一位计算化学家。根据原子清单，映射化学键和空间连接性（边）。\n\n"
    "提取规则：\n"
    "- 定义源原子与目标原子之间的化学键类型（单键、双键、芳香键等）。\n"
    "- 精确识别空间位置或立体化学取向（如：轴向、赤道向、顺式、反式）。\n"
    "- 仅在提供的原子清单中存在的原子之间建立化学键。\n"
    "- 如果提供了数值数据，请捕捉键长。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class MolecularStructureGraph(AutoSpatialGraph[AtomNode, ChemicalBond]):
    """
    用于高分辨率分子建模和结构生物学的空间图模板。
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
        super().__init__(
            node_schema=AtomNode,
            edge_schema=ChemicalBond,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.bond_type})-->{x.target.strip()}",
            location_in_edge_extractor=lambda x: x.spatial_position.strip(),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=MOLECULAR_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=MOLECULAR_NODE_PROMPT,
            prompt_for_edge_extraction=MOLECULAR_EDGE_PROMPT,
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
        def node_label_extractor(node: AtomNode) -> str:
            return f"{node.name}"
    
        def edge_label_extractor(edge: ChemicalBond) -> str:
            return f"{edge.bond_type}"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
