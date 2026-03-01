"""风险评估图谱 - 从企业披露文件中提取风险因子及其财务影响传导路径。

适用文档: SEC 10-K/10-Q Item 1A 风险因子、招股说明书风险部分、债券评级报告

功能介绍:
    提取风险因素、财务指标、运营结果等实体，以及它们之间的风险传导关系，
    支持结构化风险监测和多份财报的对比分析。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class RiskEntityNode(BaseModel):
    """
    风险评估图谱中的实体节点。
    """

    name: str = Field(description="实体名称。")
    category: str = Field(description="实体类别：'风险因素'、'财务指标'、'运营结果'。")
    description: Optional[str] = Field(
        None,
        description="实体的详细描述。",
    )


class RiskPropagationEdge(BaseModel):
    """
    风险因素到财务影响/运营结果的传导关系。
    """

    source: str = Field(description="源实体名称。")
    target: str = Field(description="目标实体名称。")
    relation_type: str = Field(
        description="关系类型：'导致'、'影响'、'提高'、'降低'、'改善'、'削弱' 等。"
    )
    transmission_mechanism: str = Field(description="传导机制说明。")
    likelihood: str = Field(description="发生可能性：高/中/低。")
    severity: Optional[str] = Field(
        None, description="影响严重程度：高/中/低，或量化影响。"
    )
    mitigation: Optional[str] = Field(
        None,
        description="缓解措施或应对策略。",
    )


_PROMPT = """## 角色与任务
你是一位专业的金融风险分析师，请从企业披露文件中提取风险因素、财务指标、运营结果等实体，以及它们之间的风险传导关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的风险因素、财务指标、运营结果等实体
- **边 (Edge)**：节点之间的风险传导关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别风险因素：运营风险、市场风险、财务风险、合规风险、外部风险
- 识别财务指标：营收、利润、毛利率、现金流等
- 识别运营结果：产能利用率、交付周期、客户流失率等
- 映射风险到财务影响的传导路径
- 提取发生可能性和影响严重程度
- 捕获管理层提及的缓解措施

## 源文本:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的金融风险分析师，请从企业披露文件中提取所有风险因素、财务指标、运营结果等实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的风险因素、财务指标、运营结果等实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 提取规则
- 识别风险因素：供应链中断、原材料价格波动、汇率变动等
- 识别财务指标：营业收入、净利润、毛利率、现金流等
- 识别运营结果：产能利用率、交付延迟、客户流失等
- 为每个实体标注正确的类别

## 源文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的金融风险分析师，请从给定实体列表中提取风险因素到财务影响/运营结果的传导关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的风险因素、财务指标、运营结果等实体
- **边 (Edge)**：节点之间的风险传导关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致
3. **关键**：边的 source 和 target 必须完全使用下方实体列表中的名称，不能创造新名称

### 提取规则
- 源实体通常是风险因素，目标实体是受影响的财务指标或运营结果
- 描述风险传导到目标的机制（如何影响）
- 提取发生可能性（高/中/低）
- 提取影响严重程度或量化影响
- 捕获提及的缓解措施或应对策略

## 已知实体列表：
{known_nodes}

## 源文本:
{source_text}
"""


class RiskAssessmentGraph(AutoGraph[RiskEntityNode, RiskPropagationEdge]):
    """
    适用文档: SEC 10-K/10-Q Item 1A 风险因子、招股说明书风险部分、
    债券评级报告、公司年报风险披露部分。

    模板用于系统性提取风险因素到财务影响的传导路径。通过分析企业披露文件，
    识别风险因素、财务指标、运营结果等实体，并映射它们之间的风险传导关系，
    支持风险监控和多报告期对比分析。

    使用示例:
        >>> risk_graph = RiskAssessmentGraph(llm_client=llm, embedder=embedder)
        >>> text = "原材料价格波动可能导致生产成本上升 10-15%，进而压缩毛利率。公司已采取套期保值措施..."
        >>> risk_graph.feed_text(text)
        >>> risk_graph.show()
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
        初始化风险评估图谱模板。

        Args:
            llm_client (BaseChatModel): 用于风险关系提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=RiskEntityNode,
            edge_schema=RiskPropagationEdge,
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
        使用 OntoSight 可视化风险评估图谱。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的传导关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的传导关系数。默认 3。
        """

        def node_label_extractor(node: RiskEntityNode) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: RiskPropagationEdge) -> str:
            return f"{edge.relation_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
