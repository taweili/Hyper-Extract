from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class BioEntityNode(BaseModel):
    """
    代表基因、蛋白质或小分子的基础生物单位。
    """
    name: str = Field(description="标准化符号或名称（如：'BRCA1'、'cAMP'）。")
    category: str = Field(description="实体类型：'基因'、'蛋白质'、'RNA'、'代谢物'、'酶'、'转录因子'。")
    synonyms: Optional[str] = Field(None, description="替代名称或数据库 ID（如：UniProt、Entrez）。")
    biological_function: Optional[str] = Field(None, description="主要分子功能或细胞定位。")

class BioInteractionEdge(BaseModel):
    """
    两个生物实体之间直接的物理或功能相互作用。
    """
    source: str = Field(description="上游或施加动作的实体。")
    target: str = Field(description="下游或接受动作的实体。")
    interaction_type: str = Field(description="类型：'磷酸化'、'抑制'、'激活'、'结合'、'调节'、'切割'。")
    mechanism: Optional[str] = Field(None, description="具体的生化机制（如：'别构抑制'）。")
    strength: Optional[str] = Field(None, description="置信度评分或结合亲和力（如果可用）。")

# ==============================================================================
# 2. Prompts
# ==============================================================================

NETWORK_CONSOLIDATED_PROMPT = (
    "你是一位擅长分子信号转导和调节网络的生物信息学专家。"
    "请从文本中提取相互作用，以构建生物网络图。\n\n"
    "规则：\n"
    "- 区分不同的分子类型（如蛋白质与基因）。\n"
    "- 识别有向相互作用（例如：酶 A 磷酸化蛋白质 B）。\n"
    "- 捕捉每条边具体的生化机制。"
)

NETWORK_NODE_PROMPT = (
    "你是一位生物信息学专家。你的任务是识别出文本中提及的所有分子实体（节点）。\n\n"
    "提取规则：\n"
    "- 识别基因、蛋白质、RNA 和代谢物。使用标准命名法（如：HGNC 符号）。\n"
    "- 捕捉可用的别名和生物学功能。\n"
    "- 排除通用的生物学词汇，除非它们作为已知分子的特定占位符。\n"
    "- 在此阶段请勿提取相互作用或状态变化。"
)

NETWORK_EDGE_PROMPT = (
    "你是一位生物信息学专家。根据以下分子实体清单，提取它们之间的物理和功能相互作用（边）。\n\n"
    "提取规则：\n"
    "- 识别相互作用的类型（磷酸化、抑制、激活、结合等）。\n"
    "- 指定方向性（源实体作用于目标实体）。\n"
    "- 仅在已提供的实体清单中的成员之间建立边。\n"
    "- 如果提及，请包含生化机制和相互作用强度。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class BiologicalNetwork(AutoGraph[BioEntityNode, BioInteractionEdge]):
    """
    用于建模分子信号、二元代谢途径和调节网络的模板。
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
            node_schema=BioEntityNode,
            edge_schema=BioInteractionEdge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.interaction_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=NETWORK_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=NETWORK_NODE_PROMPT,
            prompt_for_edge_extraction=NETWORK_EDGE_PROMPT,
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
        def node_label_extractor(node: BioEntityNode) -> str:
            info = f" ({ node.category })" if getattr(node, "category", None) else ""
            return f"{ node.name }{info}"
    
        def edge_label_extractor(edge: BioInteractionEdge) -> str:
            return f"{ edge.interaction_type }"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
