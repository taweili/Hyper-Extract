"""复杂人物关系网 - 超越两两关系，提取涉及多方的社会结构（如三角恋、结盟、家族派系）。

适用于长篇小说。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class CharacterNode(BaseModel):
    """小说人物节点"""
    name: str = Field(description="人物姓名")
    role: str = Field(description="角色定位：主角、配角、反派、酱油")
    faction: str = Field(description="所属阵营或派系", default="")
    description: str = Field(description="人物描述")


class RelationHyperedge(BaseModel):
    """复杂关系超边"""
    relationType: str = Field(description="关系类型：三角恋、结盟、敌对、背叛、竞争、家族")
    participants: List[str] = Field(description="参与方列表（3人或以上）")
    description: str = Field(description="关系描述")
    sourceScene: str = Field(description="来源情节", default="")


_NODE_PROMPT = """## 角色与任务
请从长篇小说文本中提取所有人物作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的人物
- **边 (Edge)**：连接多个节点的复杂关系超边

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 角色定位：主角、配角、反派、酱油
- 所属阵营：如"江左盟"、"太子党"、"誉王党"等

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知人物列表中提取复杂人物关系的超边结构。

## 核心概念定义
- **节点 (Node)**：从文档中提取的人物
- **边 (Edge)**：连接多个节点的复杂关系超边

## 提取规则
### 核心约束
1. 超边必须包含3个或以上参与者
2. 仅从已知人物列表中提取边，不要创建未列出的人物
3. 描述应与原文保持一致

### 领域特定规则
- 三角恋：涉及三人的爱情关系
- 结盟：多方形成的政治或军事联盟
- 敌对：多方之间的对立关系
- 背叛：一方背离原先的阵营或关系
- 竞争：多方争夺同一目标
- 家族：同一家族的成员关系

"""

_PROMPT = """## 角色与任务
你是一位专业的小说分析师，请从文本中提取人物以及它们之间的复杂关系超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的人物
- **边 (Edge)**：连接多个节点的复杂关系超边

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 超边必须包含3个或以上参与者
4. 仅从已知人物列表中提取边，不要创建未列出的人物
5. 描述应与原文保持一致

### 领域特定规则
- 角色定位：主角、配角、反派、酱油
- 所属阵营：如"江左盟"、"太子党"、"誉王党"等
- 关系类型：三角恋、结盟、敌对、背叛、竞争、家族

### 源文本:
"""


class ComplexCharacterRelation(AutoHypergraph[CharacterNode, RelationHyperedge]):
    """
    适用文档: 长篇小说

    功能介绍:
    超越两两关系，提取涉及多方的社会结构（如三角恋、结盟、家族派系）。

    设计说明:
    - 节点（CharacterNode）：存储人物信息，包括姓名、角色、阵营、描述
    - 边（RelationHyperedge）：存储复杂关系信息及各参与方

    Example:
        >>> template = ComplexCharacterRelation(llm_client=llm, embedder=embedder)
        >>> template.feed_text("梅长苏入京，太子与誉王...")
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
        初始化复杂人物关系网模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            chunk_size: 每个分块的最大字符数，默认为 512
            chunk_overlap: 分块之间的重叠字符数，默认为 64
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        def nodes_in_edge_extractor(edge: RelationHyperedge) -> set:
            return set(edge.participants)

        super().__init__(
            node_schema=CharacterNode,
            edge_schema=RelationHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.relationType}|{x.description[:20]}",
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
        展示复杂人物关系网。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: CharacterNode) -> str:
            return f"{node.name}[{node.role}]"

        def edge_label_extractor(edge: RelationHyperedge) -> str:
            return f"{edge.relationType}: {edge.description[:20]}..."

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
