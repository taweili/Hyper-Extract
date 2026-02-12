from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================

class Entity(BaseModel):
    """通用实体，代表人物、组织、地点、物体或核心概念。"""
    name: str = Field(description="实体的名称。")
    category: str = Field(
        description="实体的类别（例如：人物、组织、地理位置、概念、事件、物体）。"
    )
    description: Optional[str] = Field(
        description="该实体的简要描述及其在文本中的作用。"
    )

class Relation(BaseModel):
    """两个实体之间的事实关系。"""
    source: str = Field(description="源实体的名。")
    target: str = Field(description="目标实体的名称。")
    relation: str = Field(description="关系类型（例如：任职于、位于、创立、收购）。")
    details: Optional[str] = Field(description="关于该关系的额外上下文或详细描述。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

KNOWLEDGE_GRAPH_PROMPT = (
    "你是一个专业的知识提取专家。你的任务是从提供的文本中提取一个事实知识图谱。"
    "重点识别关键实体（人物、组织、地理位置、重要物体）以及它们之间明确的关系。\n\n"
    "提取指南：\n"
    "- 准确性：从文本中提取明确的实体及其事实属性。\n"
    "- 关系映射：描述实体之间如何互动或连接。\n"
    "- 简洁性：使用清晰、简洁的语言进行描述和关系定义。"
)

KNOWLEDGE_GRAPH_NODE_PROMPT = (
    "请从文本中提取所有关键实体。重点识别人物、组织、地理位置以及重要的物体。"
    "为每个实体提供名称、类别以及简明扼要的描述。"
)

KNOWLEDGE_GRAPH_EDGE_PROMPT = (
    "基于文本识别以下已知实体之间的事实关系。重点关注如“任职于”、“位于”、“创立”或“收购”等互动。"
    "请勿虚构不在列表中的实体。"
)

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================

class KnowledgeGraph(AutoGraph[Entity, Relation]):
    """
    用于事实提取的基础知识图谱模板。
    
    该模板经过优化，适用于从新闻文章、传记和百科文本中提取实体（人物、地点、组织）及其事实交互。
    
    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # 初始化模板
        >>> kg = KnowledgeGraph(llm_client=llm, embedder=embedder)
        >>> # 从文本中提取知识
        >>> text = "苏轼出生于眉州眉山，是北宋著名的文学家。"
        >>> kg.feed_text(text)
        >>> print(kg.nodes)  # 输出: [Entity(name='苏轼', ...), Entity(name='眉州眉山', ...)]
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
        初始化 KnowledgeGraph 模板。

        Args:
            llm_client: 用于提取的语言模型客户端。
            embedder: 用于实体去重和索引的嵌入模型。
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
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--[{x.relation.lower()}]-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=KNOWLEDGE_GRAPH_PROMPT,
            prompt_for_node_extraction=KNOWLEDGE_GRAPH_NODE_PROMPT,
            prompt_for_edge_extraction=KNOWLEDGE_GRAPH_EDGE_PROMPT,
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
        def node_label_extractor(node: Entity) -> str:
            info = f" ({node.category})" if getattr(node, "category", None) else ""
            return f"{node.name}{info}"
    
        def edge_label_extractor(edge: Relation) -> str:
            return f"{edge.relation}"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
