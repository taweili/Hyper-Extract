"""诉讼参与人图谱 - 提取原告、被告、第三人、代理律师及证人之间的关系。

适用于法院判决书、仲裁裁决书、起诉状、答辩状等法律文书。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class ParticipantNode(BaseModel):
    """诉讼参与人节点"""
    name: str = Field(description="参与人名称，如公司名、人名")
    participant_type: str = Field(
        description="参与人类型：原告、被告、第三人、委托诉讼代理人、法定代理人、证人、鉴定人、法官、合议庭成员"
    )
    role_description: Optional[str] = Field(description="角色描述，如法定代表人、执行董事", default=None)


class ParticipantRelationEdge(BaseModel):
    """诉讼参与人关系边"""
    source: str = Field(description="源参与人名称")
    target: str = Field(description="目标参与人名称")
    relation_type: str = Field(
        description="关系类型：代理、代表、股东、董事、担保、上下级、同案当事人、敌对"
    )
    description: Optional[str] = Field(description="关系描述", default=None)


_NODE_PROMPT = """## 角色与任务
你是一位专业的法律工作者，请从文本中提取所有诉讼参与人作为节点。

## 核心概念定义
- **节点 (Node)**：诉讼参与人
- **边 (Edge)**：参与人之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的参与人，禁止将多个参与人合并为一个节点
2. 参与人名称与原文保持一致

### 领域特定规则
- 参与人类型：原告、被告、第三人、委托诉讼代理人、法定代理人、证人、鉴定人、法官、合议庭成员
- 常见的参与人：当事人（公司或个人）、律师、法定代表人、证人

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知参与人列表中提取参与人之间的关系。

## 核心概念定义
- **节点 (Node)**：诉讼参与人
- **边 (Edge)**：参与人之间的关系

## 提取规则
### 核心约束
1. 仅从已知参与人列表中提取边，不要创建未列出的参与人
2. 关系描述应与原文保持一致

### 关系类型
- **代理**：委托诉讼代理关系
- **代表**：法定代表关系
- **股东**：公司股东关系
- **董事**：公司董事关系
- **担保**：担保关系
- **上下级**：上下级领导关系
- **同案当事人**：同一案件中的原告或被告
- **敌对**：利益对立关系

### 已知参与人列表:
"""

_PROMPT = """## 角色与任务
你是一位专业的法律工作者，请从文本中提取所有诉讼参与人以及他们之间的关系。

## 核心概念定义
- **节点 (Node)**：诉讼参与人
- **边 (Edge)**：参与人之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的参与人，禁止将多个参与人合并为一个节点
2. 参与人名称与原文保持一致
3. 仅从已知参与人列表中提取边，不要创建未列出的参与人
4. 关系描述应与原文保持一致

### 参与人类型
- 原告、被告、第三人、委托诉讼代理人、法定代理人、证人、鉴定人、法官、合议庭成员

### 关系类型
- 代理、代表、股东、董事、担保、上下级、同案当事人、敌对

### 源文本:
"""


class LitigationParticipantMap(AutoGraph[ParticipantNode, ParticipantRelationEdge]):
    """
    适用文档: 法院判决书、仲裁裁决书、起诉状、答辩状

    功能介绍:
    提取原告、被告、第三人、代理律师及证人之间的关系。
    适用于利益冲突检索、关联案件分析等应用场景。

    设计说明:
    - 节点（ParticipantNode）：存储诉讼参与人信息，包括名称、类型、角色描述
    - 边（ParticipantRelationEdge）：存储参与人之间的关系

    Example:
        >>> template = LitigationParticipantMap(llm_client=llm, embedder=embedder)
        >>> template.feed_text("判决书当事人信息...")
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
        初始化诉讼参与人图谱模板。

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
            node_schema=ParticipantNode,
            edge_schema=ParticipantRelationEdge,
            node_key_extractor=lambda x: x.name.strip(),
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
        展示诉讼参与人图谱。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: ParticipantNode) -> str:
            return f"{node.name}({node.participant_type})"

        def edge_label_extractor(edge: ParticipantRelationEdge) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
