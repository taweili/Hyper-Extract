"""故障案例图谱 - 提取故障现象、原因、措施和教训，识别从发现到处理的完整故障演进链条。

适用于故障案例库、事故分析报告、设备异常记录、检修报告等文本。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class CaseEntity(BaseModel):
    """故障案例实体，包括现象、原因、措施、教训等。"""

    name: str = Field(description="现象/措施等实体的名称。")
    category: str = Field(description="类别：现象、原因、措施、教训。")
    description: Optional[str] = Field(default=None, description="对该实体内涵的进一步阐述和说明。")
    equipment: Optional[str] = Field(default=None, description="涉及设备名称。")


class CaseChain(BaseModel):
    """故障案例环节之间的关联关系。"""

    source: str = Field(description="上游环节名称。")
    target: str = Field(description="下游环节名称。")
    relationType: str = Field(description="关系类型：导致、采取、产生、发现。")
    time_sequence: Optional[str] = Field(default=None, description="时序关系：发现、分析、处理、总结。")


_NODE_PROMPT = """## 角色与任务
你是一位工业设备故障分析专家，请从文本中提取所有相关实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括故障现象、故障原因、处理措施、经验教训等
- **边 (Edge)**：故障环节之间的关联关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别故障现象和异常表现
- 识别故障原因和根本原因
- 识别处理措施和解决方案
- 识别经验教训和改进建议
- 记录涉及的设备名称

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取故障环节之间的关联关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：故障环节之间的关联关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 识别从现象到原因的关联
- 识别从原因到措施的关联
- 识别从措施到教训的关联
- 时序关系：发现 → 分析 → 处理 → 总结

"""

_PROMPT = """## 角色与任务
你是一位工业设备故障分析专家，请从文本中提取故障现象、原因、处理措施和经验教训。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括故障现象、故障原因、处理措施、经验教训等
- **边 (Edge)**：故障环节之间的关联关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别故障现象和异常表现
- 分析故障原因和根本原因
- 提取处理措施和解决方案
- 总结经验教训和改进建议
- 建立从发现到处理的完整链条

### 源文本:
"""


class FailureCaseGraph(AutoGraph[CaseEntity, CaseChain]):
    """
    适用文档: 故障案例库、事故分析报告、设备异常记录、检修报告

    功能介绍:
    从故障案例文档中提取故障现象、原因、措施和教训，识别从发现到处理的完整故障演进链条。

    Example:
        >>> template = FailureCaseGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("2024年1月，A生产线主电机突发异响并伴随振动加剧。检查发现轴承磨损严重...")
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
        初始化故障案例图谱模板。

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
            node_schema=CaseEntity,
            edge_schema=CaseChain,
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
        展示故障案例图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: CaseEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: CaseChain) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
