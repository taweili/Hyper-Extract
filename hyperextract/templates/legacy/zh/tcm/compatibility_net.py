"""七情配伍网络 - 提取药物间的相须、相使、相畏、相杀、十八反十九畏关系。

适用于配伍禁忌预警、方剂组网分析。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class HerbEntity(BaseModel):
    """药物实体节点"""

    name: str = Field(description="药物名称")
    description: str = Field(description="简要描述", default="")


class CompatibilityRelation(BaseModel):
    """配伍关系边"""

    source: str = Field(description="源药物")
    target: str = Field(description="目标药物")
    relationType: str = Field(
        description="配伍关系类型：相须、相使、相畏、相杀、相恶、相反、十八反、十九畏"
    )
    effect: str = Field(description="配伍效果描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的中药配伍专家，请从文本中提取药物间的配伍关系。

## 核心概念定义
- **节点 (Node)**：中药药物实体
- **边 (Edge)**：药物之间的配伍关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 配伍关系类型：相须、相使、相畏、相杀、相恶、相反、十八反、十九畏

## 中药配伍文献:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取药物实体作为节点。

## 核心概念定义
- **节点 (Node)**：中药药物实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

## 中药配伍文献:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知药物列表中提取药物之间的配伍关系。

## 核心概念定义
- **边 (Edge)**：药物之间的配伍关系

## 提取规则
### 核心约束
1. 仅从已知药物列表中提取边，不要创建未列出的药物
2. 关系描述应与原文保持一致

## 已知药物列表:
{known_nodes}

## 中药配伍文献:
{source_text}
"""


class CompatibilityNet(AutoGraph[HerbEntity, CompatibilityRelation]):
    """
    适用文档: 本草典籍、中药配伍指南、方剂学教材等

    功能介绍:
    提取药物间的相须、相使、相畏、相杀、十八反十九畏关系，适用于配伍禁忌预警、方剂组网分析。

    Example:
        >>> template = CompatibilityNet(llm_client=llm, embedder=embedder)
        >>> template.feed_text("甘草反大戟、芫花、甘遂，海藻...")
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
        初始化七情配伍网络模板。

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
            node_schema=HerbEntity,
            edge_schema=CompatibilityRelation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
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
        展示七情配伍网络。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: HerbEntity) -> str:
            return node.name

        def edge_label_extractor(edge: CompatibilityRelation) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
