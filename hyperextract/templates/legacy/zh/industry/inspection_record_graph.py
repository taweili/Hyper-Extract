"""巡检记录图谱 - 提取设备和巡检项，构建巡检层级结构，识别设备与巡检项之间的从属关系。

适用于巡检记录本、设备运行记录、巡检日报、设备点检表等文本。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class InspectionEntity(BaseModel):
    """巡检实体，包括设备和巡检项。"""

    name: str = Field(description="实体名称（如：数控加工中心、机械臂系统、电机运行状态、轴承温度检查等）。")
    category: str = Field(description="类别：设备、巡检项。")
    description: Optional[str] = Field(default=None, description="对该实体的描述。")


class InspectionHierarchy(BaseModel):
    """巡检实体之间的层级关系。"""

    source: str = Field(description="父实体（整体/设备）名称。")
    target: str = Field(description="子实体（巡检项/部分）名称。")
    relationType: str = Field(description="关系类型：属于、子类。")
    details: Optional[str] = Field(default=None, description="关系详细说明。")


_NODE_PROMPT = """## 角色与任务
你是一位工业设备巡检分析专家，请从文本中提取所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括设备（如数控加工中心）和巡检项（如电机运行状态、轴承温度）
- **边 (Edge)**：设备与巡检项之间的从属关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别设备名称（大类）
- 识别巡检项名称（具体检查点）
- 为每个实体指定类别（设备/巡检项）

## 巡检记录文档:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取实体之间的层级关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：设备与巡检项之间的从属关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 识别巡检项与设备之间的从属关系
- 例如：电机运行状态 属于 数控加工中心

## 已知实体列表:
{known_nodes}

## 巡检记录文档:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位工业设备巡检分析专家，请从文本中提取设备和巡检项，构建巡检层级结构。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括设备（如数控加工中心）和巡检项（如电机运行状态、轴承温度）
- **边 (Edge)**：设备与巡检项之间的从属关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别大设备（如数控加工中心、机械臂系统、物料输送系统等）
- 识别每个设备下的巡检项（如电机运行状态、轴承温度、冷却液位等）
- 建立巡检项与设备之间的从属关系

## 巡检记录文档:
{source_text}
"""


class InspectionRecordGraph(AutoGraph[InspectionEntity, InspectionHierarchy]):
    """
    适用文档: 巡检记录本、设备运行记录、巡检日报、设备点检表

    功能介绍:
    从巡检记录中提取设备和巡检项，构建巡检层级结构，识别设备与巡检项之间的从属关系。

    Example:
        >>> template = InspectionRecordGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("2024年3月15日，对A生产线进行日常巡检。数控加工中心：电机运行正常...")
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
        初始化巡检层级图谱模板。

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
            node_schema=InspectionEntity,
            edge_schema=InspectionHierarchy,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
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
        展示巡检层级图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: InspectionEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: InspectionHierarchy) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
