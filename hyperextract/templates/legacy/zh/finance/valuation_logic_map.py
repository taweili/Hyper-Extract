"""估值逻辑图谱 - 映射驱动股票表现的因果链。

提取股票研究报告中从业务驱动因素到估值结论的逻辑链
（例如 新市场 -> 增长 -> 估值倍数扩张）。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class ValuationDriver(BaseModel):
    """
    分析师估值逻辑链中的一个因素。
    """

    name: str = Field(
        description="估值驱动因素名称（例如 '市场份额增长'、'估值倍数扩张'、'DCF 假设'）。"
    )
    driver_type: str = Field(
        description="类型：'基本面'、'估值指标'、'增长驱动因素'、'可比公司'、'折现率'、'终值'。"
    )
    value: Optional[str] = Field(
        None,
        description="量化值或指标（例如 '25 倍前瞻市盈率'、'WACC 9.5%'、'TAM 150 亿美元'）。",
    )
    description: Optional[str] = Field(
        None,
        description="分析师对该驱动因素在估值中所起作用的解释。",
    )


class ValuationEdge(BaseModel):
    """
    分析师估值逻辑中的因果链接。
    """

    source: str = Field(description="原因或输入驱动因素名称。")
    target: str = Field(description="结果或输出驱动因素名称。")
    logic: str = Field(
        description="分析师连接源到目标的推理逻辑"
        "（例如 '更高的云计算采用率推动经常性收入增长'）。"
    )
    relation_type: str = Field(
        description="关系类型：'驱动'（正面）、'支撑'（正面）、'确认'（正面）、"
        "'抑制'（负面）、'限制'（负面）、'假设'（中性）、'关联'（中性）。"
    )
    confidence: Optional[str] = Field(
        None,
        description="分析师的确信度：'高'、'中等'、'低'。",
    )


_PROMPT = """## 角色与任务
你是一位专业的股票研究分析师，请从研究报告中提取估值逻辑链：即从业务基本面到估值结论的因果推理。

## 核心概念定义
- **节点 (Node)**：从文档中提取的估值驱动因素
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别基本面驱动因素、增长催化剂和估值指标
- 提取从业务驱动因素到目标价的因果链
- 捕获分析师在每个链接处的具体推理
- 记录关系类型：驱动/支撑/确认（正面）、抑制/限制（负面）、假设/关联（中性）

## 源文本:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的股票研究分析师，请从文本中提取所有估值驱动因素和指标作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的估值驱动因素

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 提取规则
- 识别基本面驱动因素（收入增长、市场份额、TAM）
- 识别估值指标（P/E、EV/EBITDA、DCF、可比倍数）
- 在提及时捕获量化值

## 源文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的股票研究分析师，请从给定驱动因素列表中提取连接它们的逻辑推理链。

## 核心概念定义
- **节点 (Node)**：从文档中提取的估值驱动因素
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 提取规则
- 将业务驱动因素连接到财务结果再到估值结论
- 捕获每个链接处的具体推理
- 记录关系类型：驱动/支撑/确认（正面）、抑制/限制（负面）、假设/关联（中性）

## 已知估值因素列表：
{known_nodes}

## 源文本:
{source_text}
"""


class ValuationLogicMap(AutoGraph[ValuationDriver, ValuationEdge]):
    """
    适用文档: 股票研究报告、首次覆盖报告、估值分析、分部加总分析、DCF 模型摘要。

    模板用于映射分析师估值逻辑中的因果链。将业务基本面连接到增长驱动因素，
    再到估值指标和目标价，支持投资策略映射和论点比较。

    使用示例:
        >>> valuation = ValuationLogicMap(llm_client=llm, embedder=embedder)
        >>> report = "云计算采用推动经常性收入，支撑 30 倍前瞻市盈率..."
        >>> valuation.feed_text(report)
        >>> valuation.show()
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
        初始化估值逻辑图谱模板。

        Args:
            llm_client (BaseChatModel): 用于估值逻辑提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=ValuationDriver,
            edge_schema=ValuationEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: (
                f"{x.source}--({x.relation_type})-->{x.target}"
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
        使用 OntoSight 可视化估值逻辑图谱。

        Args:
            top_k_nodes_for_search (int): 检索的驱动因素数。默认 3。
            top_k_edges_for_search (int): 检索的逻辑链接数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的驱动因素数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的逻辑链接数。默认 3。
        """

        def node_label_extractor(node: ValuationDriver) -> str:
            val = f": {node.value}" if node.value else ""
            return f"{node.name}{val}"

        def edge_label_extractor(edge: ValuationEdge) -> str:
            return f"{edge.relation_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
