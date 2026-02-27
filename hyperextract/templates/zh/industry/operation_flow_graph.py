"""操作流程图谱 - 提取操作步骤、设备状态和预期结果，识别操作流程中的步骤顺序和状态变化。

适用于运行规程、启停操作票、设备操作手册、安全操作规程等文本。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class OperationStep(BaseModel):
    """操作步骤实体，包括具体的操作动作和设备状态。"""

    name: str = Field(description="操作步骤名称（如：开启辅助电源、启动液压系统、检查状态、关闭主电源等）。")
    category: str = Field(description="类别：动作、设备状态。动作如开启、关闭、检查等；设备状态如运行中、待机、停止等。")
    description: Optional[str] = Field(default=None, description="对该操作步骤的详细描述。")
    expected_result: Optional[str] = Field(default=None, description="执行该步骤后的预期结果。")
    target_equipment: Optional[str] = Field(default=None, description="涉及的目标设备名称。")


class OperationTransition(BaseModel):
    """操作步骤之间的流转关系。"""

    source: str = Field(description="当前步骤名称。")
    target: str = Field(description="下一步骤名称。")
    relationType: str = Field(description="关系类型：下一步、触发、导致。")
    trigger_condition: Optional[str] = Field(default=None, description="触发下一步骤的条件。")
    state_change: Optional[str] = Field(default=None, description="状态变化描述。")


_NODE_PROMPT = """## 角色与任务
你是一位工业操作流程分析专家，请从文本中提取所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括操作步骤（如开启电源、启动设备）和设备状态（如运行中、待机、停止）
- **边 (Edge)**：操作步骤之间的流转关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别操作步骤名称（如开启辅助电源、启动液压系统、检查状态、关闭主电源等）
- 识别设备状态名称（如运行中、待机、停止、故障等）
- 为每个实体指定类别（动作/设备状态）
- 记录每一步骤的预期结果和涉及设备

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取操作步骤之间的流转关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：操作步骤之间的流转关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 识别步骤的执行顺序（当前步骤 → 下一步骤）
- 提取触发下一步骤的条件
- 记录设备状态的变化
- 关系类型使用：下一步、触发、导致

### 已知实体列表:
"""

_PROMPT = """## 角色与任务
你是一位工业操作流程分析专家，请从文本中提取操作步骤、设备状态和预期结果。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括操作步骤（如开启电源、启动设备）和设备状态（如运行中、待机、停止）
- **边 (Edge)**：操作步骤之间的流转关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别各个操作步骤和执行顺序（如：开启辅助电源 → 启动液压系统 → 启动控制系统）
- 识别设备状态变化（如：从待机状态切换到运行状态）
- 记录每一步骤的详细操作内容、预期结果和涉及设备
- 建立步骤之间的流转关系

### 源文本:
"""


class OperationFlowGraph(AutoGraph[OperationStep, OperationTransition]):
    """
    适用文档: 运行规程、启停操作票、设备操作手册、安全操作规程

    功能介绍:
    从运行规程中提取操作步骤、设备状态和预期结果，识别操作流程中的步骤顺序和状态变化，
    为操作培训和安全管理提供参考。

    Example:
        >>> template = OperationFlowGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("开机流程：1. 检查电源是否正常；2. 开启控制柜主开关...")
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
        初始化操作流程图谱模板。

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
            node_schema=OperationStep,
            edge_schema=OperationTransition,
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
        展示操作流程图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: OperationStep) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: OperationTransition) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
