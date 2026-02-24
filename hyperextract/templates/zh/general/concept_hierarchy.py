"""概念层级图 - 构建上下位关系或组成关系。

适用于科学学科、教材知识点等。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class ConceptNode(BaseModel):
    """概念节点"""

    name: str = Field(description="概念名称")
    category: str = Field(description="概念类型：核心概念、子概念、属性、实例、其他")
    description: str = Field(description="概念简要描述", default="")


class HierarchyRelation(BaseModel):
    """层级关系边"""

    source: str = Field(description="父概念/整体概念")
    target: str = Field(description="子概念/部分概念")
    relationType: str = Field(
        description="关系类型：上下位（Subclass-Of）、组成（Part-Of）、实例（Instance-Of）、其他（Other）"
    )
    details: str = Field(description="关系详细说明", default="")


_PROMPT = """## 角色与任务
你是一位专业的概念结构分析专家，请从文本中提取概念及其层级关系。

## 核心概念定义
- **节点 (Node)**：概念单元
- **边 (Edge)**：概念之间的层级关系

## 提取规则
### 节点提取规则
1. 提取所有概念
2. 为每个概念指定类型

### 关系提取规则
1. 仅从提取的概念中创建边
2. 每条边必须连接已提取的节点

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取概念作为节点。

## 核心概念定义
- **节点 (Node)**：概念单元

## 提取规则
1. 提取所有概念
2. 为每个概念指定类型

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知概念列表中提取概念之间的层级关系。

## 核心概念定义
- **边 (Edge)**：概念之间的层级关系

## 约束条件
1. 仅从已知概念列表中提取边
2. 不要创建未列出的概念

"""


class ConceptHierarchy(AutoGraph[ConceptNode, HierarchyRelation]):
    """
    适用文档: 科学学科教材、知识库文档、分类体系说明

    功能介绍:
    构建上下位关系或组成关系。适用于科学学科、教材知识点等。

    Example:
        >>> template = ConceptHierarchy(llm_client=llm, embedder=embedder)
        >>> template.feed_text("机器学习是人工智能的一个分支...")
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
        初始化概念层级图模板。

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
            node_schema=ConceptNode,
            edge_schema=HierarchyRelation,
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
        展示概念层级图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: ConceptNode) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: HierarchyRelation) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
