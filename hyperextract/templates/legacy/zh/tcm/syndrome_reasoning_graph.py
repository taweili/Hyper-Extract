"""辨证论治逻辑图 - 建模 {症状群} -> 证型 -> 治则 -> {处方} 的完整推理链条。

适用于医案数据挖掘、名老中医经验传承。
"""

from typing import Any, List
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import AutoHypergraph


class TCMEntity(BaseModel):
    """中医实体节点"""

    name: str = Field(description="实体名称，如症状、证型、治则、药物等")
    category: str = Field(description="实体类型：症状、证型、治则、药物")
    description: str = Field(description="简要描述", default="")


class SyndromeReasoningEdge(BaseModel):
    """辨证论治逻辑边"""

    nodes: List[str] = Field(
        description="参与推理的节点列表：[症状1, 症状2, ..., 证型, 治则, 药物1, 药物2, ...]"
    )
    reasoningType: str = Field(description="推理类型：辨证论治、随证加减")
    reasoningProcess: str = Field(description="推理过程描述", default="")
    source: str = Field(description="推理来源，如医案名称、章节等", default="")


_NODE_PROMPT = """## 角色与任务
你是一位专业的中医辨证论治专家，请从文本中提取中医实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：连接多个节点，表达多个实体间的复杂关联关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 症状：临床表现，如发热、汗出、恶风
- 证型：疾病分类，如太阳中风、太阳伤寒
- 治则：治疗原则，如解肌发表、调和营卫
- 药物：中药名称，如桂枝、麻黄、杏仁

## 中医医案:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的中医辨证论治专家，请从已知实体列表中提取辨证论治的推理逻辑作为超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：连接多个节点，表达多个实体间的复杂关联关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 推理类型：辨证论治、随证加减
- 推理链条：症状群 → 证型 → 治则 → 处方

## 已知实体列表:
{known_nodes}

## 中医医案:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位专业的中医辨证论治专家，请从文本中提取中医实体和辨证论治推理逻辑作为超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：连接多个节点，表达多个实体间的复杂关联关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体

### 领域特定规则
- 症状：临床表现，如发热、汗出、恶风
- 证型：疾病分类，如太阳中风、太阳伤寒
- 治则：治疗原则，如解肌发表、调和营卫
- 药物：中药名称，如桂枝、麻黄、杏仁
- 推理类型：辨证论治、随证加减
- 推理链条：症状群 → 证型 → 治则 → 处方

## 中医医案:
{source_text}
"""


class SyndromeReasoningGraph(AutoHypergraph[TCMEntity, SyndromeReasoningEdge]):
    """
    适用文档: 中医医案、名医临床实录

    功能介绍:
    从中医医案中提取辨证论治的完整推理链条，建模 {症状群} -> 证型 -> 治则 -> {处方} 的逻辑关系，
    支持复杂的多实体关联关系。

    Example:
        >>> template = SyndromeReasoningGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("...")
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
        初始化辨证论治逻辑图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            chunk_size: 每个分块的最大字符数，默认为 512（中医文本信息量大，需较小分块）
            chunk_overlap: 分块之间的重叠字符数，默认为 64
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=TCMEntity,
            edge_schema=SyndromeReasoningEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.reasoningType}|{'-'.join(x.nodes)}",
            nodes_in_edge_extractor=lambda x: x.nodes,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
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
        展示辨证论治逻辑图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: TCMEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: SyndromeReasoningEdge) -> str:
            return edge.reasoningType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
