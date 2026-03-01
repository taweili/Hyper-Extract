"""因子影响超图 - 建模股票分析中的多因子关系。

将宏观因素、行业趋势和公司指标之间的复杂关系建模为
同时连接多个因子的超边，节点是因子，超边是结果。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class FactorNode(BaseModel):
    """因子节点"""

    name: str = Field(description="因子名称")
    category: str = Field(description="因子类别：宏观、行业、公司、市场情绪")
    description: str = Field(description="因子描述/说明", default="")


class FactorResult(BaseModel):
    """因子结果超边"""

    result: str = Field(
        description="结果/影响，如'业绩下滑'、'估值提升'、'价格上涨'，不超过10字"
    )
    factors: List[str] = Field(description="导致该结果的因子列表（至少2个）")
    description: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的金融多因子分析师，请从文本中提取因子（作为节点）和因子导致的结果（作为超边）。

## 核心概念定义
- **节点 (Node)**：从文档中提取的因子实体
- **超边 (Edge)**：由多个因子共同导致的结果

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的因子，禁止将多个因子合并为一个节点
2. 因子名称与原文保持一致
3. 每条超边必须连接2个或以上因子
4. **优先提取包含3个及以上因子的超边**

### 因子类别
- 宏观：GDP增速、CPI、PPI、利率、汇率等
- 行业：景气度、政策、供需格局等
- 公司：营收、ROE、PE、净利润等
- 市场情绪：资金流向、风险偏好等

### 结果类型
- 业绩类：业绩下滑、业绩增长、盈利提升等
- 估值类：估值提升、估值承压、市值增长等
- 价格类：价格上涨、股价下跌、成本上升等
- 需求类：需求旺盛、需求疲软、订单增加等

## 源文本:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的金融因子分析师，请从文本中提取所有因子作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的因子实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的因子，禁止将多个因子合并为一个节点
2. 因子名称与原文保持一致

### 因子类别
- 宏观：GDP、CPI、利率、汇率等
- 行业：景气度、政策、供需等
- 公司：营收、ROE、PE等
- 市场情绪：资金流向、风险偏好等

## 源文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的金融多因子分析师，请从已知因子列表中提取因子导致的结果。

## 核心概念定义
- **节点 (Node)**：从文档中提取的因子实体
- **超边 (Edge)**：由多个因子共同导致的结果

## 提取规则
### 核心约束
1. 仅从已知因子列表中提取超边，不要创建未列出的因子
2. 每条超边必须连接至少2个因子
3. 优先提取包含3个及以上因子的超边
4. 结果描述不超过10字

### 结果类型
- 业绩类：业绩下滑、业绩增长、盈利提升
- 估值类：估值提升、估值承压、市值增长
- 价格类：价格上涨、股价下跌、成本上升
- 需求类：需求旺盛、需求疲软

### 已知实体列表：
{known_nodes}

## 源文本:
{source_text}
"""


class FactorInfluenceHypergraph(AutoHypergraph[FactorNode, FactorResult]):
    """
    适用文档: 股票分析报告、券商研报、财报解读

    功能介绍:
    将宏观因素、行业趋势和公司指标（作为节点）与它们导致的结果（作为超边）
    建模为超图结构。

    Example:
        >>> template = FactorInfluenceHypergraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("受宏观利率上行和行业景气度下行影响，公司净利润下降...")
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
        初始化因子影响超图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage" 或 "two_stage"，默认为 "two_stage"
            chunk_size: 每个分块的最大字符数，默认为 2048
            chunk_overlap: 分块之间的重叠字符数，默认为 256
            max_workers: 并行处理工作线程数，默认为 10
            verbose: 是否启用进度日志，默认为 False
            **kwargs: 其他技术参数
        """
        super().__init__(
            node_schema=FactorNode,
            edge_schema=FactorResult,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.result}_{'_'.join(sorted(x.factors))}",
            nodes_in_edge_extractor=lambda x: tuple(x.factors),
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
    ):
        """
        展示因子影响超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量
            top_k_edges_for_search: 语义检索返回的边数量
            top_k_nodes_for_chat: 问答使用的节点数量
            top_k_edges_for_chat: 问答使用的边数量
        """

        def node_label_extractor(node: FactorNode) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: FactorResult) -> str:
            return f"{edge.result}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
