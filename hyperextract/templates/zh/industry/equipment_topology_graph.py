"""设备拓扑图谱 - 提取工业设备的实体及其相互连接关系，包括物料流向、能量传递、控制信号等。

适用于设备系统图、管道仪表图（P&ID）、设备清单、设备台账等文本。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class IndustrialEquipment(BaseModel):
    """工业设备实体，包括主机、辅机、部件、仪表、阀门、管路等。"""

    name: str = Field(description="设备或部件名称。")
    category: str = Field(description="类别：主机、辅机、部件、仪表、阀门、管路、系统、电机、泵、风机、容器等。")
    location: Optional[str] = Field(default=None, description="安装位置（如：生产车间一层、主厂房二层）。")
    status: Optional[str] = Field(default=None, description="运行状态：运行、备用、检修、停运。")
    specification: Optional[str] = Field(default=None, description="规格型号或技术参数。")
    manufacturer: Optional[str] = Field(default=None, description="制造厂家。")


class EquipmentConnection(BaseModel):
    """设备之间的连接关系。"""

    source: str = Field(description="上游设备或源设备名称。")
    target: str = Field(description="下游设备或目标设备名称。")
    connectionType: str = Field(description="连接类型：物料输送、能量传递、控制信号、工艺流程、电气连接、仪表监测等。")
    description: Optional[str] = Field(default=None, description="连接关系的详细描述（如：高温物料流向、循环水回路、闭环控制系统）。")


_NODE_PROMPT = """## 角色与任务
你是一位工业设备管理专家，请从文本中提取所有设备实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的设备实体，包括主机、辅机、部件、仪表、阀门、泵、风机、电机等
- **边 (Edge)**：设备之间的连接关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的设备，禁止将多个设备合并为一个节点
2. 设备名称与原文保持一致

### 领域特定规则
- 识别设备名称和部件名称
- 分类设备类别（主机、辅机、部件、仪表、阀门、管路、系统、电机、泵、风机、容器等）
- 记录安装位置和运行状态

## 设备系统文档:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知设备清单中提取设备之间的连接关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的设备实体
- **边 (Edge)**：设备之间的连接关系

## 提取规则
### 核心约束
1. 仅从已知设备列表中提取边，不要创建新的设备节点
2. 关系描述应与原文保持一致

### 领域特定规则
- 识别物料输送关系（上游→下游）
- 识别能量传递关系（驱动设备→被驱动设备）
- 识别控制信号关系（控制设备→被控设备）
- 识别工艺流程关系（前一工序→后一工序）
- 识别电气连接和仪表监测关系

## 已知设备列表:
{known_nodes}

## 设备系统文档:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位工业设备管理专家，请从文本中提取设备实体及其相互连接关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的设备实体，包括主机、辅机、部件、仪表、阀门、泵、风机、电机等
- **边 (Edge)**：设备之间的连接关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的设备，禁止将多个设备合并为一个节点
2. 设备名称与原文保持一致
3. 仅从已知设备列表中提取边，不要创建新的设备节点
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别所有设备、部件和系统
- 分类设备类型（主机/辅机/部件/仪表/阀门/管路/系统/电机/泵/风机/容器等）
- 提取设备之间的连接关系，包括物料输送、能量传递、控制信号等
- 记录安装位置和运行状态

## 设备系统文档:
{source_text}
"""


class EquipmentTopologyGraph(AutoGraph[IndustrialEquipment, EquipmentConnection]):
    """
    适用文档: 设备系统图、管道仪表图（P&ID）、设备清单、设备台账

    功能介绍:
    从工业设备文档中提取设备拓扑关系，识别设备之间的物理连接、物料流向、能量传递和控制信号关系。

    Example:
        >>> template = EquipmentTopologyGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("A生产线由反应釜B、冷却泵C和控制柜D组成...")
        >>> template.show()
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
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            chunk_size: 每个分块的最大字符数，默认为 2048
            chunk_overlap: 分块之间的重叠字符数，默认为 256
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=IndustrialEquipment,
            edge_schema=EquipmentConnection,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.connectionType}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
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
    ):
        """
        展示设备拓扑图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: IndustrialEquipment) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: EquipmentConnection) -> str:
            return edge.connectionType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
