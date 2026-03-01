"""调查背景图谱 - 提取报道中涉及的所有人物、机构、地点及其表层的静态关系。

适用于深度调查报道、人物特稿。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class NewsEntityNode(BaseModel):
    """新闻实体节点"""

    name: str = Field(description="实体名称")
    category: str = Field(description="实体类型：人物、机构、地点")
    description: str = Field(description="简要描述", default="")


class NewsContextEdge(BaseModel):
    """背景关系边"""

    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    relationType: str = Field(
        description="关系类型：任职、亲属、所属、所在地、投资、抵押"
    )
    description: str = Field(description="关系描述")


_NODE_PROMPT = """## 角色与任务
你是一位专业的新闻调查记者，请从调查报道文本中提取所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：实体之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 实体类型：人物（包含姓名、职务）、机构（公司、政府部门）、地点（地址、区域）
- 人物描述要包含职务或身份信息

## 调查报道文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取实体之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：实体之间的关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型：任职（人物-机构）、亲属（人物-人物）、所属（机构-机构/个人）、所在地（机构/个人-地点）、投资（机构-机构）、抵押（机构-地点）
- 描述两人之间的具体关系

## 已知实体
{known_nodes}

## 调查报道文本:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位专业的新闻调查记者，请从调查报道文本中提取实体和它们之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：实体之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 实体类型：人物（包含姓名、职务）、机构（公司、政府部门）、地点（地址、区域）
- 人物描述要包含职务或身份信息
- 关系类型：任职、亲属、所属、所在地、投资、抵押

## 调查报道文本:
{source_text}
"""


class InvestigativeContextGraph(AutoGraph[NewsEntityNode, NewsContextEdge]):
    """
    适用文档: 深度调查报道、人物特稿

    功能介绍:
    提取报道中涉及的所有人物、机构、地点及其表层的静态关系（如任职、亲属、所在地）。

    设计说明:
    - 节点（NewsEntityNode）：存储实体信息，包括名称、类型、描述
    - 边（NewsContextEdge）：存储实体间的关系及描述

    Example:
        >>> template = InvestigativeContextGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("某地产项目调查报道...")
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
        初始化调查背景图谱模板。

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
            node_schema=NewsEntityNode,
            edge_schema=NewsContextEdge,
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
        展示调查背景图谱。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: NewsEntityNode) -> str:
            return f"{node.name}[{node.category}]"

        def edge_label_extractor(edge: NewsContextEdge) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
