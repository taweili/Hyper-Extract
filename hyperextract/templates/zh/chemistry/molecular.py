from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.graphs.spatial_graph import AutoSpatialGraph

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
    "提取所有单个原子。记录它们的元素类型和电子杂化状态。"
)

MOLECULAR_EDGE_PROMPT = (
    "映射原子间的连接性（化学键）。特别识别分子框架内发生连接的空间位置。"
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
