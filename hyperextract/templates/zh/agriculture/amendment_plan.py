"""改良方案图 - 从土壤改良方案报告中提取检测结果到改良措施的逻辑链条。

适用于土壤改良方案报告、测土配方施肥建议报告、地力提升方案。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class AmendmentNode(BaseModel):
    """改良方案节点"""

    name: str = Field(description="节点名称（限制因子、改良措施、预期目标）")
    node_type: str = Field(
        description="节点类型：检测结果、限制因子、改良措施、预期目标"
    )
    description: str = Field(description="详细描述")


class AmendmentEdge(BaseModel):
    """改良关系边"""

    source: str = Field(description="源节点")
    target: str = Field(description="目标节点")
    relation_type: str = Field(description="关系类型：针对、达成")
    details: str = Field(description="详细描述")


_PROMPT = """## 角色与任务
你是一位专业的土壤肥料专家，请从土壤改良方案报告中提取改良方案图。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 边提取
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 检测结果：如pH5.2、有机质18.5g/kg、有效磷12.3mg/kg等
- 限制因子：如土壤酸化、磷钾缺乏、微量元素失衡、有机质不足
- 改良措施：如施用生石灰、增施有机肥、施用复合肥等
- 预期目标：如pH提高至6.0、有机质提升至22g/kg等

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的土壤改良方案提取专家，请从文本中提取所有相关节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 检测结果：土壤检测指标及数值，如pH5.2、有机质18.5g/kg
- 限制因子：土壤存在的问题，如土壤酸化、磷钾缺乏、微量元素失衡
- 改良措施：针对问题采取的措施，如施用生石灰、增施有机肥
- 预期目标：改良后达到的目标，如pH提高至6.0、产量提升10%

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知节点列表中提取改良方案关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型"针对"：表示改良措施针对某个限制因子
- 关系类型"达成"：表示预期目标与改良措施的关联

"""


class AmendmentPlan(AutoGraph[AmendmentNode, AmendmentEdge]):
    """
    适用文档: 土壤改良方案报告、测土配方施肥建议报告、地力提升方案

    功能介绍:
    从土壤改良方案报告中提取"检测结果 → 限制因子 → 改良措施 → 预期目标"
    的逻辑链条，构建改良方案知识图谱。
    适用于精准农业处方生成、地力提升规划。

    Example:
        >>> template = AmendmentPlan(llm_client=llm, embedder=embedder)
        >>> template.feed_text("土壤pH5.2属于严重酸性，第一限制因子是土壤酸化...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化改良方案图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            chunk_size: 每个分块的最大字符数，默认为 2048
            chunk_overlap: 分块之间的重叠字符数，默认为 256
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=AmendmentNode,
            edge_schema=AmendmentEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relation_type}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
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
        展示改良方案图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: AmendmentNode) -> str:
            return f"{node.name} ({node.node_type})"

        def edge_label_extractor(edge: AmendmentEdge) -> str:
            return f"{edge.relation_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
