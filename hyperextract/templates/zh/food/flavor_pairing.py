from typing import Optional, Any, Literal
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class FlavorComponent(BaseModel):
    """
    个别风味分子或复合物及其性质。
    """

    name: str = Field(description="风味成分的名称，例如木质素、硫含物、咖啡因。")
    component_type: str = Field(
        description="分类：分子、香气、甜味、苦味、酸味、鲜味、油质、烤焙、花卉。"
    )
    description: str = Field(
        description="来自文本的成分特征，例如温暖、烟熏、柔和的甜味。"
    )


class FlavorRelationship(BaseModel):
    """
    两个风味成分之间的关系。
    """

    source_component: str = Field(description="第一个风味成分的名称。")
    target_component: str = Field(description="第二个风味成分的名称。")
    relationship_type: Literal[
        "Contains", "Pairs_Well", "Confirms", "Complements", "Contrasts"
    ] = Field(
        description="关系类型：Contains(包含)、Pairs_Well(配对好)、Confirms(确认)、Complements(补充)、Contrasts(对比)。"
    )
    pairing_mechanism: Optional[str] = Field(
        None,
        description="为什么这两个成分会一起工作，例如共享的木质素分子或互补的甜度曲线。"
    )
    pairing_quality: Optional[str] = Field(
        None, description="配对质量的评估：优秀、好、可接受、有冲突。"
    )
    culinary_context: Optional[str] = Field(
        None, description='应用这个配对的烹饪环境或菜肴，例如"法式高汤"或"甜点"。'
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是美食科学家。从美食科学论文中提取风味配对和感官关系。\n\n"
    "规则:\n"
    "- 识别个别风味分子和复合物。\n"
    "- 链接配对好的成分和为什么它们有效。\n"
    "- 提取描述性术语（温暖、烟熏、花卉等）。\n"
    "- 关注共享分子或感官相补性的机制。\n"
    "- 记录烹饪环境（酱料、甜点、肉类等）。"
)

_NODE_PROMPT = (
    "你是美食科学家。从食品科学论文或菜谱中提取所有风味成分（节点）。\n\n"
    "提取规则:\n"
    "- 列出所有提到的风味分子、香气或感官特征。\n"
    "- 分类为 molecules、aromas、tastes、textures 等。\n"
    "- 包括来自源文本的描述性特征（工作、柔软、复杂）。\n"
    "- 不包括有关如何将成分配对的信息。\n"
    "- 此阶段保持所有成分作为独立实体。"
)

_EDGE_PROMPT = (
    "你是美食科学家。给定一个成分列表，识别哪些成分配对好（边），以及为什么。\n\n"
    "配对规则:\n"
    "- 连接列表中存在的成分。\n"
    "- 说明配对机制（共享分子、互补风味）。\n"
    "- 评评对质量（优秀、好、可接受、冲突）。\n"
    "- 记录烹饪应用（什么菜肴、什么菜系）。\n"
    "- 来自源文本中的链接只存在于显式提及的成分。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class FlavorPairingGraph(AutoGraph[FlavorComponent, FlavorRelationship]):
    """
    适用文档: 美食科学期刊、经验烹饪书、感官评估报告、风味科学研究、菜单设计指南、R&D 笔记。

    模板用于从感官和分子证据中提取风味配对知识。支持菜单创新、厨师培训和结构化食物组合理论。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> flavors = FlavorPairingGraph(llm_client=llm, embedder=embedder)
        >>> text = "草莓和黑胡椒通过共有的木质素分子进行配对"
        >>> flavors.feed_text(text)
        >>> flavors.show()
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
        初始化风味配对图谱模板。

        Args:
            llm_client (BaseChatModel): 用于提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=FlavorComponent,
            edge_schema=FlavorRelationship,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                x.source_component.strip().lower(),
                x.target_component.strip().lower(),
            ),
            nodes_in_edge_extractor=lambda x: (
                x.source_component.strip(),
                x.target_component.strip(),
            ),
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
        top_k_nodes_for_search: int = 5,
        top_k_edges_for_search: int = 5,
        top_k_nodes_for_chat: int = 5,
        top_k_edges_for_chat: int = 5,
    ) -> None:
        """
        使用 OntoSight 可视化风味配对网络。

        Args:
            top_k_nodes_for_search (int): 检索的成分数。默认 5。
            top_k_edges_for_search (int): 检索的配对数。默认 5。
            top_k_nodes_for_chat (int): 对话上下文中的成分数。默认 5。
            top_k_edges_for_chat (int): 对话上下文中的配对数。默认 5。
        """

        def node_label_extractor(node: FlavorComponent) -> str:
            return f"{node.name} ({node.component_type})"

        def edge_label_extractor(edge: FlavorRelationship) -> str:
            quality = f" [{edge.pairing_quality}]" if edge.pairing_quality else ""
            return f"{edge.relationship_type}{quality}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
