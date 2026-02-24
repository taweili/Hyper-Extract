"""生化反应超图 - 从代谢通路文献中提取生化反应的多层次关系。

适用于代谢通路文献、生物化学教科书、酶学研究报告。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class MoleculeNode(BaseModel):
    """生化分子节点"""
    name: str = Field(description="分子名称，如葡萄糖、ATP、丙酮酸")
    molecule_type: str = Field(description="分子类型：酶、底物、产物、辅因子")
    molecular_formula: str = Field(description="分子式，如C6H12O6", default="")


class BiochemicalReactionEdge(BaseModel):
    """生化反应超边"""
    enzyme: str = Field(description="催化该反应的酶名称")
    substrates: List[str] = Field(description="反应底物列表")
    products: List[str] = Field(description="反应产物列表")
    cofactors: List[str] = Field(description="辅因子列表，如NAD+、Mg2+", default_factory=list)
    reaction_type: str = Field(description="反应类型：水解、氧化还原、转移、裂解、合成")
    direction: str = Field(description="反应方向：正向、逆向、可逆")
    details: str = Field(description="反应详细描述，包括反应条件或生物学意义", default="")


_PROMPT = """## 角色与任务
你是一位专业的生物化学专家，请从文本中提取生化分子及其反应关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的生化分子实体
- **边 (Edge)**：连接多个分子的超边，表示生化反应

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的分子，禁止将多个分子合并为一个节点
2. 分子名称与原文保持一致

### 超边提取约束
1. 超边连接酶、底物、产物等多类分子
2. 每条超边必须包含至少一个酶和底物

### 领域特定规则
- 酶：催化生化反应的蛋白质
- 反应类型：水解、氧化还原、转移、裂解、合成、异构
- 反应方向：正向、逆向、可逆

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的生物化学专家，请从文本中提取所有生化分子（酶、底物、产物、辅因子）作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的生化分子实体
- **边 (Edge)**：连接多个分子的超边，表示生化反应（酶催化底物转化为产物）

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的分子，禁止将多个分子合并为一个节点
2. 分子名称与原文保持一致

### 领域特定规则
- 酶：催化生化反应的蛋白质，如己糖激酶、磷酸果糖激酶
- 底物：被酶作用的分子
- 产物：反应生成的分子
- 辅因子：协助酶催化的分子，如NAD+、ATP、Mg2+
- 分子式使用标准化学式

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知分子列表中提取生化反应关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的生化分子实体
- **边 (Edge)**：连接多个分子的超边，表示生化反应

## 提取规则
### 核心约束
1. 超边连接酶、底物、产物等多类分子
2. 仅从已知分子列表中选择参与者，不要创建未列出的分子
3. 每条超边必须包含至少一个酶和底物

### 领域特定规则
- 反应类型：水解、氧化还原、转移、裂解、合成、异构
- 反应方向：正向、逆向、可逆
- 格式：{酶 + 底物A + 底物B → 产物C + 产物D}

"""


class BiochemicalReactionHypergraph(AutoHypergraph[MoleculeNode, BiochemicalReactionEdge]):
    """
    适用文档: 代谢通路文献、生物化学教科书、酶学研究报告

    功能介绍:
    精准建模 {酶 + 底物A + 底物B -> 产物C + 产物D} 的多输入多输出生化反应。
    适用于代谢通路图谱构建、代谢工程和系统生物学研究。

    Example:
        >>> template = BiochemicalReactionHypergraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("己糖激酶催化葡萄糖 + ATP → 6-磷酸葡萄糖 + ADP")
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
        初始化生化反应超图模板。

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
            node_schema=MoleculeNode,
            edge_schema=BiochemicalReactionEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.enzyme}_{x.reaction_type}_{sorted(x.substrates + x.products)}",
            nodes_in_edge_extractor=lambda x: tuple([x.enzyme] + x.substrates + x.products + x.cofactors),
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
        展示生化反应超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: MoleculeNode) -> str:
            return f"{node.name} ({node.molecule_type})"

        def edge_label_extractor(edge: BiochemicalReactionEdge) -> str:
            substrates_str = " + ".join(edge.substrates)
            products_str = " + ".join(edge.products)
            return f"{edge.enzyme}: {substrates_str} → {products_str}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
