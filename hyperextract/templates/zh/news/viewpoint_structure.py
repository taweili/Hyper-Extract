"""观点逻辑结构 - 建模文章的论证逻辑，将观点、论据、背景引用聚合为观点结构。

适用于社论分析、舆情观点聚类。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class ArgumentElement(BaseModel):
    """论证元素"""

    name: str = Field(description="元素名称，简短唯一标识符，如'政策建议'、'数据支撑'、'专家观点'")
    category: str = Field(description="元素类型：观点、论据、背景引用")
    content: str = Field(description="完整内容，概括原文意思")
    source: str = Field(description="来源，如无则为空白", default="")


class ViewpointCluster(BaseModel):
    """观点聚合超边"""

    name: str = Field(description="聚合名称，简短唯一标识，如'核心论点'、'论证结构'、'分析框架'")
    participantNames: List[str] = Field(description="参与此观点论证的所有元素名称列表，必须从已提取的节点中选择")
    description: str = Field(description="论证描述，说明这些元素如何构成观点")


_NODE_PROMPT = """## 角色与任务
你是一位专业的政策分析师，请从政策分析或社论文本中提取所有论证元素作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的论证元素，包括观点、论据、背景引用
- **边 (Edge)**：连接多个节点的超边，将相关的论证元素聚合为完整的观点结构

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的元素，禁止将多个元素合并为一个节点
2. 元素名称 (name) 必须是简短、唯一的标识符，用于后续引用
3. 元素名称与原文保持一致，但要简洁（不超过10个字）
4. 内容 (content) 字段要完整概括原文意思

### 领域特定规则
- **观点**：作者的核心论点、主张或结论（如"经济发展应优先于环境保护"）
- **论据**：支撑观点的证据、数据或分析（如"GDP增长率下降2%"）
- **背景引用**：政策文件、统计数据、专家说法等外部引用（如"根据国家统计局2023年数据"）
- 来源如无则为空白

## 政策分析文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的政策分析师，请从已知论证元素列表中构建观点聚合超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的论证元素，每个节点有唯一的name作为标识符
- **边 (Edge)**：连接多个节点的超边，将围绕同一观点的相关元素聚合在一起

## 提取规则
### 核心约束
1. 每个超边代表一个完整的观点论证结构
2. 超边必须包含至少2个节点（一个观点 + 至少一个论据或背景引用）
3. 只能从已知节点列表中选择，禁止创建未列出的节点
4. participantNames字段必须填写节点的名字

### 引用规则（关键）
- `participantNames` 字段：填写参与此观点论证的所有元素名称列表

### 领域特定规则
- 将围绕同一核心观点的所有相关元素聚合到一个超边中
- 一个观点可以参与多个超边（从不同角度论证）
- 描述应说明这些元素如何共同支撑观点

## 已知论证元素
{known_nodes}

## 政策分析文本:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位专业的政策分析师，请从文本中提取论证元素以及它们组成的观点聚合超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的论证元素，包括观点、论据、背景引用
- **边 (Edge)**：连接多个节点的超边，将围绕同一观点的相关元素聚合在一起

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的元素，禁止将多个元素合并
2. 元素名称 (name) 必须是简短、唯一的标识符（不超过10个字）
3. 每个超边必须包含至少2个节点（观点 + 论据/背景引用）
4. 超边中的participantNames必须填写节点的元素名称

### 领域特定规则
- **观点**：作者的核心论点
- **论据**：支撑观点的证据或分析
- **背景引用**：政策文件、统计数据、专家说法

## 政策分析文本:
{source_text}
"""


class ViewpointStructure(AutoHypergraph[ArgumentElement, ViewpointCluster]):
    """
    适用文档: 政策分析、社论、舆情文章

    功能介绍:
    建模文章的论证逻辑，将观点、论据、背景引用聚合为观点结构。

    设计说明:
    - 节点（ArgumentElement）：存储论证元素信息，包括名称、类型、内容、来源
    - 边（ViewpointCluster）：将围绕同一观点的相关元素聚合在一起

    Example:
        >>> template = ViewpointStructure(llm_client=llm, embedder=embedder)
        >>> template.feed_text("某政策解读文章...")
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
        初始化观点结构模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """

        def nodes_in_edge_extractor(edge: ViewpointCluster) -> set:
            return set(edge.participantNames)

        super().__init__(
            node_schema=ArgumentElement,
            edge_schema=ViewpointCluster,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.name,
            nodes_in_edge_extractor=nodes_in_edge_extractor,
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
        展示观点结构。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: ArgumentElement) -> str:
            return f"{node.name}[{node.category}]"

        def edge_label_extractor(edge: ViewpointCluster) -> str:
            return edge.name

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
