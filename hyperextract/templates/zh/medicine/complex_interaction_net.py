"""条件性相互作用网 - 建模"药A+药B+特定体质 -> 不良反应"的高阶依赖。

适用于药品说明书中关于药物相互作用的内容。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class InteractionEntity(BaseModel):
    """相互作用实体节点"""

    name: str = Field(description="实体名称，如药物、体质、不良反应等")
    category: str = Field(description="实体类型：药物、体质、不良反应、其他等")
    description: str = Field(description="简要描述", default="")


class InteractionHyperedge(BaseModel):
    """相互作用超边"""

    name: str = Field(description="超边名称，如药物相互作用")
    nodes: List[str] = Field(description="参与超边的节点列表")
    interactionType: str = Field(description="相互作用类型：增强、减弱、不良反应等")
    details: str = Field(description="详细描述，如具体的相互作用机制")


_PROMPT = """## 角色与任务
你是一位专业的临床药师，请从文本中提取药物相互作用信息，构建条件性相互作用网。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：连接多个节点，表达多个实体间的复杂关联关系

## 提取规则
### 核心约束
#### _PROMPT（节点提取）
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

#### 边提取
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 药物名称保持原文，如二甲双胍、磺酰脲类
- 不良反应名称保持原文

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的临床药师，请从文本中提取与药物相互作用相关的所有关键实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 药物名称保持原文，如二甲双胍、磺酰脲类
- 不良反应名称保持原文

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的临床药师，请从给定实体列表中提取药物相互作用，构建条件性相互作用网。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：连接多个节点，表达多个实体间的复杂关联关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 每条边必须连接多个节点
3. 关系描述应与原文保持一致

### 领域特定规则
- 药物名称保持原文
"""


class ComplexInteractionNet(AutoHypergraph[InteractionEntity, InteractionHyperedge]):
    """
    适用文档: 药品说明书、药物相互作用指南

    功能介绍:
    建模"药A+药B+特定体质 -> 不良反应"的高阶依赖，适用于合理用药系统 (高级版)。

    Example:
        >>> template = ComplexInteractionNet(llm_client=llm, embedder=embedder)
        >>> template.feed_text("二甲双胍与磺酰脲类合用可增加低血糖风险...")
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
        初始化条件性相互作用网模板。

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
            node_schema=InteractionEntity,
            edge_schema=InteractionHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.name,
            nodes_in_edge_extractor=lambda x: x.nodes,
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
        展示条件性相互作用网。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: InteractionEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: InteractionHyperedge) -> str:
            return f"{edge.name}: {edge.interactionType}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
