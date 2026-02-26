from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class IndustrialEquipment(BaseModel):
    """
    工业设备实体，包括主机、辅机、部件、仪表、阀门、管路等。
    """

    name: str = Field(description="设备或部件名称。")
    category: str = Field(
        description='类别：主机、辅机、部件、仪表、阀门、管路、系统、电机、泵、风机、容器等。'
    )
    location: Optional[str] = Field(
        None,
        description="安装位置（如：生产车间一层、主厂房二层）。",
    )
    status: Optional[str] = Field(
        None,
        description="运行状态：运行、备用、检修、停运。",
    )
    specification: Optional[str] = Field(
        None,
        description="规格型号或技术参数。",
    )
    manufacturer: Optional[str] = Field(
        None,
        description="制造厂家。",
    )


class EquipmentConnection(BaseModel):
    """
    设备之间的连接关系。
    """

    source: str = Field(description="上游设备或源设备名称。")
    target: str = Field(description="下游设备或目标设备名称。")
    connection_type: str = Field(
        description='连接类型：物料输送、能量传递、控制信号、工艺流程、电气连接、仪表监测。'
    )
    description: Optional[str] = Field(
        None,
        description="连接关系的详细描述（如：高温物料流向、循环水回路、闭环控制系统）。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是工业设备管理专家。从工业设备文档中提取设备实体及其相互连接关系。\n\n"
    "规则:\n"
    "- 识别所有设备、部件和系统，包括主机、辅机、仪表、阀门、泵、风机、电机等。\n"
    "- 分类设备类型（主机/辅机/部件/仪表/阀门/管路/系统）。\n"
    "- 提取设备之间的连接关系，包括物料输送、能量传递、控制信号等。\n"
    "- 记录安装位置和运行状态。\n"
)

_NODE_PROMPT = (
    "你是工业设备管理专家。从文档中提取所有设备实体（节点）。\n\n"
    "提取规则:\n"
    "- 识别设备名称和部件名称。\n"
    "- 分类设备类别（主机、辅机、部件、仪表、阀门、管路、系统、电机、泵、风机、容器等）。\n"
    "- 记录安装位置和运行状态。\n"
    "- 不建立设备之间的关系。\n"
)

_EDGE_PROMPT = (
    "你是工业设备管理专家。在获得设备清单的基础上，提取设备之间的连接关系（边）。\n\n"
    "提取规则:\n"
    "- 识别设备之间的物料输送关系（上游→下游）。\n"
    "- 识别能量传递关系（驱动设备→被驱动设备）。\n"
    "- 识别控制信号关系（控制设备→被控设备）。\n"
    "- 识别工艺流程关系（前一工序→后一工序）。\n"
    "- 识别电气连接和仪表监测关系。\n"
    "- 仅在提供的设备列表中建立关系，不要创建新的设备节点。\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class EquipmentTopologyGraph(AutoGraph[IndustrialEquipment, EquipmentConnection]):
    """
    适用文档: 设备系统图、管道仪表图（P&ID）、设备清单、设备台账、系统说明书、检修规程中的设备章节。

    模板用于从工业设备文档中提取设备拓扑关系。识别设备之间的物理连接、
    物料流向、能量传递和控制信号关系，构建设备系统拓扑图。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> topology = EquipmentTopologyGraph(llm_client=llm, embedder=embedder)
        >>> doc = "A生产线由反应釜B、冷却泵C和控制柜D组成。反应釜B产生的物料通过管道输送至冷却泵C进行冷却，C由电机E驱动。控制柜D实时监测B的温度并控制E的转速。"
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
        初始化设备拓扑图谱模板。

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
            node_schema=IndustrialEquipment,
            edge_schema=EquipmentConnection,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.connection_type})-->{x.target.strip()}"
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
        使用 OntoSight 可视化设备拓扑图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的关系数。默认 3。
        """

        def node_label_extractor(node: IndustrialEquipment) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: EquipmentConnection) -> str:
            return edge.connection_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
