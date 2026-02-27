"""因子影响超图 - 建模股票分析中的多因子关系。

将宏观因素、行业趋势和公司指标之间的复杂关系建模为
同时连接多个因子的超边。
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class InvestmentFactor(BaseModel):
    """
    多因子投资分析中的一个因子。
    """

    name: str = Field(
        description="因子名称（例如 'GDP 增长'、'半导体周期'、'云计算收入'）。"
    )
    factor_level: str = Field(description="层级：'宏观'、'行业'、'公司'、'技术面'。")
    current_reading: Optional[str] = Field(
        None,
        description="当前值或状态（例如 '同比 3.2%'、'上升周期'、'加速增长'）。",
    )
    description: Optional[str] = Field(None, description="该因子重要性的说明。")


class FactorInteraction(BaseModel):
    """
    多因子交互关系，多个因子共同影响一个结果。
    """

    interaction_name: str = Field(
        description="交互关系的描述性名称（例如 'AI 资本支出乘数效应'、'利率敏感型轮动'）。"
    )
    participating_factors: List[str] = Field(
        description="参与此交互关系的所有因子名称。"
    )
    interaction_type: str = Field(
        description="类型：'增强型'、'抵消型'、'条件型'、'级联型'、'阈值型'。"
    )
    outcome: str = Field(
        description="综合结果或效应（例如 '云计算公司收入增长加速'）。"
    )
    mechanism: Optional[str] = Field(
        None,
        description="各因子如何相互作用产生该结果的机制。",
    )
    confidence: Optional[str] = Field(
        None,
        description="分析师对此交互关系的确信度：'高'、'中等'、'低'。",
    )


_PROMPT = """## 角色与任务
你是一位专业的量化基本面研究分析师，请从研究报告中提取投资因子及其多因子交互关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的投资因子
- **边 (Edge)**：连接多个节点的超边，表达多个实体间的复杂关联关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别宏观、行业和公司层面的因子
- 提取多个因子共同产生结果的复杂交互关系
- 超边连接所有参与因子，而非仅成对连接
- 捕获每个交互关系的机制和结果

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的量化基本面研究分析师，请从文本中提取所有投资因子作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的投资因子

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 提取规则
- 识别宏观指标、行业指标和公司关键绩效指标
- 捕获当前值或读数
- 按层级对每个因子进行分类

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的量化基本面研究分析师，请从给定因子列表中提取多因子交互关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的投资因子
- **边 (Edge)**：连接多个节点的超边，表达多个实体间的复杂关联关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 提取规则
- 每条超边应连接 2 个或更多因子
- 描述交互机制和结果
- 对交互类型进行分类

"""


class FactorInfluenceHypergraph(AutoHypergraph[InvestmentFactor, FactorInteraction]):
    """
    适用文档: 多因子研究报告、量化基本面分析、宏观策略笔记、跨资产研究、因子归因研究。

    模板用于建模股票分析中的复杂多因子关系。使用超边捕获多个因子共同影响结果的
    交互关系，超越简单的成对关系。

    使用示例:
        >>> factors = FactorInfluenceHypergraph(llm_client=llm, embedder=embedder)
        >>> report = "利率上升叠加强劲 GDP 和 AI 资本支出，推动向优质成长股轮动..."
        >>> factors.feed_text(report)
        >>> factors.show()
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
        初始化因子影响超图模板。

        Args:
            llm_client (BaseChatModel): 用于因子提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoHypergraph 的其他参数。
        """
        super().__init__(
            node_schema=InvestmentFactor,
            edge_schema=FactorInteraction,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.interaction_name,
            nodes_in_edge_extractor=lambda x: tuple(
                f for f in x.participating_factors
            ),
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
        使用 OntoSight 可视化因子影响超图。

        Args:
            top_k_nodes_for_search (int): 检索的因子数。默认 3。
            top_k_edges_for_search (int): 检索的交互关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的因子数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的交互关系数。默认 3。
        """

        def node_label_extractor(node: InvestmentFactor) -> str:
            reading = f": {node.current_reading}" if node.current_reading else ""
            return f"{node.name} [{node.factor_level}]{reading}"

        def edge_label_extractor(edge: FactorInteraction) -> str:
            return f"[{edge.interaction_type}] {edge.interaction_name}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
