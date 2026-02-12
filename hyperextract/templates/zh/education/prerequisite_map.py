from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================

class KnowledgePointNode(BaseModel):
    """
    学科大纲中的原子知识单位、概念或技能。
    """
    name: str = Field(
        description="知识点或概念的标准名称。"
    )
    level: str = Field(
        description="难度等级：'入门'、'中级'、'高级'、'专家'。"
    )
    concept_type: str = Field(
        description="教学类型：'定义'、'定理'、'公式'、'方法'、'应用'。"
    )
    description: Optional[str] = Field(
        None, description="该概念的核心教学内涵简述。"
    )

class PrerequisiteRelation(BaseModel):
    """
    有向依赖关系，表示一个概念必须在另一个概念之前学习。
    """
    source: str = Field(description="先修知识点（必须先学）。")
    target: str = Field(description="后续知识点（后学）。")
    dependency_type: str = Field(
        "Prerequisite",
        description="依赖性质：'必要' (必须先学), '同步' (建议同时学), '辅助' (有助于学习)。"
    )
    weight: float = Field(
        1.0, description="依赖强度，范围从 0.0 到 1.0。"
    )

# ==============================================================================
# 2. Prompts 提示词
# ==============================================================================

_PROMPT = (
    "你是一位资深课程架构师和教育心理学家。请从文本中提取知识点的逻辑结构。\n\n"
    "提取规则：\n"
    "- 识别构成学习路径的原子化概念。\n"
    "- 建立清晰的有向依赖关系（先修要求）。\n"
    "- 确保生成的图谱符合科学的教学演进逻辑。"
)

_NODE_PROMPT = (
    "你是一位擅长知识拆解的教育心理学家。你的任务是识别所有离散的知识点（节点）。\n\n"
    "提取规则：\n"
    "- 关注代表特定学术概念、公式或方法的名词或名词短语。\n"
    "- 根据上下文分配难度等级和概念类型。\n"
    "- 此阶段不要识别关系或依赖。"
)

_EDGE_PROMPT = (
    "你是一位课程设计师。根据已识别的知识点，映射先修关系（边）。\n\n"
    "提取规则：\n"
    "- 确定概念 A 是否是学习概念 B 的必要前提。\n"
    "- 将依赖关系分类为必要、同步或辅助。\n"
    "- 仅在提供的概念列表之间建立关系。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class PrerequisiteMapGraph(AutoGraph[KnowledgePointNode, PrerequisiteRelation]):
    """
    用于构建知识依赖有向无环图 (DAG) 的教育领域模板。
    适用于教学大纲分析、自动化学习路径生成和学生测评规划。

    用法示例：
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.zh.education.prerequisite_map import PrerequisiteMapGraph
        >>> graph = PrerequisiteMapGraph(llm, embedder)
        >>> graph.feed_text("在理解微积分之前，必须先掌握代数和函数。")
        >>> graph.extract()
        >>> print(graph.nodes) # 输出包含代数、函数、微积分及其依赖关系的节点
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
        **kwargs: Any,
    ):
        """
        初始化先修图谱模板。

        参数描述:
            llm_client (BaseChatModel): 用于提取的语言模型客户端。
            embedder (Embeddings): 用于节点/边去重和合并的嵌入模型。
            extraction_mode (str): 提取模式。'one_stage' 为单阶段合并提取, 'two_stage' 为节点和边分开提取。
            chunk_size (int): 处理大文档时的文本切片大小。
            chunk_overlap (int): 切片之间的重叠长度以保持上下文完整性。
            max_workers (int): 并行处理的最大进程数。
            verbose (bool): 是否在执行过程中打印详细日志。
            **kwargs: 透传给 AutoGraph 基类的其他参数。
        """
        super().__init__(
            node_schema=KnowledgePointNode,
            edge_schema=PrerequisiteRelation,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}->{x.target.strip().lower()}"
            ),
            nodes_in_edge_extractor=lambda x: (x.source.strip().lower(), x.target.strip().lower()),
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
            **kwargs,
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
        def node_label_extractor(node: KnowledgePointNode) -> str:
            return f"{node.name}"
    
        def edge_label_extractor(edge: PrerequisiteRelation) -> str:
            return f"{edge.dependency_type}"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
