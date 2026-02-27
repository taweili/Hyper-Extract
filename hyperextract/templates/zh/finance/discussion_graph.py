"""财报会议讨论图谱 - 从财报电话会议中提取实体及关系。

适用文档: 财报电话会议记录、投资者日问答、年度股东大会问答

功能介绍:
    提取财报会议中讨论的实体以及它们之间的关系，
    核心是参会人员（分析师、管理层），被提到的实体为辅助。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class DiscussionEntity(BaseModel):
    """讨论中的实体"""

    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型：参会人员、公司、产品、指标、行业")
    description: str = Field(description="实体描述/说明", default="")


class DiscussionRelation(BaseModel):
    """实体之间的关系"""

    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    relation_type: str = Field(description="关系类型")
    description: str = Field(description="简要描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的财报会议分析师，请从文本中提取讨论中出现的实体以及它们之间的关系。

## 核心概念定义
- **节点 (Node)**：讨论中出现的实体
- **边 (Edge)**：实体之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体
2. 实体名称与原文保持一致
3. **参会人员是核心，必须提取**

### 实体类型
- 参会人员：分析师、管理层（CEO、CFO等）
- 公司、产品、指标、行业等

### 关系类型
- 参会人员之间：提问、回答、追问、澄清、反问等
- 参会人员 ↔ 其他实体：提问关于、回答关于、看好、看衰、担忧、质疑、主导、负责等
- 其他实体之间：竞争、合作、增长、下降等

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取讨论中出现的实体作为节点。

## 核心概念定义
- **节点 (Node)**：讨论中出现的实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将其合并为一个节点
2. 实体名称与原文保持一致

### 实体类型
- 参会人员：分析师、管理层（CEO、CFO等）
- 公司、产品、指标、行业

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取实体之间的关系。

## 核心概念定义
- **边 (Edge)**：实体之间的关系，可以是参会人之间的关系、参会人与提到的实体之间的关系、或者实体之间的关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 关系类型
- 参会人员之间：提问、回答、追问、澄清、反问等
- 参会人员 ↔ 其他实体：提问关于、回答关于、看好、看衰、担忧、质疑、主导、负责等
- 其他实体之间：竞争、合作、增长、下降等

### 示例
- (分析师A, 提问, 营收指标)
- (CEO, 回答, 营收指标)
- (CFO, 澄清, 毛利率)
- (实体A, 竞争, 实体B)


"""


class DiscussionGraph(AutoGraph[DiscussionEntity, DiscussionRelation]):
    """
    适用文档: 财报电话会议记录、投资者日问答、年度股东大会问答

    功能介绍:
    提取财报会议中讨论的实体以及它们之间的关系。

    Example:
        >>> graph = DiscussionGraph(llm_client=llm, embedder=embedder)
        >>> graph.feed_text("分析师：关于AI业务前景？CEO：我们预计AI收入将增长...")
        >>> graph.show()
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
        初始化财报会议讨论图谱模板。

        Args:
            llm_client: LLM 客户端
            embedder: 嵌入模型
            extraction_mode: 提取模式
            chunk_size: 分块大小
            chunk_overlap: 分块重叠
            max_workers: 并行工作数
            verbose: 详细日志
            **kwargs: 其他参数
        """
        super().__init__(
            node_schema=DiscussionEntity,
            edge_schema=DiscussionRelation,
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
        """
        展示讨论图谱。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量
            top_k_edges_for_search: 语义检索返回的边数量
            top_k_nodes_for_chat: 问答使用的节点数量
            top_k_edges_for_chat: 问答使用的边数量
        """

        def node_label_extractor(node: DiscussionEntity) -> str:
            return f"{node.name} ({node.type})"

        def edge_label_extractor(edge: DiscussionRelation) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
