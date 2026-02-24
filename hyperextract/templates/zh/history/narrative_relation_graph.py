"""叙事关系图 - 提取口述者主观视角下的人物互动与评价关系。

适用于口述历史、回忆录、个人日记。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class NarrativeCharacterNode(BaseModel):
    """叙事人物节点"""
    name: str = Field(description="人物姓名")
    description: str = Field(description="人物描述")
    perspective: str = Field(description="视角人物对该人物的评价或印象", default="")


class NarrativeInteractionEdge(BaseModel):
    """叙事关系边"""
    source: str = Field(description="源人物")
    target: str = Field(description="目标人物")
    interaction: str = Field(description="互动类型：评价、往来、合作、书信")
    content: str = Field(description="互动内容或评价具体描述")


_NODE_PROMPT = """## 角色与任务
请从文本中提取口述历史或回忆录中的人物作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的人物实体
- **边 (Edge)**：人物之间的互动与评价关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 人物要包含描述信息
- 视角人物的评价或印象要记录

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知人物列表中提取人物之间的互动与评价关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的人物实体
- **边 (Edge)**：人物之间的互动与评价关系

## 提取规则
### 核心约束
1. 仅从已知人物列表中提取边，不要创建未列出的人物
2. 关系描述应与原文保持一致

### 领域特定规则
- 互动类型：评价、往来、合作、书信
- 内容要具体描述互动或评价

"""

_PROMPT = """## 角色与任务
你是一位专业的历史学专家，请从文本中提取口述历史或回忆录中的人物以及他们之间的互动与评价关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的人物实体
- **边 (Edge)**：人物之间的互动与评价关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知人物列表中提取边，不要创建未列出的人物
4. 关系描述应与原文保持一致

### 领域特定规则
- 人物要包含描述信息
- 视角人物的评价或印象要记录
- 互动类型：评价、往来、合作、书信
- 内容要具体描述互动或评价

### 源文本:
"""


class NarrativeRelationGraph(AutoGraph[NarrativeCharacterNode, NarrativeInteractionEdge]):
    """
    适用文档: 口述历史、回忆录、个人日记

    功能介绍:
    提取口述者主观视角下的人物互动与评价关系，适用于口述史社会网络分析。

    设计说明:
    - 节点（NarrativeCharacterNode）：存储人物信息及视角人物的评价
    - 边（NarrativeInteractionEdge）：存储人物间的互动内容

    Example:
        >>> template = NarrativeRelationGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("苏轼在信中评价黄庭坚的书法...")
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
        初始化叙事关系图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            chunk_size: 每个分块的最大字符数，默认为 512（历史文本信息量大，需较小分块）
            chunk_overlap: 分块之间的重叠字符数，默认为 64
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=NarrativeCharacterNode,
            edge_schema=NarrativeInteractionEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.interaction}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
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
        展示叙事关系图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: NarrativeCharacterNode) -> str:
            return node.name

        def edge_label_extractor(edge: NarrativeInteractionEdge) -> str:
            return edge.interaction

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
