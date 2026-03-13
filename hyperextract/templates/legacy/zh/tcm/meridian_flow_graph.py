"""经络流注图 - 提取十二经脉的循行路线及经气流注次序。

适用于经络理论教学。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class MeridianNode(BaseModel):
    """经脉节点"""

    name: str = Field(description="经脉名称：如手太阴肺经、手阳明大肠经等")
    category: str = Field(description="经脉类别：阴经、阳经")
    associatedOrgan: str = Field(description="关联脏腑", default="")
    circulationPath: str = Field(description="循行路线", default="")


class MeridianFlowRelation(BaseModel):
    """经络流注关系边"""

    source: str = Field(description="源经脉名称")
    target: str = Field(description="目标经脉名称")
    relationType: str = Field(description="关系类型：流注")
    flowOrder: int = Field(description="流注次序")
    connectionPoint: str = Field(description="连接部位", default="")


_PROMPT = """## 角色与任务
你是一位专业的经络学专家，请从文本中提取十二经脉的循行路线及经气流注次序。

## 核心概念定义
- **节点 (Node)**：经脉实体
- **边 (Edge)**：经脉之间的流注关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 经脉：十二经脉，如手太阴肺经、手阳明大肠经
- 经脉类别：阴经、阳经

## 经络文献:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取经脉实体作为节点。

## 核心概念定义
- **节点 (Node)**：经脉实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 经脉：十二经脉
- 经脉类别：阴经、阳经

## 经络文献:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知经脉列表中提取经脉之间的流注关系。

## 核心概念定义
- **边 (Edge)**：经脉之间的流注关系

## 提取规则
### 核心约束
1. 仅从已知经脉列表中提取边，不要创建未列出的经脉
2. 关系描述应与原文保持一致

## 已知经脉节点列表:
{known_nodes}

## 经络文献:
{source_text}
"""


class MeridianFlowGraph(AutoGraph[MeridianNode, MeridianFlowRelation]):
    """
    适用文档: 黄帝内经、经络学教材、针灸学教材等

    功能介绍:
    提取十二经脉的循行路线及经气流注次序，适用于经络理论教学。

    Example:
        >>> template = MeridianFlowGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("手太阴肺经起于中焦，下络大肠...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化经络流注图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            chunk_size: 每个分块的最大字符数，默认为 512（中医文本信息量大，需较小分块）
            chunk_overlap: 分块之间的重叠字符数，默认为 64
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=MeridianNode,
            edge_schema=MeridianFlowRelation,
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
        展示经络流注图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: MeridianNode) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: MeridianFlowRelation) -> str:
            return f"流注 #{edge.flowOrder}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
