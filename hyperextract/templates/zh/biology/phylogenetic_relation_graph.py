"""系统发育关系图 - 从进化生物学文献中提取物种亲缘关系和演化分支信息。

适用于分子系统学文献、进化生物学研究。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class PhylogeneticNode(BaseModel):
    """系统发育节点"""
    name: str = Field(description="物种或分类单元名称")
    taxon_level: str = Field(description="分类水平：界、门、纲、目、科、属、种")
    description: str = Field(description="简要描述，包含演化位置或特征", default="")


class PhylogeneticRelation(BaseModel):
    """系统发育关系边"""
    source: str = Field(description="源物种或分类单元")
    target: str = Field(description="目标物种或分类单元")
    relation_type: str = Field(description="关系类型：亲缘关系、演化距离、分支、姐妹群")
    evolutionary_distance: str = Field(description="演化距离或分支时间估算", default="")
    branch_point: str = Field(description="分支点信息，如共同的祖先年代", default="")
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的进化生物学专家，请从“生物学文献”中提取物种或分类单元及其系统发育关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的物种或分类单元实体
- **边 (Edge)**：物种之间的系统发育关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的物种或分类单元，禁止将其合并为一个节点
2. 物种名称与原文保持一致

### 边提取约束
1. 边只能连接已提取的物种或分类单元节点
2. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型：亲缘关系、演化距离、分支、姐妹群
- 演化距离可用分支时间（百万年）或序列差异度表示
- 分支点信息包括共同的祖先和分化时间

## 生物学文献:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的进化生物学专家，请从“生物学文献”中提取所有物种或分类单元作为系统发育节点。


## 核心概念定义
- **节点 (Node)**：从文档中提取的物种或分类单元实体
- **边 (Edge)**：物种之间的系统发育关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的物种或分类单元，禁止将其合并为一个节点
2. 物种名称与原文保持一致

### 领域特定规则
- 分类等级：界(kingdom)、门(phylum)、纲(class)、目(order)、科(family)、属(genus)、种(species)
- 系统发育关系包括：亲缘关系、演化距离、分支、姐妹群关系

### 生物学文献:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从“生物学文献”中提取它们之间的系统发育关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的物种或分类单元实体
- **边 (Edge)**：物种之间的系统发育关系

## 提取规则
### 核心约束
1. 仅从已知的实体中提取边，不要创建未列出的物种
2. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型：亲缘关系、演化距离、分支、姐妹群
- 演化距离可用分支时间（百万年）或序列差异度表示
- 分支点信息包括共同的祖先和分化时间

## 已知物种或分类单元实体:
{known_entities}

## 生物学文献:
{source_text}
"""


class PhylogeneticRelationGraph(AutoGraph[PhylogeneticNode, PhylogeneticRelation]):
    """
    适用文档: 分子系统学文献、进化生物学研究、分子系统发育树描述

    功能介绍:
    提取物种间的亲缘关系、演化距离及分支点，构建系统发育关系网络。
    适用于分子系统学、进化树构建和生物多样性演化研究。

    Example:
        >>> template = PhylogeneticRelationGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("鱼类最早分出，随后是两栖类，鸟类和哺乳动物属于羊膜动物...")
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
        初始化系统发育关系图模板。

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
            node_schema=PhylogeneticNode,
            edge_schema=PhylogeneticRelation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relation_type}|{x.target}",
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
        展示系统发育关系图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: PhylogeneticNode) -> str:
            return f"{node.name} ({node.taxon_level})"

        def edge_label_extractor(edge: PhylogeneticRelation) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
