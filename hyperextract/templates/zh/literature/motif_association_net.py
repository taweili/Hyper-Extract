"""意象关联网络 - 提取文本中反复出现的符号、意象之间的关联，节点类型统一为"意象"。

适用于文学评论。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class MotifNode(BaseModel):
    """意象节点"""
    name: str = Field(description="意象名称")
    description: str = Field(description="意象描述")


class MotifEdge(BaseModel):
    """意象关联边"""
    source: str = Field(description="源意象")
    target: str = Field(description="目标意象")
    associationType: str = Field(description="关联类型：对比、递进、因果、象征、配套")
    description: str = Field(description="关联描述")


_NODE_PROMPT = """## 角色与任务
请从文学评论文本中提取所有意象作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的意象
- **边 (Edge)**：意象之间的关联关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的意象，禁止将多个意象合并为一个节点
2. 意象名称与原文保持一致

### 领域特定规则
- 意象：反复出现的符号、象征物、自然元素等

## 文学评论文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知意象列表中提取意象之间的关联关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的意象
- **边 (Edge)**：意象之间的关联关系

## 提取规则
### 核心约束
1. 仅从已知意象列表中提取边，不要创建未列出的意象
2. 关系描述应与原文保持一致

### 领域特定规则
- 对比：两个意象形成对照或反衬
- 递进：一个意象引出另一个意象
- 因果：一个意象导致另一个意象出现
- 象征：一个意象代表另一个含义
- 配套：多个意象共同构成一个意象群

## 已知意象列表:
{known_nodes}

## 文学评论文本:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位专业的文学评论家，请从文本中提取意象以及它们之间的关联关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的意象
- **边 (Edge)**：意象之间的关联关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的意象，禁止将多个意象合并为一个节点
2. 意象名称与原文保持一致
3. 仅从已知意象列表中提取边，不要创建未列出的意象
4. 关系描述应与原文保持一致

### 领域特定规则
- 意象：反复出现的符号、象征物、自然元素等
- 关联类型：对比、递进、因果、象征、配套

## 文学评论文本:
{source_text}
"""


class MotifAssociationNet(AutoGraph[MotifNode, MotifEdge]):
    """
    适用文档: 文学评论

    功能介绍:
    提取文本中反复出现的符号、意象之间的关联，节点类型统一为"意象"。

    设计说明:
    - 节点（MotifNode）：存储意象信息，包括名称、描述
    - 边（MotifEdge）：存储意象之间的关联关系

    Example:
        >>> template = MotifAssociationNet(llm_client=llm, embedder=embedder)
        >>> template.feed_text("梅花在剧中多次出现，象征...")
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
        初始化意象关联网络模板。

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
            node_schema=MotifNode,
            edge_schema=MotifEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.associationType}|{x.target}",
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
        展示意象关联网络。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: MotifNode) -> str:
            return node.name

        def edge_label_extractor(edge: MotifEdge) -> str:
            return f"{edge.associationType}: {edge.source} -> {edge.target}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
