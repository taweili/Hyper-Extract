"""案件事实时序图 - 展示法律关系的变化过程。

从判决书的事实认定部分提取实体和法律行为，还原法律关系的时间演变。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph


class LegalEntityNode(BaseModel):
    """法律实体节点"""
    name: str = Field(description="实体名称，如原告、被告、合同、金钱、股权等")
    entity_type: str = Field(
        description="实体类型：当事人、合同/协议、金钱、股权、证物、其他"
    )
    description: Optional[str] = Field(description="简要描述", default=None)


class LegalEventEdge(BaseModel):
    """法律事件边"""
    source: str = Field(description="源实体名称")
    target: str = Field(description="目标实体名称")
    event: str = Field(
        description="法律行为或事件，如签订协议、支付投资款、分配红利、提起诉讼等"
    )
    time_info: str = Field(
        description="时间信息，统一格式为年-月-日（如2021-03-15）或年月（如2021-03）"
    )
    description: Optional[str] = Field(description="事件详细描述", default=None)


_NODE_PROMPT = """## 角色与任务
你是一位专业的法律工作者，请从文本中提取案件相关的法律实体作为节点。

## 核心概念定义
- **节点 (Node)**：案件中的法律实体
- **边 (Edge)**：法律实体之间的法律行为（带时间）

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 实体类型：当事人、合同/协议、金钱、股权、证物、其他
- 当事人：原告、被告、第三人、法定代表人、委托诉讼代理人
- 合同/协议：战略合作协议、补充协议、收益分配说明函等
- 金钱：投资款、红利、违约金等
- 股权：股份、股权等

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取法律实体之间的法律行为（事件）。

## 核心概念定义
- **节点 (Node)**：案件中的法律实体
- **边 (Edge)**：法律实体之间的法律行为（带时间）

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 法律行为
- 常见的法律行为：签订协议、支付投资款、完成登记、召开股东会、分配红利、发送函件、提起诉讼等
- 每个边表示一个法律行为，连接相关实体

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）
2. 精确时间 → 转换为标准格式年-月-日
3. 时间缺失 → 留空

### 已知实体列表:
"""

_PROMPT = """## 角色与任务
你是一位专业的法律工作者，请从文本中提取案件相关的法律实体以及它们之间的法律行为。

## 核心概念定义
- **节点 (Node)**：案件中的法律实体
- **边 (Edge)**：法律实体之间的法律行为（带时间）

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 实体类型
- 当事人：原告、被告、第三人、法定代表人、委托诉讼代理人
- 合同/协议：战略合作协议、补充协议、收益分配说明函等
- 金钱：投资款、红利、违约金等
- 股权：股份、股权等

### 法律行为
- 签订协议、支付投资款、完成登记、召开股东会、分配红利、发送函件、提起诉讼等

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）
2. 精确时间 → 转换为标准格式年-月-日
3. 时间缺失 → 留空

### 源文本:
"""


class CaseFactTimeline(AutoTemporalGraph[LegalEntityNode, LegalEventEdge]):
    """
    适用文档: 法院判决书、仲裁裁决书

    功能介绍:
    从判决书的"经审理查明"或"案件事实"部分提取实体和法律行为，
    展示法律关系随时间的变化过程。适用于案情复盘、证据链梳理等应用场景。

    设计说明:
    - 节点（LegalEntityNode）：存储法律实体信息，包括名称、类型、描述
    - 边（LegalEventEdge）：存储法律行为及时间，连接相关实体

    Example:
        >>> template = CaseFactTimeline(llm_client=llm, embedder=embedder)
        >>> template.feed_text("判决书事实认定部分...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: str = "2024-06-15",
        extraction_mode: str = "two_stage",
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化案件事实时序图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            observation_time: 观察时间，用于解析相对时间表达，默认2024-06-15
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=LegalEntityNode,
            edge_schema=LegalEventEdge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}|{x.event}|{x.target.strip()}",
            time_in_edge_extractor=lambda x: x.time_info or "",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
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
        展示案件事实时序图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: LegalEntityNode) -> str:
            return f"{node.name}({node.entity_type})"

        def edge_label_extractor(edge: LegalEventEdge) -> str:
            time_str = f" [{edge.time_info}]" if edge.time_info else ""
            return f"{edge.event}{time_str}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
