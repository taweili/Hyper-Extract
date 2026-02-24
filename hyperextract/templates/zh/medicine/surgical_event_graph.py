"""手术事件超图 - 将手术建模为 {医生, 部位, 术式, 器械} 共同参与的复杂事件。

适用于出院小结中关于手术事件的内容。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class SurgicalEntity(BaseModel):
    """手术实体节点"""

    name: str = Field(description="实体名称，如医生、部位、术式、器械等")
    category: str = Field(description="实体类型：医生、部位、术式、器械、麻醉方式等")
    description: str = Field(description="简要描述", default="")


class SurgicalHyperedge(BaseModel):
    """手术事件超边"""

    name: str = Field(description="超边名称，如手术名称")
    nodes: List[str] = Field(description="参与超边的节点列表")
    date: str = Field(description="手术日期")
    duration: str = Field(description="手术时长", default="")
    details: str = Field(description="详细描述，如手术过程")


_PROMPT = """## 角色与任务
你是一位专业的外科医生，请从文本中提取手术事件及其相关实体，构建手术事件超图。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：连接多个节点，表达多个实体间的复杂关联关系

## 提取规则
### 核心约束
#### 节点提取
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

#### 边提取
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 手术术式保持原文，如冠状动脉旁路移植术
- 医疗器械名称保持原文

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的手术实体识别专家，请从文本中提取与手术事件相关的所有关键实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 手术术式保持原文
- 医疗器械名称保持原文

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的手术事件提取专家，请从给定实体列表中提取完整的手术事件，构建手术事件超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：连接多个节点，表达多个实体间的复杂关联关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 每条边必须连接多个节点
3. 关系描述应与原文保持一致

### 领域特定规则
- 医学术语保持原文
"""


class SurgicalEventGraph(AutoHypergraph[SurgicalEntity, SurgicalHyperedge]):
    """
    适用文档: 出院小结、手术记录

    功能介绍:
    将手术建模为 {医生, 部位, 术式, 器械} 共同参与的复杂事件，适用于手术质控、绩效评估。

    Example:
        >>> template = SurgicalEventGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("2026年2月4日，王医生为患者进行了冠状动脉旁路移植术...")
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
        初始化手术事件超图模板。

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
            node_schema=SurgicalEntity,
            edge_schema=SurgicalHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.name,
            nodes_in_edge_extractor=lambda x: x.nodes,
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
        展示手术事件超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: SurgicalEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: SurgicalHyperedge) -> str:
            return f"{edge.name} ({edge.date})"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
