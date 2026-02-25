"""故事实体图谱 - 专注于提取关键物品、地点及其归属或位置关系，与人物关系分离。

适用于长篇小说。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class StoryEntityNode(BaseModel):
    """故事实体节点"""
    name: str = Field(description="实体名称")
    category: str = Field(description="实体类型：物品、地点")
    description: str = Field(description="实体描述")


class BelongsToEdge(BaseModel):
    """归属关系边"""
    source: str = Field(description="物品")
    target: str = Field(description="归属者或位置")
    relationType: str = Field(description="关系类型：归属、位于")
    description: str = Field(description="描述")


_NODE_PROMPT = """## 角色与任务
请从长篇小说文本中提取所有故事实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的故事实体
- **边 (Edge)**：实体之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 物品：武器、书信、信物、药材等
- 地点：城市、建筑、区域等

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取实体之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的故事实体
- **边 (Edge)**：实体之间的关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 归属：物品的所有者或使用者
- 位于：物品的位置或地点的所在

"""

_PROMPT = """## 角色与任务
你是一位专业的小说分析师，请从文本中提取故事实体以及它们之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的故事实体
- **边 (Edge)**：实体之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 物品：武器、书信、信物、药材等
- 地点：城市、建筑、区域等
- 关系类型：归属（物品的所有者）、位于（物品的位置）

### 源文本:
"""


class StoryEntityGraph(AutoGraph[StoryEntityNode, BelongsToEdge]):
    """
    适用文档: 长篇小说

    功能介绍:
    专注于提取关键物品、地点及其归属或位置关系，与人物关系分离。

    设计说明:
    - 节点（StoryEntityNode）：存储故事实体信息，包括名称、类型、描述
    - 边（BelongsToEdge）：存储实体之间的归属或位置关系

    Example:
        >>> template = StoryEntityGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("梅长苏手中握着一枚金牌令...")
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
        初始化故事实体图谱模板。

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
            node_schema=StoryEntityNode,
            edge_schema=BelongsToEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
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
        展示故事实体图谱。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: StoryEntityNode) -> str:
            return f"{node.name}[{node.category}]"

        def edge_label_extractor(edge: BelongsToEdge) -> str:
            return f"{edge.relationType}: {edge.source} -> {edge.target}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
