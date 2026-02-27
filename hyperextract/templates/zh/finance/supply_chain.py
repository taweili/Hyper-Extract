"""供应链图谱 - 从 SEC 申报文件中提取供应链实体及其关系。

适用文档: 10-K 财报业务概览部分、供应商审计报告、ESG 报告

功能介绍:
    映射企业供应链依赖和伙伴关系，支持识别关键供应商、
    地缘政治敞口和供应链韧性风险。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class SupplyEntity(BaseModel):
    """
    供应链中的参与者（公司、供应商、客户、分销商）。
    """

    name: str = Field(description="实体名称（公司或供应商）。")
    entity_type: str = Field(
        description='类型："客户"、"供应商"、"战略伙伴"、"分销商"、"本公司"。'
    )
    details: Optional[str] = Field(None, description="地理管辖区、认证信息及合规说明。")


class SupplyTransaction(BaseModel):
    """
    实体间的供应链关系。
    """

    source: str = Field(description="上游供应商或提供方。")
    target: str = Field(description="下游买方或需求方。")
    relationship_type: str = Field(
        description='类型："供应"、"采购"、"分销"、"战略合作"。'
    )
    product_service: str = Field(
        description='被供应或交易的内容，例如"锂芯片"、"物流服务"等。'
    )


_PROMPT = """## 角色与任务
你是一位专业的供应链分析师，请从文本中提取供应链实体及其关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的供应链参与者
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别供应商、客户和伙伴
- 提取交易类型及产品
- 将依赖度、交易量及地缘政治风险汇总至 risk_assessment

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的供应链分析师，请从文本中提取所有供应链参与者作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的供应链参与者

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 提取规则
- 识别公司及合作伙伴
- 分类角色（客户、供应商、战略伙伴、分销商）
- 记录地区及认证至 details

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的供应链分析师，请从给定参与者列表中提取交易关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的供应链参与者
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 提取规则
- 通过产品/服务连接实体
- 综合评估依赖度、交易量及风险（关税、单一来源）

"""


class SupplyChainGraph(AutoGraph[SupplyEntity, SupplyTransaction]):
    """
    适用文档: 10-K 财报中的业务概览部分、供应商审计报告、供应链韧性披露（10-K Item 1A）、环境社会治理报告、供应商管理文件。

    模板用于映射企业供应链依赖和伙伴关系。支持识别关键供应商、地缘政治敞口和供应链韧性风险。

    使用示例:
        >>> supply_chain = SupplyChainGraph(llm_client=llm, embedder=embedder)
        >>> filing = "供应商 XYZ 提供我们 70% 的零部件。我们还依赖于..."
        >>> supply_chain.feed_text(filing)
        >>> supply_chain.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化供应链图谱模板。

        Args:
            llm_client (BaseChatModel): 用于实体和关系提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=SupplyEntity,
            edge_schema=SupplyTransaction,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: (
                f"{x.source}--({x.product_service})-->{x.target}"
            ),
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
    ) -> None:
        """
        使用 OntoSight 可视化供应链图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的关系数。默认 3。
        """

        def node_label_extractor(node: SupplyEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: SupplyTransaction) -> str:
            return f"{edge.relationship_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
