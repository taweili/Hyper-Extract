"""个人轨迹超图 - 以人生阶段为超边，关联时期、地点、同行人物、核心经历。

适用于口述历史、人物传记、回忆录。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class PersonNode(BaseModel):
    """人物节点"""
    name: str = Field(description="人物姓名")
    description: str = Field(description="人物描述")


class LifePhaseHyperedge(BaseModel):
    """人生阶段超边"""
    phase: str = Field(description="人生阶段，如进士及第、被贬黄州、任翰林学士")
    time: str = Field(description="时期")
    location: str = Field(description="地点")
    companions: List[str] = Field(description="同行或交往人物", default_factory=list)
    experiences: List[str] = Field(description="核心经历列表", default_factory=list)
    description: str = Field(description="阶段描述")


_NODE_PROMPT = """## 角色与任务
请从文本中提取人物传记中的主要人物作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的人物实体
- **边 (Edge)**：连接人物的人生阶段超边

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 主要人物：传记主角及其重要交往对象
- 人物要包含描述信息

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知人物列表中提取人物的人生阶段超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的人物实体
- **边 (Edge)**：连接人物的人生阶段超边

## 提取规则
### 核心约束
1. 超边必须关联一个主要人物
2. 仅从已知人物列表中提取边，不要创建未列出的人物
3. 关系描述应与原文保持一致

### 领域特定规则
- 人生阶段：如进士及第、被贬黄州、任翰林学士等
- 同行人物：该阶段与主角有交往的人
- 核心经历：该阶段的重要事件

"""

_PROMPT = """## 角色与任务
你是一位专业的历史学专家，请从文本中提取人物传记中的人物以及他们的人生阶段超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的人物实体
- **边 (Edge)**：连接人物的人生阶段超边

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 超边必须关联一个主要人物
4. 仅从已知人物列表中提取边，不要创建未列出的人物
5. 关系描述应与原文保持一致

### 领域特定规则
- 主要人物：传记主角及其重要交往对象
- 人生阶段：如进士及第、被贬黄州、任翰林学士等
- 同行人物：该阶段与主角有交往的人
- 核心经历：该阶段的重要事件

### 源文本:
"""


class PersonalTrajectoryHypergraph(AutoHypergraph[PersonNode, LifePhaseHyperedge]):
    """
    适用文档: 口述历史、人物传记、回忆录

    功能介绍:
    以人生阶段为超边，关联 {时期, 地点, 同行人物, 核心经历}，适用于人物传记编撰、生命历程研究。

    设计说明:
    - 节点（PersonNode）：存储人物信息
    - 边（LifePhaseHyperedge）：存储人生阶段信息及关联人物

    Example:
        >>> template = PersonalTrajectoryHypergraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("苏轼于元丰二年被贬黄州...")
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
        初始化个人轨迹超图模板。

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
        def nodes_in_edge_extractor(edge: LifePhaseHyperedge) -> set:
            return set(edge.companions)

        super().__init__(
            node_schema=PersonNode,
            edge_schema=LifePhaseHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.phase}|{x.time}",
            nodes_in_edge_extractor=nodes_in_edge_extractor,
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
        展示个人轨迹超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: PersonNode) -> str:
            return node.name

        def edge_label_extractor(edge: LifePhaseHyperedge) -> str:
            return f"{edge.phase}({edge.time})"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
