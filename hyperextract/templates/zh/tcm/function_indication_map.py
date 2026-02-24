"""主治功效映射 - 关联 方剂 -> 功能（如清热解毒） -> 主治证候。

适用于方剂推荐系统。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class GeneralEntity(BaseModel):
    """通用实体节点"""

    name: str = Field(description="实体名称")
    category: str = Field(description="实体类型：方剂、功能、主治证候")
    description: str = Field(description="简要描述", default="")


class GeneralRelation(BaseModel):
    """通用关系边"""

    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    relationType: str = Field(description="关系类型：具有功能、主治")
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的方剂学专家，请从文本中提取方剂、功能和主治证候之间的关联关系。

## 核心概念定义
- **节点 (Node)**：方剂、功能、主治证候
- **边 (Edge)**：实体之间的二元关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 方剂：如桂枝汤、麻黄汤
- 功能：如解肌发表、清热解毒
- 主治证候：如太阳中风、外感风寒

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取方剂、功能和主治证候实体作为节点。

## 核心概念定义
- **节点 (Node)**：方剂、功能、主治证候

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 方剂：如桂枝汤、麻黄汤
- 功能：如解肌发表、清热解毒
- 主治证候：如太阳中风、外感风寒

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取方剂、功能和主治证候之间的关联关系。

## 核心概念定义
- **边 (Edge)**：实体之间的二元关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 已知实体列表:
"""


class FunctionIndicationMap(AutoGraph[GeneralEntity, GeneralRelation]):
    """
    适用文档: 方剂规范、伤寒论、金匮要略、方剂学教材等

    功能介绍:
    关联 方剂 -> 功能（如清热解毒） -> 主治证候，适用于方剂推荐系统。

    Example:
        >>> template = FunctionIndicationMap(llm_client=llm, embedder=embedder)
        >>> template.feed_text("桂枝汤：解肌发表，调和营卫。主治太阳中风...")
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
        初始化主治功效映射模板。

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
            node_schema=GeneralEntity,
            edge_schema=GeneralRelation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
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
        展示主治功效映射。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: GeneralEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: GeneralRelation) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
