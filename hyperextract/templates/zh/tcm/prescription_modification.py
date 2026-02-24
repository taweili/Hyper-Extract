"""处方加减逻辑 - 提取基于特定证型或症状对基础方剂进行的药物加减（如"随证加减"）。

适用于临证用药规律分析、临床处方加减逻辑提取。

设计原则：
- 节点（PrescriptionNode）：存储方剂、药物、证型、症状等实体
- 超边（ModificationHyperedge）：存储完整的加减关系，包含基础方、加减条件、加减药物
"""

from typing import Any, List
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import AutoHypergraph


class PrescriptionNode(BaseModel):
    """处方加减实体节点"""

    name: str = Field(description="实体名称")
    category: str = Field(description="实体类型：基础方、药物、证型、症状")


class ModificationHyperedge(BaseModel):
    """处方加减超边 - 存储完整的加减关系"""

    baseFormula: str = Field(description="基础方剂名称")
    condition: str = Field(description="加减条件（证型或症状）")
    modificationType: str = Field(description="加减类型：加、减、替换")
    herbs: List[str] = Field(description="加减药物列表")
    reason: str = Field(description="加减原因", default="")
    dosage: str = Field(description="调整后的剂量", default="")


_NODE_PROMPT = """## 角色与任务
你是一位专业的中医方剂专家，请从文本中提取处方加减相关的实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 基础方：方剂名称，如桂枝汤、麻黄汤、小柴胡汤
- 药物：中药名称，如葛根、厚朴、杏仁、附子
- 证型/症状：临床表现，如项背强几几、喘、腹满痛

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的中医方剂专家，请从已知实体列表中提取处方加减逻辑作为超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：连接多个节点，表达多个实体间的复杂关联关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 加减类型：加、减、替换（通过 modificationType 字段区分）

### 已知实体列表:
"""

_PROMPT = """## 角色与任务
你是一位专业的中医方剂专家，请从文本中提取处方加减的实体和超边结构。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：连接多个节点，表达多个实体间的复杂关联关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体

### 领域特定规则
- 基础方：方剂名称
- 药物：中药名称
- 证型/症状：临床表现
- 加减类型：加、减、替换

### 源文本:
"""


class PrescriptionModification(AutoHypergraph[PrescriptionNode, ModificationHyperedge]):
    """
    适用文档: 中医方剂学著作、临床医案、伤寒论、金匮要略

    功能介绍:
    从中医文本中提取基于特定证型或症状对基础方剂进行的药物加减逻辑，
    如"随证加减"等临证用药规律。

    Example:
        >>> template = PrescriptionModification(llm_client=llm, embedder=embedder)
        >>> template.feed_text("若兼喘者，加厚朴二两、杏仁五十枚。")
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
        初始化处方加减逻辑模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """

        def nodes_in_edge_extractor(edge: ModificationHyperedge) -> set:
            nodes = set()
            if edge.baseFormula:
                nodes.add(edge.baseFormula)
            for herb in edge.herbs:
                if herb:
                    nodes.add(herb)
            return nodes

        super().__init__(
            node_schema=PrescriptionNode,
            edge_schema=ModificationHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.baseFormula}|{x.condition}",
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
        展示处方加减逻辑图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: PrescriptionNode) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: ModificationHyperedge) -> str:
            return f"{edge.baseFormula} | {edge.condition}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
