from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================


class AnimalNode(BaseModel):
    """畜牧管理中的实体（如个体动物、品种、群体、健康状况）。"""

    name: str = Field(description="动物个体或群体的名称/ID。")
    category: str = Field(
        description="类别：'个体', '品种', '品系', '健康状况', '营养/饲料', '设施'。"
    )
    traits: Optional[str] = Field(description="关键体貌特征、基因标记或健康指标。")


class BreedingRelation(BaseModel):
    """育种与健康管理中的关系。"""

    source: str = Field(description="源畜牧实体。")
    target: str = Field(description="目标畜牧实体。")
    relation_type: str = Field(
        description="类型：'父代/母代', '与...交配', '属于', '诊断为', '饲喂'。"
    )
    details: Optional[str] = Field(description="继承特征、剂量或具体的健康观察。")


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

LIVESTOCK_GRAPH_PROMPT = (
    "你是一位畜牧专家和遗传学家。请从文本中提取育种与健康管理图谱。\n\n"
    "提取指南：\n"
    "- 识别动物个体及其品种。\n"
    "- 映射家谱关系（亲子关系）和育种配对。\n"
    "- 将动物与其健康状况、疫苗接种和营养记录关联起来。"
)

LIVESTOCK_NODE_PROMPT = "请提取畜牧实体：识别特定动物（通过ID或名称）、品种、健康状况、疫苗类型以及特定的饲料。为每一项提供相关的特征或指标。"

LIVESTOCK_EDGE_PROMPT = "逻辑化地连接畜牧实体。映射家族树（亲缘链接）、育种历史以及医疗/营养事件。确保准确使用'与...交配'或'饲喂'等关系类型。"

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================


class LivestockGraph(AutoGraph[AnimalNode, BreedingRelation]):
    """
    用于管理畜牧系谱、健康记录和育种计划的模板。

    适用于牧场管理软件、兽医记录和基因追踪。

    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> graph = LivestockGraph(llm_client=llm, embedder=embedder)
        >>> text = "402号母牛（安格斯）与09号公牛配种以提高肉质。"
        >>> graph.feed_text(text)
        >>> print(graph.edges) # 提取育种关系
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
        初始化 LivestockGraph 模板。

        Args:
            llm_client: 用于提取的语言模型客户端。
            embedder: 用于去重的嵌入模型。
            extraction_mode: "one_stage" 或 "two_stage"。
            chunk_size: 每个分块的最大字符数。
            chunk_overlap: 分块间的重叠字符数。
            max_workers: 并行处理的最大 worker 数量。
            verbose: 是否开启进度日志。
            **kwargs: 传递给 AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=AnimalNode,
            edge_schema=BreedingRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.relation_type.lower()})-->{x.target.strip()}"
            ),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=LIVESTOCK_GRAPH_PROMPT,
            prompt_for_node_extraction=LIVESTOCK_NODE_PROMPT,
            prompt_for_edge_extraction=LIVESTOCK_EDGE_PROMPT,
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

        def node_label_extractor(node: AnimalNode) -> str:
            info = f" ({node.category})" if getattr(node, "category", None) else ""
            return f"{node.name}{info}"

        def edge_label_extractor(edge: BreedingRelation) -> str:
            return f"{edge.relation_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
