"""历史背景关联图 - 提取事件背后的人物关系、地缘政治等静态关联。

适用于编年史、历史背景分析、事件深层原因分析。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class ContextEntityNode(BaseModel):
    """历史背景实体节点"""
    name: str = Field(description="实体名称")
    category: str = Field(description="类型：地理、政治、经济、军事、文化")
    description: str = Field(description="实体描述，包括位置、作用、意义等")


class ContextRelationEdge(BaseModel):
    """历史背景关系边"""
    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    relationType: str = Field(description="关系类型：包含、影响、对抗、支撑")
    description: str = Field(description="关系描述")


_NODE_PROMPT = """## 角色与任务
请从文本中提取历史背景相关的实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的历史背景实体
- **边 (Edge)**：实体之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 实体类型：地理、政治、经济、军事、文化
- 实体要包含描述信息

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取实体之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的历史背景实体
- **边 (Edge)**：实体之间的关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型：包含、影响、对抗、支撑

"""

_PROMPT = """## 角色与任务
你是一位专业的历史学专家，请从文本中提取历史背景相关的实体以及它们之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的历史背景实体
- **边 (Edge)**：实体之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 实体类型：地理、政治、经济、军事、文化
- 关系类型：包含、影响、对抗、支撑

### 源文本:
"""


class HistoricalContextGraph(AutoGraph[ContextEntityNode, ContextRelationEdge]):
    """
    适用文档: 编年史、历史背景分析、事件深层原因分析

    功能介绍:
    提取事件背后的人物关系、地缘政治、经济基础、文化背景等静态关联。

    设计说明:
    - 节点（ContextEntityNode）：存储背景实体信息，包括名称、类型、描述
    - 边（ContextRelationEdge）：存储实体之间的关系

    Example:
        >>> template = HistoricalContextGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("赤壁之战的背景是曹操统一北方后意图南下...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化历史背景关联图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=ContextEntityNode,
            edge_schema=ContextRelationEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
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
        展示历史背景关联图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: ContextEntityNode) -> str:
            return f"{node.name}[{node.category}]"

        def edge_label_extractor(edge: ContextRelationEdge) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
