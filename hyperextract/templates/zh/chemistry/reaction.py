from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.hypergraphs.base import AutoHypergraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class ChemicalEntity(BaseModel):
    """
    一种化学物质（试剂、产物、催化剂、溶剂）。
    """
    name: str = Field(description="IUPAC 名称或常用名称（如：'硫酸'）。")
    formula: Optional[str] = Field(None, description="化学式（如：'H2SO4'）。")
    cas_number: Optional[str] = Field(None, description="CAS 登记号。")
    phase: str = Field("Unknown", description="物理状态：'气态'、'液态'、'固态'、'水溶液'。")

class ReactionEvent(BaseModel):
    """
    涉及多种试剂、特定条件和所得产物的化学反应。
    """
    reaction_id: str = Field(description="反应的名称或简短描述（如：'哈伯制氨法'）。")
    reactants: List[str] = Field(description="起始化学实体名称列表。")
    products: List[str] = Field(description="所得化学实体名称列表。")
    catalysts: List[str] = Field(default_factory=list, description="促进反应的物质名称。")
    solvents: List[str] = Field(default_factory=list, description="反应发生的介质。")
    temperature: Optional[str] = Field(None, description="操作温度（如：'250°C'）。")
    pressure: Optional[str] = Field(None, description="操作压力（如：'200 atm'）。")
    yield_info: Optional[str] = Field(None, description="获得的产率/产量。")

# ==============================================================================
# 2. Prompts
# ==============================================================================

REACTION_CONSOLIDATED_PROMPT = (
    "你是一位专业的有机和无机化学家。请提取多组分的反应事件。\n\n"
    "规则：\n"
    "- 将每个反应表示为一个超边（Hyperedge），连接所有反应物、产物和催化剂。\n"
    "- 捕获详细的反应条件，如温度、压力和特定溶剂。\n"
    "- 在反应语境中正确识别每个化学实体的角色。"
)

REACTION_NODE_PROMPT = (
    "识别提及的所有化学实体。查找 IUPAC 名称、化学式和 CAS 号。"
)

REACTION_EDGE_PROMPT = (
    "映射涉及这些化学物质的反应。将所有参与者归入单个反应超边中。确保清晰地区分反应物和产物。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class ChemicalReactionHyper(AutoHypergraph[ChemicalEntity, ReactionEvent]):
    """
    用于复杂化学合成、工业流程和反应路径的超图模板。
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
            node_schema=ChemicalEntity,
            edge_schema=ReactionEvent,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: x.reaction_id.strip(),
            nodes_in_edge_extractor=lambda x: tuple(set(x.reactants + x.products + x.catalysts + x.solvents)),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=REACTION_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=REACTION_NODE_PROMPT,
            prompt_for_edge_extraction=REACTION_EDGE_PROMPT,
            **kwargs
        )
