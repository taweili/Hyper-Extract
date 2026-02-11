from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. 模式定义 (Schema)
# ==============================================================================

class ArtEntity(BaseModel):
    """艺术领域实体（如：作品、艺术家、博物馆、私人收藏家、拍卖行）。"""
    name: str = Field(description="艺术品名称、人物姓名或机构名称。")
    category: str = Field(
        description="类别：'艺术品'、'艺术家'、'收藏家'、'机构'、'地理位置'。"
    )
    description: Optional[str] = Field(description="材质、创作日期或历史地位描述。")

class ProvenanceEdge(BaseModel):
    """艺术品的所有权或流转记录。"""
    source: str = Field(description="原持有者或起始地点。")
    target: str = Field(description="新持有者或目的地。")
    transfer_type: str = Field(
        description="流转类型：'收购自'、'出售给'、'捐赠予'、'借展给'、'委托'。"
    )
    specification: Optional[str] = Field(description="流转日期、成交价格或拍卖详情。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

PROVENANCE_GRAPH_PROMPT = (
    "你是一位资深的艺术史学家和流传考证专家。请提取艺术品的流传历程图谱。\n\n"
    "准则：\n"
    "- 识别核心艺术品及其所有历史持有者（私人收藏家、博物馆、王室）。\n"
    "- 按照时间顺序映射所有权转移（出售、继承、掠夺、捐赠）。\n"
    "- 捕捉提到的具体日期、成交价格及传承细节。"
)

PROVENANCE_NODE_PROMPT = (
    "提取艺术实体：识别作品、艺术家、收藏家、博物馆和拍卖行。标注作品的材质及相关人物/机构的角色。"
)

PROVENANCE_EDGE_PROMPT = (
    "构建传承链条。将前任所有者与现任所有者联系起来，标注流转类型（如'捐赠予'）。包含流转的时间段和交易详情。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class ProvenanceGraph(AutoGraph[ArtEntity, ProvenanceEdge]):
    """
    艺术品流传图谱模板，用于追踪艺术品和文物的历史所有权。
    
    适用于艺术品鉴定、馆藏档案管理和历史研究。
    
    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> graph = ProvenanceGraph(llm_client=llm, embedder=embedder)
        >>> text = "该画作于1815年由卢浮宫从博尔盖塞收藏中购得。"
        >>> graph.feed_text(text)
        >>> print(graph.edges) # 提取的作品所有权转移记录
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
        初始化艺术品流传图谱模板。

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
            node_schema=ArtEntity,
            edge_schema=ProvenanceEdge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.transfer_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=PROVENANCE_GRAPH_PROMPT,
            prompt_for_node_extraction=PROVENANCE_NODE_PROMPT,
            prompt_for_edge_extraction=PROVENANCE_EDGE_PROMPT,
            **kwargs
        )
