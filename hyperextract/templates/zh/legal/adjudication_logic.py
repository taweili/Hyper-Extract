"""裁判逻辑超图 - 建模法官的推理过程。

适用于法院判决书、仲裁裁决书等法律文书。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class AdjudicationElement(BaseModel):
    """裁判要素节点"""
    name: str = Field(description="要素名称")
    category: str = Field(
        description="要素类型：事实认定、法律依据、裁判结论、主旨、证据、其他"
    )
    description: str = Field(description="简要描述", default="")


class AdjudicationLogicEdge(BaseModel):
    """裁判逻辑超边"""
    logic_type: str = Field(
        description="推理类型：事实认定、法律适用、因果认定、责任认定、金额计算、其他"
    )
    participants: List[str] = Field(
        description="参与要素名称列表，必须使用已提取节点的 name"
    )
    reasoning: str = Field(
        description="推理过程描述，从事实到结论的逻辑推导"
    )
    conclusion: str = Field(description="推理结论")
    source_clause: str = Field(description="裁判文书的章节位置", default="")


_PROMPT = """## 角色与任务
你是一位专业的法律工作者，请从判决书中提取裁判要素和法官的推理逻辑。

## 核心概念定义
- **节点 (Node)**：构成裁判逻辑的基本要素，包括六类：
  - **事实认定**：法院查明的事实（如协议签订、款项支付等）
  - **法律依据**：适用的法律条文（如《民法典》第X条）
  - **裁判结论**：法院的最终判定（如确认协议无效、支付违约金等）
  - **主旨**：法律条文的核心要义
  - **证据**：证明事实的证据材料
  - **其他**：不属于上述类别的要素
- **边 (Edge)**：即"裁判逻辑"，连接多个节点，表达"认定事实 + 适用法律 -> 裁判结论"的推理过程

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的要素，禁止将多个要素合并为一个节点
2. 要素名称与原文保持一致
3. 仅从已提取节点创建裁判逻辑

### 节点提取
1. 提取判决书中涉及的裁判要素作为节点
2. 为每个要素指定类型
3. 为每个要素添加简要描述

### 超边提取
1. 逻辑类型：事实认定、法律适用、因果认定、责任认定、金额计算、其他
2. 超边必须包含 logic_type、participants、reasoning、conclusion
3. participants 必须严格使用已提取节点的名称

## 源文本:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
请从判决书中提取裁判相关要素作为节点。

## 核心概念定义
- **节点 (Node)**：构成裁判逻辑的基本要素，包括六类：
  - **事实认定**：法院查明的事实
  - **法律依据**：适用的法律条文
  - **裁判结论**：法院的最终判定
  - **主旨**：法律条文的核心要义
  - **证据**：证明事实的证据材料
  - **其他**：不属于上述类别的要素

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的要素，禁止将多个要素合并为一个节点
2. 要素名称与原文保持一致

### 节点提取
1. 提取判决书中涉及的裁判要素作为节点
2. 为每个要素指定类型
3. 为每个要素添加简要描述

## 判决书文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知裁判要素列表中提取裁判逻辑超边。

## 核心概念定义
- **节点 (Node)**：构成裁判逻辑的基本要素，作为超边的参与者
- **边 (Edge)**：即"裁判逻辑"，连接多个节点，表达"认定事实 + 适用法律 -> 裁判结论"的推理过程

## 提取规则
### 核心约束
1. participants 必须严格使用已知裁判要素列表中的名称，不要创建新名称
2. 超边必须包含 logic_type、participants、reasoning、conclusion
3. participants 应包含事实认定、法律依据、裁判结论等相关要素

### 逻辑类型说明
- **事实认定**：从证据推导出事实
- **法律适用**：将法律条文适用于具体事实
- **因果认定**：认定行为与损害之间的因果关系
- **责任认定**：认定当事人应承担的责任
- **金额计算**：计算具体的赔偿金额
- **其他**：不属于上述类型的推理

## 已知裁判要素列表:
{known_nodes}

## 判决书文本:
{source_text}
"""


class AdjudicationLogic(AutoHypergraph[AdjudicationElement, AdjudicationLogicEdge]):
    """
    适用文档: 法院判决书、仲裁裁决书

    功能介绍:
    建模法官的推理过程：{认定事实 + 适用法律 -> 裁判结论}。
    适用于类案推送、判决预测辅助等应用场景。

    设计说明:
    - 节点（AdjudicationElement）：存储裁判要素信息，包括名称、类型、描述
    - 边（AdjudicationLogicEdge）：存储完整的裁判推理逻辑

    Example:
        >>> template = AdjudicationLogic(llm_client=llm, embedder=embedder)
        >>> template.feed_text("判决书内容...")
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
        初始化裁判逻辑超图模板。

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
            node_schema=AdjudicationElement,
            edge_schema=AdjudicationLogicEdge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.logic_type}_{x.conclusion.strip()}",
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
        展示裁判逻辑超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: AdjudicationElement) -> str:
            return f"{node.name}({node.category})"

        def edge_label_extractor(edge: AdjudicationLogicEdge) -> str:
            return f"[{edge.logic_type}] {edge.conclusion}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
