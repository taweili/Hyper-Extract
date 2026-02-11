from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class TaxonNode(BaseModel):
    """
    表示生命之树中的生物分类单元。
    """
    name: str = Field(description="生物体或群体的学名（拉丁语）或标准俗名。")
    rank: str = Field(description="分类等级：'域'、'界'、'门'、'纲'、'目'、'科'、'属'、'种'。")
    common_name: Optional[str] = Field(None, description="在非科学背景下使用的通用名称。")
    description: Optional[str] = Field(None, description="简要的生物特征、栖息地或区别性性状。")

class TaxonomyRelation(BaseModel):
    """
    两个分类单元之间直接的层级关系。
    """
    source: str = Field(description="父级分类单元（如：'哺乳纲'）。")
    target: str = Field(description="子级分类单元（如：'灵长目'）。")
    type: str = Field("parent_of", description="关系类型：'parent_of'（父级）、'subspecies_of'（亚种）、'classified_under'（归类于）。")
    evidence: Optional[str] = Field(None, description="证明该分类合理的表型或基因组数据引用。")

# ==============================================================================
# 2. Prompts
# ==============================================================================

TAXONOMY_CONSOLIDATED_PROMPT = (
    "你是一位专业的分类学家和系统生物学家。请从文本中提取生物层级（分类学）信息。\n\n"
    "规则：\n"
    "- 识别所有分类阶元（从界到种）及其特定的等级。\n"
    "- 使用 'parent_of' 关系构建严格的树状层级。\n"
    "- 捕捉可用的学名和常用名。"
)

TAXONOMY_NODE_PROMPT = (
    "你是一位专业的分类学家。你的任务是从文本中识别并提取所有生物分类单元（节点）。\n\n"
    "提取规则：\n"
    "- 为每个分类单元识别其学名和指定的等级（如：域、界、门、纲、目、科、属、种）。\n"
    "- 捕捉通用名称和简要描述（如果提供）。\n"
    "- 仅专注于正式的生物分类。\n"
    "- 在此阶段请勿提取分类单元之间的关系。"
)

TAXONOMY_EDGE_PROMPT = (
    "你是一位专业的分类学家。根据以下已识别分类单元的清单，提取文本中描述的层级关系（边）。\n\n"
    "提取规则：\n"
    "- 在高层级分类单元包含低层级分类单元时建立 'parent_of' 链接。\n"
    "- 确保谱系准确反映文本中描述的系统发育或系统分类树。\n"
    "- 仅连接已提供的分类单元清单中存在的节点。\n"
    "- 使用提及的任何证据或基因组背景来补充关系。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class TaxonomyGraph(AutoGraph[TaxonNode, TaxonomyRelation]):
    """
    生物分类和系统发育层级的高精度提取模板。
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
            node_schema=TaxonNode,
            edge_schema=TaxonomyRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.type})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=TAXONOMY_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=TAXONOMY_NODE_PROMPT,
            prompt_for_edge_extraction=TAXONOMY_EDGE_PROMPT,
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
        def node_label_extractor(node: TaxonNode) -> str:
            info = f" ({ node.description })" if getattr(node, "description", None) else ""
            return f"{ node.name }{info}"
    
        def edge_label_extractor(edge: TaxonomyRelation) -> str:
            info = f" ({ edge.type })" if getattr(edge, "type", None) else ""
            return f"{ edge.source }{info}"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
