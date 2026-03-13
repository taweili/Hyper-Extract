"""法律概念本体 - 提取法律术语的定义、上下位关系及法理阐释。

适用于法学专著、法律评注、法条解读等文本。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class LegalConceptNode(BaseModel):
    """法律概念节点"""
    name: str = Field(description="法律概念名称，如过错、故意、过失、违法性")
    category: str = Field(description="概念类型：原则、规则、学说、术语、法律依据")
    definition: Optional[str] = Field(description="概念的简要定义", default=None)


class LegalConceptRelationEdge(BaseModel):
    """法律概念关系边"""
    source: str = Field(description="源概念名称")
    target: str = Field(description="目标概念名称")
    relationType: str = Field(
        description="关系类型：上位概念、下位概念、相关联、对立、包含、依据"
    )
    description: Optional[str] = Field(description="关系描述", default=None)


_NODE_PROMPT = """## 角色与任务
你是一位专业的法学专家，请从文本中提取所有法律概念作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的法律概念
- **边 (Edge)**：概念之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的概念，禁止将多个概念合并为一个节点
2. 概念名称与原文保持一致

### 领域特定规则
- 法律概念类型包括：原则、规则、学说、术语、法律依据
- 常见的法律概念：过错、故意、过失、违法性、因果关系、举证责任等

## 法律文献文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知法律概念列表中提取概念之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的法律概念
- **边 (Edge)**：概念之间的关系

## 提取规则
### 核心约束
1. 仅从已知法律概念列表中提取边，不要创建未列出的概念
2. 关系描述应与原文保持一致

### 关系类型
- 上位概念：概念之间的层级包含关系
- 下位概念：概念之间的层级包含关系
- 相关联：概念之间存在逻辑关联
- 对立：概念之间存在对立关系
- 包含：一个概念包含另一个概念
- 依据：一个概念是另一个概念的依据

## 已知法律概念列表:
{known_nodes}

## 法律文献文本:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位专业的法学专家，请从文本中提取所有法律概念以及它们之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的法律概念
- **边 (Edge)**：概念之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的概念，禁止将多个概念合并为一个节点
2. 概念名称与原文保持一致
3. 仅从已知概念列表中提取边，不要创建未列出的概念
4. 关系描述应与原文保持一致

### 领域特定规则
- 法律概念类型包括：原则、规则、学说、术语、法律依据
- 关系类型：上位概念、下位概念、相关联、对立、包含、依据

## 法律文献文本:
{source_text}"""


class LegalConceptOntology(AutoGraph[LegalConceptNode, LegalConceptRelationEdge]):
    """
    适用文档: 法学专著、法律评注、法条解读、法学教材

    功能介绍:
    提取法律术语的定义、上下位关系及法理阐释，构建法律概念本体网络。
    支持法律检索增强、法学教育等应用场景。

    设计说明:
    - 节点（LegalConceptNode）：存储法律概念信息，包括名称、类型、定义
    - 边（LegalConceptRelationEdge）：存储概念间的关系及描述

    Example:
        >>> template = LegalConceptOntology(llm_client=llm, embedder=embedder)
        >>> template.feed_text("过错责任原则是民事侵权责任的核心归责原则...")
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
        初始化法律概念本体模板。

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
            node_schema=LegalConceptNode,
            edge_schema=LegalConceptRelationEdge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}|{x.relationType}|{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
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
        展示法律概念本体图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: LegalConceptNode) -> str:
            return f"{node.name}({node.category})"

        def edge_label_extractor(edge: LegalConceptRelationEdge) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
