"""应急预案图谱 - 提取事故场景、响应动作和部门，构建应急响应流程，识别应急响应的流程和责任分工。

适用于应急预案、应急处置方案、安全规程等文本。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class EmergencyEntity(BaseModel):
    """应急预案实体，包括事故场景、响应动作、部门等。"""

    name: str = Field(description="实体名称（如：火灾、停电、报警、疏散人员、设备部等）。")
    category: str = Field(description="类别：事故场景、响应动作、部门。")
    description: Optional[str] = Field(default=None, description="对该实体的描述。")


class ResponseFlow(BaseModel):
    """应急响应流程关系。"""

    source: str = Field(description="源实体名称（事故场景或响应动作）。")
    target: str = Field(description="目标实体名称（响应动作或部门）。")
    relationType: str = Field(description="关系类型：触发、执行、负责。")
    time_limit: Optional[str] = Field(default=None, description="响应时间要求（如：5分钟内、10分钟内）。")
    success_criterion: Optional[str] = Field(default=None, description="成功标准（如：人员安全撤离、火势控制）。")


_NODE_PROMPT = """## 角色与任务
你是一位工业应急管理分析专家，请从文本中提取所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括事故场景（如火灾、泄漏）、响应动作（如报警、疏散）、负责部门（如安保部、设备部）
- **边 (Edge)**：应急响应流程关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别事故场景名称（如火灾、泄漏、停电、设备故障）
- 识别响应动作名称（如报警、疏散人员、关闭电源）
- 识别负责部门名称（如安保部、设备部、急救部）
- 为每个实体指定类别（事故场景/响应动作/部门）

## 事故应急预案:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取应急响应流程关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：应急响应流程关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 识别从事故场景到响应动作的关联
- 识别从响应动作到负责部门的关联
- 记录响应时间要求
- 记录成功标准

## 已知实体列表:
{known_nodes}

## 事故应急预案:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位工业应急管理分析专家，请从文本中提取事故场景、响应动作和部门，构建应急响应流程。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括事故场景（如火灾、泄漏）、响应动作（如报警、疏散）、负责部门（如安保部、设备部）
- **边 (Edge)**：应急响应流程关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别事故场景（如火灾、泄漏、停电、设备故障、人员受伤等）
- 识别响应动作（如报警、疏散人员、关闭电源等）
- 识别负责部门（如安保部、设备部、急救部、后勤部等）
- 建立从事故场景到响应动作的流程关系
- 记录时间要求和成功标准

## 事故应急预案:
{source_text}
"""


class EmergencyResponseGraph(AutoGraph[EmergencyEntity, ResponseFlow]):
    """
    适用文档: 应急预案、应急处置方案、安全规程

    功能介绍:
    从应急预案中提取事故场景、响应动作和部门，构建应急响应流程，识别应急响应的流程和责任分工。

    Example:
        >>> template = EmergencyResponseGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("发生火灾时，应立即报警并启动应急预案。安保部负责疏散人员，设备部负责关闭电源...")
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
        初始化应急预案图谱模板。

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
            node_schema=EmergencyEntity,
            edge_schema=ResponseFlow,
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
        展示应急预案图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: EmergencyEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: ResponseFlow) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
