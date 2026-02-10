from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.hypergraphs.base import AutoHypergraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class MetaboliteNode(BaseModel):
    """
    代谢反应中涉及的任何物理物质（底物或产物）。
    """
    name: str = Field(description="分子的化学名或常用名（如：'丙酮酸'）。")
    formula: Optional[str] = Field(None, description="化学式/表示法。")
    charge: Optional[int] = Field(None, description="代谢物的净电荷。")
    compartment: Optional[str] = Field(description="细胞定位：'细胞质'、'线粒体'、'细胞外'。")

class MetabolicReactionHyperedge(BaseModel):
    """
    一种多试剂生化反应，其中多个底物产生多个产物。
    """
    reaction_id: str = Field(description="唯一标识符或 EC 编号（如：'EC 1.1.1.1'）。")
    substrates: List[str] = Field(description="底物代谢物名称列表。")
    products: List[str] = Field(description="产物代谢物名称列表。")
    enzymes: List[str] = Field(default_factory=list, description="涉及的催化剂（酶）列表。")
    stoichiometry: Optional[str] = Field(None, description="如果文本中提到，则记录化学计量系数。")
    reversibility: bool = Field(True, description="反应是否可逆。")

# ==============================================================================
# 2. Prompts
# ==============================================================================

METABOLIC_CONSOLIDATED_PROMPT = (
    "你是一位擅长代谢工程的生物化学家。请提取复杂的 N 元反应。\n\n"
    "规则：\n"
    "- 将所有参与者（底物、产物和酶）归为一个超边（Hyperedge）。\n"
    "- 区分反应物（底物）和结果（产物）。\n"
    "- 将催化酶作为超边参与者的一部分进行捕获。"
)

METABOLIC_NODE_PROMPT = (
    "识别所有化学物质（代谢物）和酶。专注于精确的命名。"
)

METABOLIC_EDGE_PROMPT = (
    "定义代表代谢反应的超边。包含每个识别出的反应事件中所有的代谢物和酶参与者。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class MetabolicHypergraph(AutoHypergraph[MetaboliteNode, MetabolicReactionHyperedge]):
    """
    用于涉及多底物/多产物反应的代谢途径的复杂超图模板。
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
            node_schema=MetaboliteNode,
            edge_schema=MetabolicReactionHyperedge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: x.reaction_id.strip(),
            nodes_in_edge_extractor=lambda x: tuple(set(x.substrates + x.products + x.enzymes)),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=METABOLIC_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=METABOLIC_NODE_PROMPT,
            prompt_for_edge_extraction=METABOLIC_EDGE_PROMPT,
            **kwargs
        )
