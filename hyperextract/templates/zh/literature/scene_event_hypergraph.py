"""场景事件超图 - 将一场戏建模为连接 {出场角色, 场景地点, 关键道具, 核心动作} 的超边。

适用于影视剧本（场景头、动作、对白格式）。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class SceneNode(BaseModel):
    """场景元素节点"""
    name: str = Field(description="元素名称")
    category: str = Field(description="元素类型：角色、地点、道具、动作")
    description: str = Field(description="简要描述")


class SceneHyperedge(BaseModel):
    """场景事件超边"""
    sceneName: str = Field(description="场景名称，如'第一场：桐花台夜话'")
    characters: List[str] = Field(description="出场角色列表")
    location: str = Field(description="场景地点")
    props: List[str] = Field(description="关键道具列表", default_factory=list)
    actions: List[str] = Field(description="核心动作列表")
    timeOfDay: str = Field(description="时间段：日/夜/晨/昏")


_NODE_PROMPT = """## 角色与任务
请从影视剧本文本中提取所有场景元素作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的场景元素，包括角色、地点、道具、动作
- **边 (Edge)**：连接多个节点的超边，表示一场完整的戏

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 角色：从【动作】或对白中识别的人物
- 地点：从场景头中提取，如"碎玉轩"、"桐花台"
- 道具：从动作描述中提取的关键物品，如"油纸伞"、"宫灯"
- 动作：从动作描述中提取的核心行为，如"起舞"、"吟诵"

## 影视剧本文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知场景元素列表中提取场景事件的超边结构。

## 核心概念定义
- **节点 (Node)**：从文档中提取的场景元素
- **边 (Edge)**：连接多个节点的超边，表示一场完整的戏

## 提取规则
### 核心约束
1. 超边必须包含至少一个角色
2. 超边必须包含地点
3. 仅从已知场景元素列表中提取边，不要创建未列出的元素
4. 描述应与原文保持一致

### 领域特定规则
- 出场角色：从剧本对白和动作中识别的参与人物
- 场景地点：场景头中标注的地点
- 关键道具：动作描述中出现的物品
- 核心动作：角色完成的主要行为
- 时间段：从场景头中提取，如"日"、"夜"、"晨"、"昏"

## 已知场景元素列表:
{known_nodes}

## 影视剧本文本:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位专业的影视剧本分析师，请从文本中提取场景元素以及它们组成的场景事件超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的场景元素，包括角色、地点、道具、动作
- **边 (Edge)**：连接多个节点的超边，表示一场完整的戏

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 超边必须包含至少一个角色和地点
4. 仅从已知场景元素列表中提取边，不要创建未列出的元素
5. 描述应与原文保持一致

### 领域特定规则
- 角色：从【动作】或对白中识别的人物
- 地点：从场景头中提取，如"碎玉轩"、"桐花台"
- 道具：从动作描述中提取的关键物品，如"油纸伞"、"宫灯"
- 动作：从动作描述中提取的核心行为
- 时间段：从场景头中提取，如"日"、"夜"、"晨"、"昏"

## 影视剧本文本:
{source_text}
"""


class SceneEventHypergraph(AutoHypergraph[SceneNode, SceneHyperedge]):
    """
    适用文档: 影视剧本（场景头、动作、对白格式）

    功能介绍:
    将一场戏建模为连接 {出场角色, 场景地点, 关键道具, 核心动作} 的超边。

    设计说明:
    - 节点（SceneNode）：存储场景元素信息，包括名称、类型、描述
    - 边（SceneHyperedge）：存储场景事件信息及各元素

    Example:
        >>> template = SceneEventHypergraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("【场景一：桐花台 - 夜】甄嬛...")
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
        初始化场景事件超图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        def nodes_in_edge_extractor(edge: SceneHyperedge) -> set:
            nodes = set()
            nodes.update(edge.characters)
            nodes.add(edge.location)
            nodes.update(edge.props)
            nodes.update(edge.actions)
            return nodes

        super().__init__(
            node_schema=SceneNode,
            edge_schema=SceneHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.sceneName,
            nodes_in_edge_extractor=nodes_in_edge_extractor,
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
        展示场景事件超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: SceneNode) -> str:
            return f"{node.name}[{node.category}]"

        def edge_label_extractor(edge: SceneHyperedge) -> str:
            return f"{edge.sceneName}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
