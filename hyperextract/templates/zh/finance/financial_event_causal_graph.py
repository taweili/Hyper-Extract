"""金融事件因果图谱 - 将金融事件映射到市场反应。

适用文档: 财经新闻文章、市场评论、宏观策略报告、经济数据发布

功能介绍:
    将金融事件映射到受影响的实体和下游市场反应，
    支持事件驱动策略开发和宏观影响分析。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class FinancialEventNode(BaseModel):
    """金融事件节点"""

    name: str = Field(description="实体名称")
    category: str = Field(
        description="实体类别：'政策事件'、'市场实体'、'经济指标'"
    )
    description: str = Field(
        description="实体的简要描述"
    )


class EventCausalEdge(BaseModel):
    """因果关系边"""

    source: str = Field(description="源实体名称")
    target: str = Field(description="目标实体名称")
    relation_type: str = Field(
        description="因果关系类型：推动、促进、带动、抑制、拖累、冲击、利好、利空"
    )
    description: str = Field(
        description="因果关系的详细说明"
    )


_PROMPT = """## 角色与任务
你是一位专业的宏观策略师，请从文本中提取金融事件及它们之间的因果关系。

## 核心概念定义
- **节点 (Node)**：金融事件、政策、经济指标、市场实体
- **边 (Edge)**：因果关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的事件/实体
2. 名称与原文保持一致
3. **source 和 target 都必须是已提取的实体节点**

### 实体类型
- 政策事件：降准、加息、财政政策
- 市场实体：银行、房地产、科技、消费
- 经济指标：GDP、CPI、利率、汇率

### 关系类型
- 推动类：推动、促进、带动
- 抑制类：抑制、拖累、冲击
- 影响类：利好、利空

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取金融实体作为节点。

## 核心概念定义
- **节点 (Node)**：政策事件、市场实体、经济指标

## 提取规则
1. 提取所有金融实体
2. 名称与原文保持一致

### 实体类型
- 政策事件：降准、加息、财政政策
- 市场实体：银行、房地产、科技、消费
- 经济指标：GDP、CPI、利率

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取实体之间的关系。

## 核心概念定义
- **边 (Edge)**：实体之间的因果关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致
3. **关键**：边的 source 和 target 必须完全使用下方实体列表中的名称

### 关系类型
- 推动类：推动、促进、带动
- 抑制类：抑制、拖累、冲击
- 影响类：利好、利空

"""


class FinancialEventCausalGraph(AutoGraph[FinancialEventNode, EventCausalEdge]):
    """
    适用文档: 财经新闻文章、市场评论、宏观策略报告、经济数据发布

    功能介绍:
    将金融事件映射到受影响的实体和下游市场反应，
    支持事件驱动策略开发和宏观影响分析。

    Example:
        >>> causal = FinancialEventCausalGraph(llm_client=llm, embedder=embedder)
        >>> causal.feed_text("美联储加息25个基点，银行板块上涨...")
        >>> causal.show()
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
        super().__init__(
            node_schema=FinancialEventNode,
            edge_schema=EventCausalEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relation_type}|{x.target}",
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
        def node_label_extractor(node: FinancialEventNode) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: EventCausalEdge) -> str:
            return f"{edge.relation_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
