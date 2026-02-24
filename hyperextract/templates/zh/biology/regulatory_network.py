"""基因调控网络 - 从分子生物学文献中提取转录因子与基因之间的调控关系。

适用于分子生物学文献、基因调控研究、信号通路分析。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class GeneNode(BaseModel):
    """基因/转录因子节点"""
    name: str = Field(description="基因或转录因子名称，如HIF-1α、c-Myc")
    gene_symbol: str = Field(description="基因符号，如HK2、PFKFB3", default="")
    type: str = Field(description="类型：转录因子、基因、启动子")
    function: str = Field(description="功能描述", default="")


class GeneRegulationRelation(BaseModel):
    """基因调控关系边"""
    source: str = Field(description="调控因子（转录因子）名称")
    target: str = Field(description="被调控基因名称")
    relation_type: str = Field(description="调控类型：激活、抑制、协同激活")
    mechanism: str = Field(description="调控机制，如结合启动子、组蛋白修饰", default="")
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的分子生物学专家，请从文本中提取基因、转录因子及其之间的调控关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的基因实体
- **边 (Edge)**：基因之间的调控关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的基因或转录因子，禁止将多个基因合并为一个节点
2. 基因名称与原文保持一致

### 边提取约束
1. 边只能连接已提取的基因节点
2. 关系描述应与原文保持一致

### 领域特定规则
- 转录因子：调控其他基因表达的蛋白质，如HIF-1α、c-Myc
- 调控类型：激活（促进表达）、抑制（阻止表达）、协同激活
- 调控机制：结合启动子、组蛋白修饰、DNA甲基化等

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的分子生物学专家，请从文本中提取所有基因、转录因子和启动子作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的基因实体
- **边 (Edge)**：基因之间的调控关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的基因或转录因子，禁止将多个基因合并为一个节点
2. 基因名称与原文保持一致

### 领域特定规则
- 转录因子：调控其他基因表达的蛋白质，如HIF-1α、c-Myc
- 启动子：基因转录起始区域
- 基因符号使用标准缩写，如HK2（己糖激酶2）、PFKFB3

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知基因列表中提取基因之间的调控关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的基因实体
- **边 (Edge)**：基因之间的调控关系

## 提取规则
### 核心约束
1. 仅从已知基因列表中提取边，不要创建未列出的基因
2. 关系描述应与原文保持一致

### 领域特定规则
- 调控类型：激活（促进表达）、抑制（阻止表达）、协同激活
- 调控机制：结合启动子、组蛋白修饰、DNA甲基化等

"""


class RegulatoryNetwork(AutoGraph[GeneNode, GeneRegulationRelation]):
    """
    适用文档: 分子生物学文献、基因调控研究、信号通路分析

    功能介绍:
    提取转录因子、启动子及其对基因表达的促进、抑制、协同作用，构建基因调控网络。
    适用于基因调控分析、系统生物学和药物靶点研究。

    Example:
        >>> template = RegulatoryNetwork(llm_client=llm, embedder=embedder)
        >>> template.feed_text("HIF-1α激活糖酵解相关基因HK2、PFKFB3、PKM2的表达...")
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
        初始化基因调控网络模板。

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
            node_schema=GeneNode,
            edge_schema=GeneRegulationRelation,
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
        展示基因调控网络。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: GeneNode) -> str:
            return f"{node.name} ({node.type})"

        def edge_label_extractor(edge: GeneRegulationRelation) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
