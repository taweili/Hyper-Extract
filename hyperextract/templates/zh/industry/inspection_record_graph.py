from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class InspectionEntity(BaseModel):
    """
    巡检实体，包括设备和巡检项。
    """

    name: str = Field(description="实体名称（如：数控加工中心、机械臂系统、电机运行状态、轴承温度检查等）。")
    category: str = Field(
        description='类别：设备、巡检项。'
    )
    description: Optional[str] = Field(
        None,
        description="对该实体的描述。",
    )


class InspectionHierarchy(BaseModel):
    """
    巡检实体之间的层级关系。
    """

    source: str = Field(description="父实体（整体/设备）名称。")
    target: str = Field(description="子实体（巡检项/部分）名称。")
    relation_type: str = Field(
        description='关系类型：属于、子类。'
    )
    details: Optional[str] = Field(
        None,
        description="关系详细说明。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是工业设备巡检分析专家。从巡检记录文档中提取设备和巡检项，构建巡检层级结构。\n\n"
    "规则:\n"
    "- 识别大设备（如数控加工中心、机械臂系统、物料输送系统等）。\n"
    "- 识别每个设备下的巡检项（如电机运行状态、轴承温度、冷却液位等）。\n"
    "- 建立巡检项与设备之间的从属关系。\n"
)

_NODE_PROMPT = (
    "你是工业设备巡检分析专家。从巡检记录文档中提取所有实体（节点）。\n\n"
    "提取规则:\n"
    "- 识别设备名称（大类）。\n"
    "- 识别巡检项名称（具体检查点）。\n"
    "- 为每个实体指定类别（设备/巡检项）。\n"
    "- 不建立实体之间的关系。\n"
)

_EDGE_PROMPT = (
    "你是工业设备巡检分析专家。在获得实体清单的基础上，提取实体之间的层级关系（边）。\n\n"
    "提取规则:\n"
    "- 识别巡检项与设备之间的从属关系。\n"
    "- 例如：电机运行状态 属于 数控加工中心。\n"
    "- 仅在提供的实体列表中建立关系。\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class InspectionRecordGraph(AutoGraph[InspectionEntity, InspectionHierarchy]):
    """
    适用文档: 巡检记录本、设备运行记录、巡检日报、设备点检表。

    模板用于从巡检记录中提取设备和巡检项，构建巡检层级结构。
    识别设备与巡检项之间的从属关系（Part-Of）。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> inspection = InspectionRecordGraph(llm_client=llm, embedder=embedder)
        >>> doc = "2024年3月15日，对A生产线进行日常巡检。数控加工中心：电机运行正常..."
        >>> inspection.feed_text(doc)
        >>> inspection.show()
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
        初始化巡检层级图谱模板。

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
            node_schema=InspectionEntity,
            edge_schema=InspectionHierarchy,
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
        使用 OntoSight 可视化巡检层级图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的关系数。默认 3。
        """

        def node_label_extractor(node: InspectionEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: InspectionHierarchy) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
