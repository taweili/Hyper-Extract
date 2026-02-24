"""历史人物关系图 - 提取基础的人物关系（亲属、君臣、敌友）及事件因果。

适用于历史专著、人物传记、断代史。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class HistoricalPersonNode(BaseModel):
    """历史人物节点"""
    name: str = Field(description="人物姓名")
    title: str = Field(description="身份或官职，如吴国大都督、刘备军师")
    faction: str = Field(description="所属阵营，如吴、蜀、魏")
    description: str = Field(description="人物简要描述，包括主要成就和特点", default="")


class PersonRelationEdge(BaseModel):
    """人物关系边"""
    source: str = Field(description="源人物姓名")
    target: str = Field(description="目标人物姓名")
    relationType: str = Field(description="关系类型：亲属、君臣、敌友、联盟、对手")
    description: str = Field(description="关系描述，描述两人之间的具体互动或关系详情")


_NODE_PROMPT = """## 角色与任务
你是一位专业的历史学专家，请从文本中提取所有历史人物作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的历史人物实体
- **边 (Edge)**：人物之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 同一人物在不同势力有不同官职时，以原文描述的主要官职为准
- 历史人物要包含所属阵营信息

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知人物列表中提取人物之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的历史人物实体
- **边 (Edge)**：人物之间的关系

## 提取规则
### 核心约束
1. 仅从已知人物列表中提取边，不要创建未列出的人物
2. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型：亲属、君臣、敌友、联盟、对手
- 详细描述两人之间的具体互动

"""

_PROMPT = """## 角色与任务
你是一位专业的历史学专家，请从文本中提取所有历史人物以及他们之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的历史人物实体
- **边 (Edge)**：人物之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知人物列表中提取边，不要创建未列出的人物
4. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型：亲属、君臣、敌友、联盟、对手
- 历史人物要包含所属阵营信息

### 源文本:
"""


class HistoricalKnowledgeGraph(AutoGraph[HistoricalPersonNode, PersonRelationEdge]):
    """
    适用文档: 历史专著、人物传记、断代史

    功能介绍:
    提取基础的人物关系（亲属、君臣、敌友）及事件因果，构建历史人物关系网络。

    设计说明:
    - 节点（HistoricalPersonNode）：存储人物信息，包括姓名、官职、阵营、描述
    - 边（PersonRelationEdge）：存储人物间的关系及描述

    Example:
        >>> template = HistoricalKnowledgeGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("赤壁之战中，周瑜率军大败曹操...")
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
        初始化历史人物关系图模板。

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
            node_schema=HistoricalPersonNode,
            edge_schema=PersonRelationEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
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
        展示历史人物关系图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: HistoricalPersonNode) -> str:
            return f"{node.name}({node.faction})"

        def edge_label_extractor(edge: PersonRelationEdge) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
