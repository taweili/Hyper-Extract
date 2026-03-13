"""政治博弈超图 - 针对战役或政争，提取攻方、守方、策划者、变节者的复杂互动。

适用于战役记录、政治斗争史、权力更迭档案。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class PoliticalActorNode(BaseModel):
    """政治博弈参与者节点"""
    name: str = Field(description="人物姓名")
    role: str = Field(description="角色定位：攻方、守方、策划者、变节者、调解者")
    faction: str = Field(description="所属阵营", default="")
    description: str = Field(description="人物描述")


class StruggleHyperedge(BaseModel):
    """政治博弈事件超边"""
    eventName: str = Field(description="事件名称")
    attackers: List[str] = Field(description="攻方列表")
    defenders: List[str] = Field(description="守方列表")
    planners: List[str] = Field(description="策划者列表", default_factory=list)
    turncoats: List[str] = Field(description="变节者列表", default_factory=list)
    time: str = Field(description="时间")
    location: str = Field(description="地点")
    outcome: str = Field(description="结果描述")


_NODE_PROMPT = """## 角色与任务
请从文本中提取政治博弈或战役中的人物作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的政治博弈参与者
- **边 (Edge)**：连接多个参与者的超边，表示一个完整的博弈事件

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 角色定位：攻方、守方、策划者、变节者、调解者
- 参与者要标注所属阵营

## 源文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知人物列表中提取政治博弈或战役的超边结构。

## 核心概念定义
- **节点 (Node)**：从文档中提取的政治博弈参与者
- **边 (Edge)**：连接多个参与者的超边，表示一个完整的博弈事件

## 提取规则
### 核心约束
1. 超边必须包含攻方和守方
2. 仅从已知人物列表中提取边，不要创建未列出的人物
3. 关系描述应与原文保持一致

### 领域特定规则
- 攻方：主动发起进攻或挑战的一方
- 守方：被动防守或应战的一方
- 策划者：幕后策划或出谋划策的人
- 变节者：中途倒戈或背叛的人

## 已知人物列表:
{known_nodes}

## 源文本:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位专业的历史学专家，请从文本中提取政治博弈或战役中的人物以及他们组成的博弈事件超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的政治博弈参与者
- **边 (Edge)**：连接多个参与者的超边，表示一个完整的博弈事件

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 超边必须包含攻方和守方
4. 仅从已知人物列表中提取边，不要创建未列出的人物
5. 关系描述应与原文保持一致

### 领域特定规则
- 角色定位：攻方、守方、策划者、变节者、调解者
- 参与者要标注所属阵营
- 攻方：主动发起进攻或挑战的一方
- 守方：被动防守或应战的一方
- 策划者：幕后策划或出谋划策的人
- 变节者：中途倒戈或背叛的人

## 源文本:
{source_text}
"""


class PoliticalStruggleHypergraph(AutoHypergraph[PoliticalActorNode, StruggleHyperedge]):
    """
    适用文档: 战役记录、政治斗争史、权力更迭档案

    功能介绍:
    针对战役或政争，提取 {攻方, 守方, 策划者, 变节者} 的复杂互动结构。

    设计说明:
    - 节点（PoliticalActorNode）：存储参与者信息，包括姓名、角色、阵营、描述
    - 边（StruggleHyperedge）：存储博弈事件信息及各方参与者

    Example:
        >>> template = PoliticalStruggleHypergraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("赤壁之战中，周瑜率吴军火攻曹操...")
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
        初始化政治博弈超图模板。

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
        def nodes_in_edge_extractor(edge: StruggleHyperedge) -> set:
            nodes = set()
            nodes.update(edge.attackers)
            nodes.update(edge.defenders)
            nodes.update(edge.planners)
            nodes.update(edge.turncoats)
            return nodes

        super().__init__(
            node_schema=PoliticalActorNode,
            edge_schema=StruggleHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.eventName,
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
        展示政治博弈超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: PoliticalActorNode) -> str:
            return f"{node.name}[{node.role}]"

        def edge_label_extractor(edge: StruggleHyperedge) -> str:
            return f"{edge.eventName}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
