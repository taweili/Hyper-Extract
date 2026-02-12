from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph

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

_PROMPT = (
    "你是一位擅长代谢工程的生物化学家。请提取复杂的 N 元反应。\n\n"
    "规则：\n"
    "- 将所有参与者（底物、产物和酶）归为一个超边（Hyperedge）。\n"
    "- 区分反应物（底物）和结果（产物）。\n"
    "- 将催化酶作为超边参与者的一部分进行捕获。"
)

_NODE_PROMPT = (
    "你是一位生物化学家。你的任务是识别代谢过程中涉及的所有代谢物和催化酶（节点）。\n\n"
    "提取规则：\n"
    "- 识别化学组分（底物/产物）以及促进其转化的酶。\n"
    "- 如果有描述，请捕捉其化学式、电荷和细胞定位。\n"
    "- 确保名称是标准化的（如：'6-磷酸葡萄糖'）。\n"
    "- 在此阶段请勿构建反应方程式或复合物。"
)

_EDGE_PROMPT = (
    "你是一位生物化学家。根据以下代谢物和酶的清单，提取复杂的代谢反应（超边）。\n\n"
    "提取规则：\n"
    "- 将所有参与者（底物、产物和酶）归入单个反应事件中。\n"
    "- 在反应元数据中清晰区分底物（输入）和产物（输出）。\n"
    "- 仅包含已提供的实体清单中存在的参与者。\n"
    "- 如果有具体数据，记录其化学计量和可逆性。"
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
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
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
        def node_label_extractor(node: MetaboliteNode) -> str:
            return f"{node.name}"
    
        def edge_label_extractor(edge: MetabolicReactionHyperedge) -> str:
            return f"{edge.reaction_id}"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
