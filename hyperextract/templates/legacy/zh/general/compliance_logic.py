"""合规行为超图 - 建模"在何种条件下，何种主体，必须/禁止执行何种操作"的复杂逻辑。

适用于合规审计、风险识别等。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class ComplianceElement(BaseModel):
    """合规要素 - 节点"""

    name: str = Field(description="要素名称，文本中出现的精确名称")
    category: str = Field(description="要素类型：主体、操作、条件、其他")
    description: str = Field(description="简要描述", default="")


class ComplianceRule(BaseModel):
    """合规规则 - 超边"""

    ruleType: str = Field(description="规则类型：必须、禁止、允许、其他")
    participants: List[str] = Field(
        description="参与要素名称列表，必须使用已提取节点的 name"
    )
    action: str = Field(description="要求执行或禁止的操作内容")
    condition: str = Field(description="适用条件/前置要求", default="")
    consequence: str = Field(description="违规后果/奖励措施", default="")
    sourceClause: str = Field(description="规则来源条款", default="")


_PROMPT = """## 角色与任务
你是一位专业的合规评估员，请从文本中提取合规要素和规则。

## 核心概念定义
- **节点 (Node)**：构成规则的基本要素，包括四类：
  - **主体**：执行动作的实体（个人、部门、组织、角色等）
  - **操作**：具体的行为动作（提交、审批、执行、禁止等）
  - **条件**：规则适用的时间、地点、状态、数量等前提条件
  - **其他**：不属于上述类别的要素（文书、文件、状态、结果等）
- **边 (Edge)**：即"规则"，连接多个节点，表达"在何种条件下，何种主体，必须/禁止执行何种操作"的逻辑

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已提取节点创建规则

### 节点提取
1. 提取规则中涉及的要素作为节点
2. 为每个要素指定类型
3. 为每个要素添加简要描述

### 超边提取
1. 规则类型：必须、禁止、允许、其他
2. 规则必须包含 ruleType、participants、action
3. participants 必须严格使用已提取节点的名称

## 源文本:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取合规相关要素作为节点。

## 核心概念定义
- **节点 (Node)**：构成规则的基本要素，包括四类：
  - **主体**：执行动作的实体（个人、部门、组织、角色等）
  - **操作**：具体的行为动作（提交、审批、执行、禁止等）
  - **条件**：规则适用的时间、地点、状态、数量等前提条件
  - **其他**：不属于上述类别的要素（文书、文件、状态、结果等）

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 节点提取
1. 提取规则中涉及的要素作为节点
2. 为每个要素指定类型
3. 为每个要素添加简要描述（1-2句话）

## 源文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知要素列表中提取合规规则超边。

## 核心概念定义
- **节点 (Node)**：构成规则的基本要素，作为超边的参与者
- **边 (Edge)**：即"规则"，连接多个节点，表达"在何种条件下，何种主体，必须/禁止执行何种操作"的逻辑

## 提取规则
### 核心约束
1. participants 必须严格使用已知要素列表中的名称，不要创建新名称
2. 规则必须包含 ruleType、participants、action
3. participants 应包含涉及的主体、执行的操作、以及相关的其他要素

### 规则类型说明
- **必须**：必须执行的动作
- **禁止**：禁止执行的动作
- **允许**：允许执行的动作
- **其他**：不属于上述类别的规则

## 已知要素列表:
{known_nodes}

## 源文本:
{source_text}
"""


class ComplianceLogic(AutoHypergraph[ComplianceElement, ComplianceRule]):
    """
    适用文档: 合规指南、行政法规、公司管理制度

    功能介绍:
    建模"在何种条件下，何种主体，必须/禁止执行何种操作"的复杂逻辑。适用于合规审计、风险识别等。

    Example:
        >>> template = ComplianceLogic(llm_client=llm, embedder=embedder)
        >>> template.feed_text("公司合规手册...")
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
        初始化合规行为超图模板。

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
            node_schema=ComplianceElement,
            edge_schema=ComplianceRule,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: (
                f"{sorted(x.participants)}_{x.ruleType}_{x.action}"
            ),
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
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
        展示合规行为超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: ComplianceElement) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: ComplianceRule) -> str:
            return f"[{edge.ruleType}] {edge.action}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
