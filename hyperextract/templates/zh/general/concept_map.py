from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================

class Concept(BaseModel):
    """一个代表术语、想法或理论的概念节点。"""
    term: str = Field(description="技术术语或概念的名称。")
    definition: str = Field(description="该概念的正式定义或解释。")
    examples: Optional[List[str]] = Field(default_factory=list, description="说明该概念的示例。")
    attributes: Optional[List[str]] = Field(default_factory=list, description="该概念的关键特征或属性。")

class ConceptRelation(BaseModel):
    """两个概念之间的语义关系。"""
    source: str = Field(description="源概念。")
    target: str = Field(description="目标概念。")
    relation_type: str = Field(
        description="关系类型（例如：是一种 (is-a), 属于 (part-of), 相关于, 用于, 为...的实例）。"
    )

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

CONCEPT_MAP_PROMPT = (
    "你是一位语义建模专家。请从文本中提取概念图（Concept Map），重点关注术语定义及其层级或关联关系。\n\n"
    "提取指南：\n"
    "- 识别核心术语，并基于文本提供精确定义。\n"
    "- 使用标准的语义关系词，如“是一种”（继承关系）或“属于”（组成关系）。\n"
    "- 如果文本提到了说明性的示例，请一并捕获。"
)

CONCEPT_MAP_NODE_PROMPT = (
    "请从文本中提取所有基础概念和技术术语。对于每个概念，提供其术语名称、精确定义、关键属性列表，"
    "以及文本中提到的任何具体示例。"
)

CONCEPT_MAP_EDGE_PROMPT = (
    "在提供的概念之间建立语义关系。重点关注层级分类（是一种、属于）以及功能性关联（用于、为...的实例）。"
    "确保边逻辑上连接了已定义的各个概念。"
)

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================

class ConceptMap(AutoGraph[Concept, ConceptRelation]):
    """
    用于构建概念图和分类体系的模板。
    
    适用于结构化学习、技术文档和术语表提取。侧重于定义、语义类别和层级关系。
    
    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # 初始化模板
        >>> cm = ConceptMap(llm_client=llm, embedder=embedder)
        >>> # 从文本中提取分类体系
        >>> text = "机器学习是人工智能的一个子集，它利用数据进行学习。"
        >>> cm.feed_text(text)
        >>> print(cm.edges)  # 输出显示：机器学习 --(是一种)--> 人工智能
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
        初始化 ConceptMap 模板。

        Args:
            llm_client: 用于提取的语言模型客户端。
            embedder: 用于概念去重和索引的嵌入模型。
            extraction_mode: 提取策略：
                - "one_stage": 同时提取节点和边（速度更快）。
                - "two_stage": 先提取节点，再提取边（准确度更高）。
            chunk_size: 每个文本块的最大字符数。
            chunk_overlap: 文本块之间的重叠字符数。
            max_workers: 并行处理的最大线程数。
            verbose: 如果为 True，则打印详细的进度日志。
            **kwargs: 传给 AutoGraph 构造函数的其他参数。
        """
        super().__init__(
            node_schema=Concept,
            edge_schema=ConceptRelation,
            node_key_extractor=lambda x: x.term.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.relation_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CONCEPT_MAP_PROMPT,
            prompt_for_node_extraction=CONCEPT_MAP_NODE_PROMPT,
            prompt_for_edge_extraction=CONCEPT_MAP_EDGE_PROMPT,
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
        def node_label_extractor(node: Concept) -> str:
            return f"{ node.term }"
    
        def edge_label_extractor(edge: ConceptRelation) -> str:
            return f"{ edge.source }"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
