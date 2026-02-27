"""维修作业图 - 从维修作业指导书中提取操作人、工具、对象、耗时的复杂关联关系。

适用于维修标准化、维修作业指导书、设备检修规程等文本。
"""

from typing import Optional, Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class MaintenanceEntity(BaseModel):
    """
    维修作业实体节点。
    """

    name: str = Field(
        description="实体名称（例如：维修工李四、扳手、离心泵P-101、润滑油等）。"
    )
    category: str = Field(description="类型：人员、工具、设备、材料、备件、岗位。")
    description: Optional[str] = Field(
        None, description="描述或规格（例如：高级维修工、16mm开口扳手、15kW离心泵）。"
    )


class MaintenanceOperationEdge(BaseModel):
    """
    维修作业超边，连接多个实体。
    """

    nodes: List[str] = Field(
        description="参与作业的节点列表：[操作人员, 工具1, 工具2, 设备, 材料1, ...]"
    )
    operation_name: str = Field(
        description="作业名称或步骤（例如：更换轴承、清洗过滤器、添加润滑油）。"
    )
    duration: Optional[str] = Field(
        None, description="作业耗时（例如：30分钟、2小时、半天）。"
    )
    prerequisite: Optional[str] = Field(
        None, description="前置条件或注意事项（例如：需停机断电、需佩戴防护用品）。"
    )
    quality_standard: Optional[str] = Field(
        None,
        description="质量标准或验收要求（例如：运转正常无异响、螺栓紧固力矩达标）。",
    )


_NODE_PROMPT = """## 角色与任务
你是一位设备维修管理专家，请从维修作业指导书中提取所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的参与维修作业的实体
- **边 (Edge)**：连接多个节点，表达维修作业中的复杂关联关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别维修人员（维修工、班组长、技术员）
- 识别工具（扳手、螺丝刀、千斤顶、测量仪器）
- 识别设备（离心泵、电机、阀门）
- 识别材料（润滑油、密封胶、清洁剂）
- 识别备件（轴承、密封圈、滤芯）

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位设备维修管理专家，请从已知实体列表中提取维修作业中的复杂关联作为超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的参与维修作业的实体
- **边 (Edge)**：连接多个节点，表达维修作业中的复杂关联关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 识别维修作业步骤（更换轴承、清洗过滤器、添加润滑油）
- 关联操作人员和工具
- 关联设备和材料/备件
- 提取作业耗时
- 记录前置条件和质量标准
- 边的 nodes 字段应包含所有参与该作业的实体

"""

_PROMPT = """## 角色与任务
你是一位设备维修管理专家，请从维修作业指导书中提取实体和维修作业中的复杂关联作为超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的参与维修作业的实体
- **边 (Edge)**：连接多个节点，表达维修作业中的复杂关联关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体

### 领域特定规则
- 识别维修人员（维修工、班组长、技术员）
- 识别工具（扳手、螺丝刀、千斤顶、测量仪器）
- 识别设备（离心泵、电机、阀门）
- 识别材料（润滑油、密封胶、清洁剂）
- 识别备件（轴承、密封圈、滤芯）
- 识别维修作业步骤（更换轴承、清洗过滤器、添加润滑油）
- 关联操作人员和工具
- 关联设备和材料/备件
- 提取作业耗时
- 记录前置条件和质量标准

### 源文本:
"""


class MaintenaceOperationMap(
    AutoHypergraph[MaintenanceEntity, MaintenanceOperationEdge]
):
    """
    适用文档: 维修作业指导书、设备检修规程、
    维修标准化文档。

    模板用于从维修作业指导书中提取操作人、工具、对象、耗时
    的复杂关联关系，支持维修标准化和工时估算。

    使用示例:
        >>> operation = MaintenaceOperationMap(llm_client=llm, embedder=embedder)
        >>> doc = "更换离心泵P-101轴承：维修工李四使用扳手和拉马，耗时30分钟..."
        >>> operation.feed_text(doc)
        >>> operation.show()
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
        初始化维修作业图模板。

        Args:
            llm_client (BaseChatModel): 用于作业提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoHypergraph 的其他参数。
        """
        super().__init__(
            node_schema=MaintenanceEntity,
            edge_schema=MaintenanceOperationEdge,
            node_key_extractor=lambda x: x.name,
            nodes_in_edge_extractor=lambda x: x.nodes,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
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
        使用 OntoSight 可视化维修作业图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的作业数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的作业数。默认 3。
        """

        def node_label_extractor(node: MaintenanceEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: MaintenanceOperationEdge) -> str:
            duration = f" [{edge.duration}]" if edge.duration else ""
            return f"{edge.operation_name}{duration}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
