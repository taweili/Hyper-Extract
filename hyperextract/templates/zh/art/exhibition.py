from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. 模式定义 (Schema)
# ==============================================================================

class ExhibitionEntity(BaseModel):
    """艺术展览的组成要素（策展人、主题、作品、场馆、赞助商）。"""
    name: str = Field(description="展览名称、艺术家姓名或策展人姓名。")
    type: str = Field(
        description="类型：'展览'、'主题'、'艺术品'、'策展人'、'场馆'、'合作伙伴'。"
    )
    details: Optional[str] = Field(description="展览日期、理念说明或地理位置。")

class ExhibitionRelation(BaseModel):
    """展览策划与执行中的连接关系。"""
    source: str = Field(description="组织或控制实体。")
    target: str = Field(description="相关的作品 or 参与者。")
    relation_type: str = Field(
        description="类型：'策展自'、'参展于'、'举办于'、'赞助自'、'主题关联至'。"
    )
    context: Optional[str] = Field(description="具体展厅、借展条件或主题子组。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

EXHIBITION_GRAPH_PROMPT = (
    "你是一位博物馆馆长和展览设计师。请映射艺术展览的结构图谱。\n\n"
    "准则：\n"
    "- 识别展览名称、核心主题以及参展的艺术家和作品。\n"
    "- 将作品连接到其所属的主题板块以及负责的策展人。\n"
    "- 捕捉场馆和赞助商等物流信息。"
)

EXHIBITION_NODE_PROMPT = (
    "提取展览组件：展览名称、场馆、主题、具体艺术品以及关键人员（策展人、设计师）。"
)

EXHIBITION_EDGE_PROMPT = (
    "连接展览内的各项内容。展示哪些作品属于哪个主题，并识别举办场馆和赞助商。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class ExhibitionGraph(AutoGraph[ExhibitionEntity, ExhibitionRelation]):
    """
    展览策划图谱模板，用于策划筹备和展览分析。
    
    追踪艺术品、主题、策展人和场馆之间的关系。
    
    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI()
        >>> embedder = OpenAIEmbeddings()
        >>> graph = ExhibitionGraph(llm_client=llm, embedder=embedder)
        >>> text = "'超现实之梦'展览由 Alice Smith 在泰特现代美术馆策划。"
        >>> graph.feed_text(text)
        >>> print(graph.edges) # 展览关联信息
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
        初始化展览策划图谱模板。

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
            node_schema=ExhibitionEntity,
            edge_schema=ExhibitionRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.relation_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=EXHIBITION_GRAPH_PROMPT,
            prompt_for_node_extraction=EXHIBITION_NODE_PROMPT,
            prompt_for_edge_extraction=EXHIBITION_EDGE_PROMPT,
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
        def node_label_extractor(node: ExhibitionEntity) -> str:
            info = f" ({ node.type })" if getattr(node, "type", None) else ""
            return f"{ node.name }{info}"
    
        def edge_label_extractor(edge: ExhibitionRelation) -> str:
            return f"{ edge.source }"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
