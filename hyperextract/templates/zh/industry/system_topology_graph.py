from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class SystemEntity(BaseModel):
    """
    系统拓扑实体，包括厂区、系统、子系统、设备等。
    """

    name: str = Field(description="实体名称（如：A工厂、制造车间A、数控加工系统、冷却系统等）。")
    category: str = Field(
        description='类别：厂区、系统、子系统、设备。'
    )
    function: Optional[str] = Field(
        None,
        description="功能描述。",
    )
    capacity: Optional[str] = Field(
        None,
        description="容量或规模。",
    )


class SystemHierarchy(BaseModel):
    """
    系统层级关系。
    """

    source: str = Field(description="上级实体名称（厂区或系统）。")
    target: str = Field(description="下级实体名称（系统或子系统或设备）。")
    relation_type: str = Field(
        description='关系类型：包含。'
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是工业系统架构分析专家。从系统说明书中提取厂区、系统、子系统和设备的层级关系。\n\n"
    "规则:\n"
    "- 识别厂区（如A工厂、B工厂）。\n"
    "- 识别生产系统（如制造车间、加工车间）。\n"
    "- 识别子系统（如数控加工系统、冷却系统、物料输送系统）。\n"
    "- 识别具体设备（如数控加工中心、机械臂、泵等）。\n"
    "- 建立上下级的层级包含关系。\n"
)

_NODE_PROMPT = (
    "你是工业系统架构分析专家。从系统说明书中提取所有实体（节点）。\n\n"
    "提取规则:\n"
    "- 识别厂区名称。\n"
    "- 识别生产系统名称。\n"
    "- 识别子系统名称。\n"
    "- 识别具体设备名称。\n"
    "- 为每个实体指定类别（厂区/系统/子系统/设备）。\n"
    "- 不建立实体之间的关系。\n"
)

_EDGE_PROMPT = (
    "你是工业系统架构分析专家。在获得实体清单的基础上，提取系统层级关系（边）。\n\n"
    "提取规则:\n"
    "- 识别厂区与系统之间的包含关系。\n"
    "- 识别系统与子系统之间的包含关系。\n"
    "- 识别子系统与设备之间的包含关系。\n"
    "- 记录层级类型。\n"
    "- 仅在提供的实体列表中建立关系。\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class SystemTopologyGraph(AutoGraph[SystemEntity, SystemHierarchy]):
    """
    适用文档: 系统说明书、工厂布局图、系统架构文档。

    模板用于从系统说明书中提取厂区、系统、子系统和设备的层级关系。
    构建完整的工厂系统架构视图。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> topology = SystemTopologyGraph(llm_client=llm, embedder=embedder)
        >>> doc = "A工厂包含制造车间A，制造车间A包括数控加工系统和物料输送系统..."
        >>> topology.feed_text(doc)
        >>> topology.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化系统拓扑图谱模板。

        Args:
            llm_client (BaseChatModel): 用于实体和关系提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。默认为 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=SystemEntity,
            edge_schema=SystemHierarchy,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.relation_type})-->{x.target.strip()}"
            ),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
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
        使用 OntoSight 可视化系统拓扑图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的关系数。默认 3。
        """

        def node_label_extractor(node: SystemEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: SystemHierarchy) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
