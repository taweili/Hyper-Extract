"""分类学树 - 从生物学文献中提取生物分类层级包含关系。

适用于生物学专著、分类学文献、物种描述。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class TaxonomicNode(BaseModel):
    """分类单元节点"""
    name: str = Field(description="分类单元名称，如绿藻门、鲤科、鲢鱼")
    rank: str = Field(description="分类等级：界、门、纲、目、科、属、种")
    latin_name: str = Field(description="拉丁学名", default="")


class TaxonomicRelation(BaseModel):
    """分类关系边"""
    source: str = Field(description="源分类单元（较高等级，如门）")
    target: str = Field(description="目标分类单元（较低等级，如种）")
    relation_type: str = Field(description="关系类型：包含于")
    details: str = Field(description="详细描述，包含具体的分类路径信息", default="")


_PROMPT = """## 角色与任务
你是一位专业的生物分类学专家，请从文本中提取分类单元及其层级包含关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的分类单元实体
- **边 (Edge)**：分类单元之间的层级包含关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的分类单元，禁止将多个分类单元合并为一个节点
2. 物种名称与原文保持一致

### 边提取约束
1. 边只能连接已提取的分类单元节点
2. 分类关系是层级包含关系，从高等级指向低等级

### 领域特定规则
- 分类等级：界(kingdom)、门(phylum)、纲(class)、目(order)、科(family)、属(genus)、种(species)
- 拉丁学名保持原文格式
- 关系类型统一为"包含于"

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的生物分类学专家，请从文本中提取所有分类单元作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的分类单元实体
- **边 (Edge)**：分类单元之间的层级包含关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的分类单元，禁止将多个分类单元合并为一个节点
2. 物种名称与原文保持一致

### 领域特定规则
- 分类等级：界(kingdom)、门(phylum)、纲(class)、目(order)、科(family)、属(genus)、种(species)
- 拉丁学名保持原文格式（属名首字母大写，种名小写斜体）
- 常见的分类等级英文缩写：Kingdom, Phylum, Class, Order, Family, Genus, Species

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知分类单元列表中提取它们之间的层级包含关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的分类单元实体
- **边 (Edge)**：分类单元之间的层级包含关系

## 提取规则
### 核心约束
1. 仅从已知分类单元列表中提取边，不要创建未列出的分类单元
2. 关系描述应与原文保持一致
3. 分类关系是层级包含关系，从高等级指向低等级

### 领域特定规则
- 关系类型统一为"包含于"
- 提取完整的分类路径信息

"""


class TaxonomicTree(AutoGraph[TaxonomicNode, TaxonomicRelation]):
    """
    适用文档: 生物学专著、分类学文献、物种描述

    功能介绍:
    提取生物分类学中的层级包含关系，构建分类学树。
    适用于生物分类学数据库、物种信息系统和生物多样性研究。

    Example:
        >>> template = TaxonomicTree(llm_client=llm, embedder=embedder)
        >>> template.feed_text("脊索动物门 → 辐鳍鱼纲 → 鲤形目 → 鲤科 → 鲢属 → 鲢鱼")
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
        初始化分类学树模板。

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
            node_schema=TaxonomicNode,
            edge_schema=TaxonomicRelation,
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
        展示分类学树。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: TaxonomicNode) -> str:
            return f"{node.name} ({node.rank})"

        def edge_label_extractor(edge: TaxonomicRelation) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
