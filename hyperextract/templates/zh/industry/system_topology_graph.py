"""系统拓扑图谱 - 提取工厂的厂区、系统、子系统、设备等层级结构。

适用于系统说明书、工厂布局图、系统架构文档等文本。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class SystemEntity(BaseModel):
    """系统拓扑实体，包括厂区、系统、子系统、设备等。"""

    name: str = Field(description="实体名称（如：A工厂、制造车间A、数控加工系统、冷却系统等）。")
    category: str = Field(description="类别：厂区、系统、子系统、设备。")
    function: Optional[str] = Field(default=None, description="功能描述。")
    capacity: Optional[str] = Field(default=None, description="容量或规模。")


class SystemHierarchy(BaseModel):
    """系统层级关系。"""

    source: str = Field(description="上级实体名称（厂区或系统）。")
    target: str = Field(description="下级实体名称（系统或子系统或设备）。")
    relationType: str = Field(description="关系类型：包含等。")


_NODE_PROMPT = """## 角色与任务
你是一位工业系统架构分析专家，请从文本中提取所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括厂区、系统、子系统、设备等
- **边 (Edge)**：实体之间的层级包含关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别厂区名称（如A工厂、B工厂）
- 识别生产系统名称（如制造车间、加工车间）
- 识别子系统名称（如数控加工系统、冷却系统）
- 识别具体设备名称（如数控加工中心、机械臂、泵等）
- 为每个实体指定类别（厂区/系统/子系统/设备）

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取实体之间的层级关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括厂区、系统、子系统、设备等
- **边 (Edge)**：实体之间的层级包含关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 识别厂区与系统之间的包含关系
- 识别系统与子系统之间的包含关系
- 识别子系统与设备之间的包含关系

"""

_PROMPT = """## 角色与任务
你是一位工业系统架构分析专家，请从文本中提取实体和它们之间的层级关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括厂区、系统、子系统、设备等
- **边 (Edge)**：实体之间的层级包含关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别厂区（如A工厂、B工厂）
- 识别生产系统（如制造车间、加工车间）
- 识别子系统（如数控加工系统、冷却系统）
- 识别具体设备（如数控加工中心、机械臂、泵等）
- 建立上下级的层级包含关系

### 源文本:
"""


class SystemTopologyGraph(AutoGraph[SystemEntity, SystemHierarchy]):
    """
    适用文档: 系统说明书、工厂布局图、系统架构文档

    功能介绍:
    从系统说明书中提取厂区、系统、子系统和设备的层级关系，构建完整的工厂系统架构视图。

    Example:
        >>> template = SystemTopologyGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("A工厂包含制造车间A，制造车间A包括数控加工系统和物料输送系统...")
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
        初始化系统拓扑图谱模板。

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
            node_schema=SystemEntity,
            edge_schema=SystemHierarchy,
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
        展示系统拓扑图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: SystemEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: SystemHierarchy) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
