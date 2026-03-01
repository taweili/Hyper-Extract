"""蛋白质复合物超图 - 从蛋白质结构文献中提取蛋白质复合物的多亚基组成关系。

适用于蛋白质结构文献、蛋白质组学研究、信号通路分析。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class ProteinSubunitNode(BaseModel):
    """蛋白质亚基节点"""
    name: str = Field(description="蛋白质或亚基名称，如Gαs、Gβ、β2-AR")
    gene_name: str = Field(description="基因名称，如GNAS、GNB1", default="")
    subunit_type: str = Field(description="亚基类型：G蛋白α亚基、G蛋白β亚基、G蛋白γ亚基、受体、效应器")
    description: str = Field(description="简要描述", default="")


class ProteinComplexEdge(BaseModel):
    """蛋白质复合物超边"""
    members: List[str] = Field(description="参与组成复合物的所有蛋白质或亚基名称列表")
    complex_name: str = Field(description="复合物名称，如G蛋白异源三聚体、β2-AR信号复合物")
    function: str = Field(description="复合物功能描述")
    assembly_details: str = Field(description="组装细节，如哪些亚基相互作用", default="")


_PROMPT = """## 角色与任务
你是一位专业的结构生物学专家，请从“蛋白质结构文献”中提取蛋白质及其复合物组成关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的蛋白质实体
- **边 (Edge)**：连接多个蛋白质实体的超边，表示它们共同组成功能复合物

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的蛋白质或亚基，禁止将多个蛋白质合并为一个节点
2. 蛋白质名称与原文保持一致

### 超边提取约束
1. 超边连接2个或多个蛋白质节点
2. 每条超边必须至少有2个成员

### 领域特定规则
- G蛋白异源三聚体：包括Gα、Gβ、Gγ三个亚基
- 复合物类型：G蛋白异源三聚体、信号转导复合物、酶复合物等

## 蛋白质结构文献：
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的结构生物学专家，请从文本中提取所有蛋白质或亚基作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的蛋白质实体
- **边 (Edge)**：连接多个蛋白质实体的超边，表示它们共同组成功能复合物

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的蛋白质或亚基，禁止将多个蛋白质合并为一个节点
2. 蛋白质名称与原文保持一致

### 领域特定规则
- G蛋白异源三聚体：包括Gα、Gβ、Gγ三个亚基
- 受体：如β2-肾上腺素受体（β2-AR）
- 效应器：如腺苷酸环化酶（AC）
- 基因名称使用标准缩写

## 蛋白质结构文献:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知蛋白质列表中提取蛋白质复合物的组成关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的蛋白质实体
- **边 (Edge)**：连接多个蛋白质实体的超边，表示它们共同组成功能复合物

## 提取规则
### 核心约束
1. 超边连接2个或多个蛋白质实体节点
2. 仅从已知蛋白质实体列表中选择参与者，不要创建未列出的蛋白质实体
3. 每条超边必须至少有2个成员

### 领域特定规则
- 复合物类型：G蛋白异源三聚体、信号转导复合物、酶复合物等
- 组装信息：亚基之间的相互作用关系

## 已知蛋白质实体列表:
{known_nodes}

## 蛋白质结构文献:
{source_text}
"""


class ProteinComplexMap(AutoHypergraph[ProteinSubunitNode, ProteinComplexEdge]):
    """
    适用文档: 蛋白质结构文献、蛋白质组学研究、信号通路分析

    功能介绍:
    提取蛋白质复合物的多亚基结构，建模 {亚基A, 亚基B, 辅因子} 共同组成功能复合物的关系。
    适用于蛋白质复合物数据库、结构研究和药物设计。

    Example:
        >>> template = ProteinComplexMap(llm_client=llm, embedder=embedder)
        >>> template.feed_text("G蛋白异源三聚体由Gαs、Gβ和Gγ三个亚基组成...")
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
        初始化蛋白质复合物超图模板。

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
            node_schema=ProteinSubunitNode,
            edge_schema=ProteinComplexEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.complex_name}_{sorted(x.members)}",
            nodes_in_edge_extractor=lambda x: tuple(x.members),
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
        展示蛋白质复合物超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: ProteinSubunitNode) -> str:
            return f"{node.name} ({node.subunit_type})"

        def edge_label_extractor(edge: ProteinComplexEdge) -> str:
            return f"{edge.complex_name}: {', '.join(edge.members)}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
