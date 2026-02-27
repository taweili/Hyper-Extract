"""故障知识超图 - 从故障案例中提取故障现象、根因、部件、解决方案的复杂关联关系。

适用于故障诊断、故障案例库、设备故障分析等文本。
"""

from typing import Optional, Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class FailureEntity(BaseModel):
    """
    故障知识实体节点。
    """

    name: str = Field(description="实体名称（例如：振动异常、轴承损坏密封失效等）。")
    category: str = Field(description="类型：故障现象、根因、部件、解决方案。")
    description: Optional[str] = Field(
        None, description="描述（例如：表现为轴承温度升高、由于润滑不良导致）。"
    )


class FailureKnowledgeEdge(BaseModel):
    """
    故障知识超边，连接多个实体。
    """

    nodes: List[str] = Field(
        description="参与故障推理的节点列表：[故障现象1, 故障现象2, ..., 根因, 部件, 解决方案1, 解决方案2, ...]"
    )
    reasoning_type: str = Field(description="推理类型：故障诊断、原因分析、解决方案。")
    failure_description: Optional[str] = Field(None, description="故障详细描述。")


_NODE_PROMPT = """## 角色与任务
你是一位设备故障诊断专家，请从故障案例中提取所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的故障知识实体
- **边 (Edge)**：连接多个节点，表达故障现象、根因、解决方案的复杂关联

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别故障现象（振动异常、噪音、温度升高、泄漏、异响）
- 识别故障根因（润滑不良、过载、磨损、老化、设计缺陷）
- 识别故障部件（轴承、密封、电机、泵体、阀门）
- 识别解决方案（更换备件、调整参数、清洁、紧固）

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位设备故障诊断专家，请从已知实体列表中提取故障诊断推理作为超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的故障知识实体
- **边 (Edge)**：连接多个节点，表达故障现象、根因、解决方案的复杂关联

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 识别故障现象（振动异常、噪音、温度升高、泄漏、异响）
- 识别从现象到根因的推理
- 识别从根因到解决方案的推理
- 边的 nodes 字段应包含所有参与该故障推理的实体

"""

_PROMPT = """## 角色与任务
你是一位设备故障诊断专家，请从故障案例中提取故障知识实体和故障诊断推理作为超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的故障知识实体
- **边 (Edge)**：连接多个节点，表达故障现象、根因、解决方案的复杂关联

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体

### 领域特定规则
- 识别故障现象（振动异常、噪音、温度升高、泄漏、异响）
- 识别故障根因（润滑不良、过载、磨损、老化、设计缺陷）
- 识别故障部件（轴承、密封、电机、泵体、阀门）
- 识别解决方案（更换备件、调整参数、清洁、紧固）
- 建立从现象→根因→解决方案的完整推理链条

### 源文本:
"""


class FailureKnowledgeHypergraph(AutoHypergraph[FailureEntity, FailureKnowledgeEdge]):
    """
    适用文档: 故障案例库、设备故障分析报告、
    故障诊断手册。

    模板用于从故障案例中提取故障现象、根因、部件、解决方案
    的复杂关联关系，支持故障诊断和知识复用。

    使用示例:
        >>> failure = FailureKnowledgeHypergraph(llm_client=llm, embedder=embedder)
        >>> doc = "离心泵P-101出现振动异常，经检查发现轴承磨损严重..."
        >>> failure.feed_text(doc)
        >>> failure.show()
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
        初始化故障知识超图模板。

        Args:
            llm_client (BaseChatModel): 用于故障知识提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoHypergraph 的其他参数。
        """
        super().__init__(
            node_schema=FailureEntity,
            edge_schema=FailureKnowledgeEdge,
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
        使用 OntoSight 可视化故障知识超图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的故障推理数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的故障推理数。默认 3。
        """

        def node_label_extractor(node: FailureEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: FailureKnowledgeEdge) -> str:
            return edge.reasoning_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
