"""合同义务超图 - 建模复杂的条件性义务。

适用于主服务协议、劳动合同、采购合同等商业合同文本。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class ContractElement(BaseModel):
    """合同要素节点"""
    name: str = Field(description="要素名称，文本中出现的精确名称")
    category: str = Field(
        description="要素类型：主体、义务、触发条件、例外情形、违约责任、其他"
    )
    description: str = Field(description="简要描述", default="")


class ContractObligationEdge(BaseModel):
    """合同义务超边"""
    obligation_type: str = Field(
        description="义务类型：支付义务、交付义务、保密义务、竞业限制、售后服务、其他"
    )
    participants: List[str] = Field(
        description="参与要素名称列表，必须使用已提取节点的 name"
    )
    trigger_condition: str = Field(
        description="触发条件，如合同签订后、验收合格后、违约行为发生时等",
        default=""
    )
    exception: str = Field(
        description="例外情形，如不可抗力、对方违约在先等",
        default=""
    )
    liability: str = Field(
        description="违约责任，如支付违约金、赔偿损失、解除合同等",
        default=""
    )
    source_clause: str = Field(description="义务来源条款编号或名称", default="")


_PROMPT = """## 角色与任务
你是一位专业的合同法律师，请从文本中提取合同要素和合同义务。

## 核心概念定义
- **节点 (Node)**：构成合同义务的基本要素，包括六类：
  - **主体**：合同的当事人（甲方、乙方、委托方、服务方等）
  - **义务**：具体需要执行的行为（支付、交付、保密、培训等）
  - **触发条件**：义务生效或履行的前提条件（合同签订后、验收合格后等）
  - **例外情形**：义务免除或减轻的情形（不可抗力、对方违约等）
  - **违约责任**：违反义务的后果（违约金、赔偿损失、解除合同等）
  - **其他**：不属于上述类别的要素（验收标准、付款方式等）
- **边 (Edge)**：即"合同义务"，连接多个节点，表达"在何种条件下，主体应履行何种义务，例外情形及违约责任"的完整逻辑

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的要素，禁止将多个要素合并为一个节点
2. 要素名称与原文保持一致
3. 仅从已提取节点创建合同义务

### 节点提取
1. 提取合同中涉及的要素作为节点
2. 为每个要素指定类型
3. 为每个要素添加简要描述

### 超边提取
1. 义务类型：支付义务、交付义务、保密义务、竞业限制、售后服务、其他
2. 超边必须包含 obligation_type、participants
3. participants 必须严格使用已提取节点的名称

## 合同条款:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取合同相关要素作为节点。

## 核心概念定义
- **节点 (Node)**：构成合同义务的基本要素，包括六类：
  - **主体**：合同的当事人（甲方、乙方、委托方、服务方等）
  - **义务**：具体需要执行的行为（支付、交付、保密、培训等）
  - **触发条件**：义务生效或履行的前提条件（合同签订后、验收合格后等）
  - **例外情形**：义务免除或减轻的情形（不可抗力、对方违约等）
  - **违约责任**：违反义务的后果（违约金、赔偿损失、解除合同等）
  - **其他**：不属于上述类别的要素（验收标准、付款方式等）

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的要素，禁止将多个要素合并为一个节点
2. 要素名称与原文保持一致

### 节点提取
1. 提取合同中涉及的要素作为节点
2. 为每个要素指定类型
3. 为每个要素添加简要描述（1-2句话）

## 合同条款:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知合同要素列表中提取合同义务超边。

## 核心概念定义
- **节点 (Node)**：构成合同义务的基本要素，作为超边的参与者
- **边 (Edge)**：即"合同义务"，连接多个节点，表达完整的合同义务逻辑

## 提取规则
### 核心约束
1. participants 必须严格使用已知合同要素列表中的名称，不要创建新名称
2. 超边必须包含 obligation_type、participants
3. participants 应包含涉及的主体、义务及相关要素

### 义务类型说明
- **支付义务**：支付款项的义务
- **交付义务**：交付产品、工作成果的义务
- **保密义务**：保护商业秘密的义务
- **竞业限制**：限制从事同类业务的义务
- **售后服务**：提供后续服务的义务
- **其他**：不属于上述类别的义务

### 触发条件
- 合同签订后X个工作日内
- 验收合格后X日内
- 违约行为发生时
- 质保期满后

### 违约责任
- 支付违约金
- 赔偿损失
- 解除合同
- 返还已付款项

## 已知合同要素列表:
{known_nodes}

## 合同条款:
{source_text}
"""


class ContractObligationHypergraph(AutoHypergraph[ContractElement, ContractObligationEdge]):
    """
    适用文档: 主服务协议（MSA）、劳动合同、采购合同、技术合同

    功能介绍:
    建模复杂的条件性义务：{主体, 义务, 触发条件, 例外情形, 违约责任}。
    适用于同时履行抗辩权分析、合同审查等应用场景。

    设计说明:
    - 节点（ContractElement）：存储合同要素信息，包括名称、类型、描述
    - 边（ContractObligationEdge）：存储合同义务的完整逻辑

    Example:
        >>> template = ContractObligationHypergraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("合同条款内容...")
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
        初始化合同义务超图模板。

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
            node_schema=ContractElement,
            edge_schema=ContractObligationEdge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.obligation_type}_{'_'.join(sorted(x.participants))}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
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
        展示合同义务超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: ContractElement) -> str:
            return f"{node.name}({node.category})"

        def edge_label_extractor(edge: ContractObligationEdge) -> str:
            return f"[{edge.obligation_type}] {edge.liability or edge.trigger_condition or ''}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
