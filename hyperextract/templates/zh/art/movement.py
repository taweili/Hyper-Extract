from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. 模式定义 (Schema)
# ==============================================================================

class MovementEntity(BaseModel):
    """艺术流派、风格、艺术家或具有影响力的作品。"""
    name: str = Field(description="流派名称（如：印象派）或艺术家姓名。")
    category: str = Field(
        description="类别：'流派'、'风格'、'艺术家'、'宣言'、'代表作'。"
    )
    attributes: Optional[str] = Field(description="核心特征、常用媒介或流行时期。")

class ArtInfluenceEdge(BaseModel):
    """艺术史中的影响、衍生或成员关系。"""
    source: str = Field(description="前驱流派 or 影响源。")
    target: str = Field(description="后继流派、具体作品或艺术家。")
    relation: str = Field(
        description="关系：'影响了'、'创始人'、'成员'、'是对...的反叛'、'衍生自'。"
    )
    details: Optional[str] = Field(description="具体的风格技巧传承或历史事件。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

MOVEMENT_GRAPH_PROMPT = (
    "你是一位专门研究艺术风格演变的艺术史学家。请提取艺术流派及其相互影响的图谱。\n\n"
    "准则：\n"
    "- 识别不同的艺术流派以及与之相关的艺术家。\n"
    "- 映射流派之间的演进关系（例如：后印象派对印象派的反思与继承）。\n"
    "- 捕捉宣言或作品中定义的各种核心哲学和视觉特征。"
)

MOVEMENT_NODE_PROMPT = (
    "提取艺术流派、风格、相关艺术家及关键作品。描述其视觉语言和核心理论。"
)

MOVEMENT_EDGE_PROMPT = (
    "定义流派与个人之间的联系。使用诸如'是对...的反叛'或'影响了'等关系词。记录代际之间传递的具体技法。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class ArtMovementGraph(AutoGraph[MovementEntity, ArtInfluenceEdge]):
    """
    艺术流派图谱模板，用于映射艺术风格、流派影响力和艺术家所属流派。
    
    适用于教学应用和艺术史深度分析。
    
    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI()
        >>> embedder = OpenAIEmbeddings()
        >>> graph = ArtMovementGraph(llm_client=llm, embedder=embedder)
        >>> text = "以莫奈为首的印象派，后来受到了后印象派结构化方法的挑战。"
        >>> graph.feed_text(text)
        >>> print(graph.nodes) # 流派与艺术家详情
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
        初始化艺术流派图谱模板。

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
            node_schema=MovementEntity,
            edge_schema=ArtInfluenceEdge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.relation.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=MOVEMENT_GRAPH_PROMPT,
            prompt_for_node_extraction=MOVEMENT_NODE_PROMPT,
            prompt_for_edge_extraction=MOVEMENT_EDGE_PROMPT,
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
        def node_label_extractor(node: MovementEntity) -> str:
            info = f" ({ node.category })" if getattr(node, "category", None) else ""
            return f"{ node.name }{info}"
    
        def edge_label_extractor(edge: ArtInfluenceEdge) -> str:
            return f"{ edge.source }"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
