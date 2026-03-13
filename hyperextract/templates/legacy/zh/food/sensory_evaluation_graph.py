"""感官评价图谱 - 提取 {菜品} -[具有特征]-> {口感/味道} -[归因于]-> {食材/技法} 的评价逻辑。

适用于风味归因分析、新品研发反馈。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class SensoryNode(BaseModel):
    """感官评价节点"""

    name: str = Field(description="节点名称")
    category: str = Field(description="节点类型：菜品/口感/味道/食材/技法")
    description: str = Field(description="简要描述", default="")


class SensoryEdge(BaseModel):
    """感官评价边"""

    source: str = Field(description="源节点")
    target: str = Field(description="目标节点")
    relation_type: str = Field(description="关系类型：具有特征/归因于")
    description: str = Field(description="详细描述")


_PROMPT = """## 角色与任务
你是一位专业的美食评论家，请从文本中提取感官评价图谱，包括菜品、口感/味道、食材/技法之间的归因关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型：具有特征（描述菜品具有某种口感/味道）、归因于（解释某种口感/味道的来源）
- 节点类型：菜品、口感、味道、食材、技法

## 源文本:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取所有感官评价相关的节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 节点类型：菜品、口感、味道、食材、技法
- 口感描述词：脆爽、鲜嫩、Q弹、绵密、软糯等
- 味道描述词：鲜香、麻辣、酸甜、醇厚、清爽等
- 技法描述词：腌制、烹煮、火候、刀工等

## 源文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从给定节点列表中提取感官评价边，构建评价逻辑图。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 每条边必须连接已提取的节点
3. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型：具有特征（描述菜品具有某种口感/味道）、归因于（解释某种口感/味道的来源）

## 已知实体列表:
{known_nodes}

## 源文本:
{source_text}
"""


class SensoryEvaluationGraph(AutoGraph[SensoryNode, SensoryEdge]):
    """
    适用文档: 美食评论、食评文章、风味分析报告

    功能介绍:
    提取 {菜品} -[具有特征]-> {口感/味道} -[归因于]-> {食材/技法} 的评价逻辑，适用于风味归因分析、新品研发反馈。

    Example:
        >>> template = SensoryEvaluationGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("红烧肉：肥而不腻，入口即化，这得益于五花肉的品质和慢火炖煮...")
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
        初始化感官评价图谱模板。

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
            node_schema=SensoryNode,
            edge_schema=SensoryEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relation_type}|{x.target}",
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
        展示感官评价图谱。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: SensoryNode) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: SensoryEdge) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
