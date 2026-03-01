"""多因素病理机制图 - 建模"基因+环境+诱因 -> 疾病"的复杂致病逻辑。

适用于医学教科书与专著中关于疾病病理机制的内容。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class PathologyEntity(BaseModel):
    """病理实体节点"""

    name: str = Field(description="实体名称，如基因、环境因素、诱因、疾病等")
    category: str = Field(
        description="实体类型：基因、环境因素、诱因、疾病、病理过程、症状等"
    )
    description: str = Field(description="简要描述", default="")


class PathologyHyperedge(BaseModel):
    """病理机制超边"""

    mechanism_name: str = Field(
        description="机制名称，简短描述性名称，例如 '气道高反应性诱发机制'、'α1-抗胰蛋白酶缺乏致病途径'"
    )
    participating_entities: List[str] = Field(
        description="参与此病理机制的所有实体名称列表"
    )
    relationType: str = Field(description="关系类型：致病、诱发、促进、抑制等")
    details: str = Field(description="详细描述，如具体的致病机制")
    outcome: str = Field(
        description="该机制导致的结果或效应，例如 '慢性阻塞性肺疾病发生'、'肺气肿形成'"
    )


_PROMPT = """## 角色与任务
你是一位专业的病理学家，请从文本中提取与疾病病理机制相关的实体和它们之间的复杂关联关系，构建多因素病理机制图。

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
- 医学专业术语保持原文，如基因名称（BRCA1、KRAS、TP53）、蛋白名称
- 疾病名称保持原文，如慢性阻塞性肺疾病、肺癌

## 病理文档:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的病理实体识别专家，请从文本中提取与疾病病理机制相关的所有关键实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 医学专业术语保持原文，如基因名称（BRCA1、KRAS、TP53）、蛋白名称
- 疾病名称保持原文

## 病理文档:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的病理机制分析师，请从给定实体列表中提取它们之间的复杂关联关系，构建病理机制超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：连接多个节点，表达多个实体间的复杂关联关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 每条超边必须连接多个节点
3. 关系描述应与原文保持一致

### 领域特定规则
- 医学专业术语保持原文

## 已知实体:
{known_nodes}

## 病理文档:
{source_text}
"""


class PathologyHypergraph(AutoHypergraph[PathologyEntity, PathologyHyperedge]):
    """
    适用文档: 医学教科书、医学专著、病理生理学教材

    功能介绍:
    建模"基因+环境+诱因 -> 疾病"的复杂致病逻辑，从文本中提取病理相关实体及其复杂关联关系。

    Example:
        >>> template = PathologyHypergraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("慢性阻塞性肺疾病的发病机制涉及遗传因素、环境因素和炎症反应...")
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
        初始化多因素病理机制图模板。

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
            node_schema=PathologyEntity,
            edge_schema=PathologyHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.mechanism_name,
            nodes_in_edge_extractor=lambda x: x.participating_entities,
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
        展示多因素病理机制图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: PathologyEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: PathologyHyperedge) -> str:
            return f"[{edge.relationType}] {edge.mechanism_name}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
