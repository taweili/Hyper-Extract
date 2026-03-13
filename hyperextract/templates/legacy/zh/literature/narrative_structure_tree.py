"""叙事结构树 - 构建作品的结构层级（如主线、支线、插叙部分）。

适用于文学评论。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class StructureNode(BaseModel):
    """叙事结构节点"""
    name: str = Field(description="结构单元名称")
    category: str = Field(description="类型：主线、支线、插叙、前提、结局")
    description: str = Field(description="描述")


class StructureEdge(BaseModel):
    """结构层级边"""
    source: str = Field(description="上位结构")
    target: str = Field(description="下位结构")
    relationType: str = Field(description="关系类型：包含、从属、展开、转折")
    description: str = Field(description="描述")


_NODE_PROMPT = """## 角色与任务
请从文学评论文本中提取所有叙事结构单元作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的叙事结构单元
- **边 (Edge)**：结构单元之间的层级关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的结构单元，禁止将多个单元合并为一个节点
2. 单元名称与原文保持一致

### 领域特定规则
- 主线：推动故事核心发展的情节线
- 支线：辅助主线或展现次要人物的情节线
- 插叙：中断主线叙事的回忆或补充说明
- 前提：故事发生的背景设定
- 结局：故事的最终走向和结果

## 文学评论文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知结构单元列表中提取结构单元之间的层级关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的叙事结构单元
- **边 (Edge)**：结构单元之间的层级关系

## 提取规则
### 核心约束
1. 仅从已知结构单元列表中提取边，不要创建未列出的单元
2. 关系描述应与原文保持一致

### 领域特定规则
- 包含：上位结构包含下位结构
- 从属：下位结构从属于上位结构
- 展开：上位结构展开为下位结构
- 转折：从一线转到另一线

## 已知结构单元列表:
{known_nodes}

## 文学评论文本:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位专业的文学评论家，请从文本中提取叙事结构单元以及它们之间的层级关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的叙事结构单元
- **边 (Edge)**：结构单元之间的层级关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的结构单元，禁止将多个单元合并为一个节点
2. 单元名称与原文保持一致
3. 仅从已知结构单元列表中提取边，不要创建未列出的单元
4. 关系描述应与原文保持一致

### 领域特定规则
- 主线：推动故事核心发展的情节线
- 支线：辅助主线或展现次要人物的情节线
- 插叙：中断主线叙事的回忆或补充说明
- 前提：故事发生的背景设定
- 结局：故事的最终走向和结果
- 包含：上位结构包含下位结构
- 从属：下位结构从属于上位结构
- 展开：上位结构展开为下位结构
- 转折：从一线转到另一线

## 文学评论文本:
{source_text}
"""


class NarrativeStructureTree(AutoGraph[StructureNode, StructureEdge]):
    """
    适用文档: 文学评论

    功能介绍:
    构建作品的结构层级（如主线、支线、插叙部分）。

    设计说明:
    - 节点（StructureNode）：存储叙事结构单元信息，包括名称、类型、描述
    - 边（StructureEdge）：存储结构单元之间的层级关系

    Example:
        >>> template = NarrativeStructureTree(llm_client=llm, embedder=embedder)
        >>> template.feed_text("甄嬛从入宫到成为太后构成主线...")
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
        初始化叙事结构树模板。

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
            node_schema=StructureNode,
            edge_schema=StructureEdge,
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
        展示叙事结构树。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: StructureNode) -> str:
            return f"{node.name}[{node.category}]"

        def edge_label_extractor(edge: StructureEdge) -> str:
            return f"{edge.relationType}: {edge.source} -> {edge.target}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
