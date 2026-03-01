"""受益所有权图谱 - 穿透多层股权结构，识别最终受益人和控制人。

适用于反洗钱申报文件、公司股权结构说明、受益所有人识别报告等。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class OwnershipNode(BaseModel):
    """股权节点"""
    entity_name: str = Field(description="实体名称，如公司名、人名")
    entity_type: str = Field(
        description="实体类型：公司、自然人、基金、合伙企业、境外特殊目的公司"
    )
    description: Optional[str] = Field(description="简要描述，如持股比例、职务", default=None)


class OwnershipRelationEdge(BaseModel):
    """股权关系边"""
    source: str = Field(description="源实体名称")
    target: str = Field(description="目标实体名称")
    relation_type: str = Field(
        description="关系类型：控股、参股、担任董事、执行事务合伙人、实际控制、配偶关系等"
    )
    shareholding_ratio: Optional[str] = Field(
        description="持股比例或出资比例，如35%、1%、XX%",
        default=None
    )
    description: Optional[str] = Field(description="关系描述，如通过多层持股结构控制", default=None)


_NODE_PROMPT = """## 角色与任务
你是一位专业的反洗钱合规专员，请从文本中提取股权结构相关的实体作为节点。

## 核心概念定义
- **节点 (Node)**：股权结构中的实体
- **边 (Edge)**：实体之间的股权或控制关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 实体类型：公司、自然人、基金、合伙企业、境外特殊目的公司
- 包含股东、合伙人、高管、实际控制人等

## 股权结构文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取股权或控制关系。

## 核心概念定义
- **节点 (Node)**：股权结构中的实体
- **边 (Edge)**：实体之间的股权或控制关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 关系类型
- **控股**：持有50%以上股份或出资额
- **参股**：持有一定比例股份但不构成控股
- **担任董事**：在公司担任董事职务
- **执行事务合伙人**：执行合伙事务
- **实际控制**：通过协议或其他安排实现实际控制
- **配偶关系**：夫妻关系
- **其他关系**：如父子、兄弟、姐妹等

## 已知实体列表:
{known_nodes}

## 股权结构文本:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位专业的反洗钱合规专员，请从文本中提取股权结构和受益所有权信息。

## 核心概念定义
- **节点 (Node)**：股权结构中的实体
- **边 (Edge)**：实体之间的股权或控制关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 实体类型
- 公司、自然人、基金、合伙企业、境外特殊目的公司

### 关系类型
- 控股、参股、担任董事、执行事务合伙人、实际控制、配偶关系等

## 股权结构文本:
{source_text}
"""


class BeneficialOwnershipGraph(AutoGraph[OwnershipNode, OwnershipRelationEdge]):
    """
    适用文档: 反洗钱申报文件、公司股权结构说明、受益所有人识别报告

    功能介绍:
    穿透多层股权结构，识别最终受益人和控制人。
    适用于反洗钱、制裁筛查等应用场景。

    设计说明:
    - 节点（OwnershipNode）：存储股权实体信息，包括名称、类型、描述
    - 边（OwnershipRelationEdge）：存储股权或控制关系

    Example:
        >>> template = BeneficialOwnershipGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("公司股权结构说明...")
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
        初始化受益所有权图谱模板。

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
            node_schema=OwnershipNode,
            edge_schema=OwnershipRelationEdge,
            node_key_extractor=lambda x: x.entity_name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}|{x.relation_type}|{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
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
        展示受益所有权图谱。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: OwnershipNode) -> str:
            return f"{node.entity_name}({node.entity_type})"

        def edge_label_extractor(edge: OwnershipRelationEdge) -> str:
            ratio = f" {edge.shareholding_ratio}" if edge.shareholding_ratio else ""
            return f"{edge.relation_type}{ratio}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
