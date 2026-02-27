"""事故因果链超图 - 从事故调查报告中提取隐患、触发条件、违章行为、事故后果的因果关系。

适用于事故推演、风险预防、调查报告分析等文本。
"""

from typing import Optional, Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class IncidentEntity(BaseModel):
    """
    事故因果链实体节点。
    """

    name: str = Field(description="实体名称（例如：违章操作、泄漏积累、点火源等）。")
    category: str = Field(description="类型：隐患、触发条件、违章行为、事故后果。")
    description: Optional[str] = Field(
        None, description="描述（例如：未佩戴安全带、管道腐蚀破裂）。"
    )
    severity: Optional[str] = Field(
        None, description="严重程度：轻微、一般、严重、重大。"
    )


class IncidentCausalityEdge(BaseModel):
    """
    事故因果链超边，连接多个实体形成因果链条。
    """

    nodes: List[str] = Field(
        description="参与因果链条的节点列表：[隐患1, 隐患2, ..., 触发条件, 违章行为, 事故后果1, 事故后果2, ...]"
    )
    causality_type: str = Field(
        description="因果类型：隐患积累、触发导致、违章促成、后果扩展。"
    )
    causality_description: Optional[str] = Field(
        None,
        description="因果关系详细描述（例如：由于管道腐蚀导致泄漏，遇火源引发火灾）。",
    )


_NODE_PROMPT = """## 角色与任务
你是一位工业安全事故调查专家，请从事故调查报告中提取所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的事故相关实体
- **边 (Edge)**：连接多个节点，表达隐患、触发条件、违章行为、事故后果的因果关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别隐患（设备老化、防护缺失、管理漏洞、安全培训不足）
- 识别触发条件（点火源、静电、明火、高温）
- 识别违章行为（违章操作、违章指挥、违反劳动纪律）
- 识别事故后果（人员伤亡、设备损坏、环境污染、停产损失）
- 为实体指定严重程度

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位工业安全事故调查专家，请从已知实体列表中提取事故因果链条作为超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的事故相关实体
- **边 (Edge)**：连接多个节点，表达隐患、触发条件、违章行为、事故后果的因果关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 识别隐患积累过程
- 识别触发条件的作用
- 识别违章行为的促成作用
- 识别事故后果的扩展
- 建立完整的因果链条：隐患 → 触发条件 → 违章行为 → 事故后果
- 边的 nodes 字段应包含所有参与该因果链条的实体

"""

_PROMPT = """## 角色与任务
你是一位工业安全事故调查专家，请从事故调查报告中提取实体和事故因果链条作为超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的事故相关实体
- **边 (Edge)**：连接多个节点，表达隐患、触发条件、违章行为、事故后果的因果关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体

### 领域特定规则
- 识别隐患（设备老化、防护缺失、管理漏洞、安全培训不足）
- 识别触发条件（点火源、静电、明火、高温）
- 识别违章行为（违章操作、违章指挥、违反劳动纪律）
- 识别事故后果（人员伤亡、设备损坏、环境污染、停产损失）
- 建立完整的因果链条：隐患 → 触发条件 → 违章行为 → 事故后果

### 源文本:
"""


class IncidentCausalityMap(AutoHypergraph[IncidentEntity, IncidentCausalityEdge]):
    """
    适用文档: 事故调查报告、事故分析报告、
    风险评估报告。

    模板用于从事故调查报告中提取隐患、触发条件、违章行为、事故后果
    的因果关系，支持事故推演和风险预防分析。

    使用示例:
        >>> causality = IncidentCausalityMap(llm_client=llm, embedder=embedder)
        >>> doc = "管道腐蚀老化（隐患）导致泄漏，遇明火（触发条件）引发火灾..."
        >>> causality.feed_text(doc)
        >>> causality.show()
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
        初始化事故因果链超图模板。

        Args:
            llm_client (BaseChatModel): 用于因果关系提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoHypergraph 的其他参数。
        """
        super().__init__(
            node_schema=IncidentEntity,
            edge_schema=IncidentCausalityEdge,
            node_key_extractor=lambda x: x.name,
            nodes_in_edge_extractor=lambda x: x.nodes,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ) -> None:
        """
        使用 OntoSight 可视化事故因果链超图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的因果链条数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的因果链条数。默认 3。
        """

        def node_label_extractor(node: IncidentEntity) -> str:
            severity = f" [{node.severity}]" if node.severity else ""
            return f"{node.name} ({node.category}){severity}"

        def edge_label_extractor(edge: IncidentCausalityEdge) -> str:
            return edge.causality_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
