"""财务数据时序图谱 - 跨报告期追踪财务指标变化。

从 SEC 申报文件中提取财务实体（公司、分部、科目）及其跨期的
量化关系，支持多期趋势分析、分部级追踪和跨期财务对比。
"""

from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class FinancialDataEntity(BaseModel):
    """
    SEC 申报文件中出现的财务实体：公司、业务分部或财务指标/科目。
    """

    name: str = Field(
        description="实体的规范名称（例如 '苹果公司'、'云服务分部'、'营业收入'、'净利润'）。"
    )
    entity_type: str = Field(
        description="类型：'公司'、'分部'、'财务指标'、'会计科目'、'外部因素'。"
    )
    description: Optional[str] = Field(
        None,
        description="简要背景说明（例如 '消费电子业务板块'、'GAAP 收入确认口径'）。",
    )


class FinancialDataEdge(BaseModel):
    """锚定于特定报告期的时序财务关系，将实体与指标、指标与指标关联起来。"""

    source: str = Field(
        description="主体（公司/分部/指标名称）"
    )
    target: str = Field(
        description="目标（指标/分部/因素名称）"
    )
    relationship: str = Field(
        description="关系类型：'拥有'、'同比变化'、'占比'、'贡献'、'影响'"
    )
    value: Optional[str] = Field(
        None,
        description="数值（如 '3943亿美元'、'+7.8%'、'30%'）"
    )
    fiscal_period: Optional[str] = Field(
        None,
        description="财务期间（如 'FY2024'、'Q3 2024'）"
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = """## 角色与任务
你是一位专业的财务分析师，请从文本中提取财务实体及其跨时间的量化关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系
- **时间**：财务数据所属的财务期间

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 将公司、业务分部和财务指标/会计科目识别为实体
- 对每个报告数据，创建连接报告主体与指标的边，附带精确数值和财务期间
- 将同比变化、衍生比率和分部贡献分别作为独立的边提取
- 保留源文本中的精确金额和单位
- 统一使用一致的财务期间标签（例如 'FY2024'、'Q3 2024'）
- 在可获取时提取多期对比数据
- 不要计算文本中未明确给出的数值

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月
   - "本季度" → {observation_time} 所在季度
   - "FY2024" → 2024财年

2. 精确时间 → 保持原样
3. 时间缺失 → 留空，不要猜测

### 源文本:
"""

_NODE_PROMPT = """## 角色
你是专业的财务分析师，从文本中提取财务实体作为节点。

## 提取规则
### 核心约束
1. 每个节点对应一个独立实体
2. 实体名称与原文保持一致
3. **重要**：提取的节点名称要完整准确，因为边会引用这些名称

### 只提取以下类型的实体：
- **公司**：申报公司及其重要子公司
- **分部**：业务分部或区域（具体名称）
- **财务指标**：关键财务指标（营业收入、净利润、毛利率等）
- **会计科目**：主要会计科目
- **外部因素**：影响财务的外部因素

### 不提取为节点：
- 日期、时间期间
- 纯数值

### 提取原则
- 公司名使用完整官方名称（如 '苹果公司' 而非 '苹果'）
- 财务指标使用标准名称（如 '营业收入' 而非 '收入'）
- 避免提取过于通用或抽象的概念

## 源文本:
"""

_EDGE_PROMPT = """## 角色
你是专业的财务分析师，从文本中提取带时间上下文的财务数据关系。

## 核心约束
1. **source 和 target 都必须是已知实体列表中的节点**
2. 每个出现的财务数据都必须提取为一条边
3. 节点名称必须完全匹配

## 关系类型（有区分度的类型）
- "拥有"：公司拥有某分部/子公司
- "同比变化"：同比增加/减少（如 "营收同比增长7.8%"）
- "占比"：某指标占某指标的比例（如 "云服务收入占比30%"）
- "贡献"：某分部贡献了某指标的多少（如 "华东区贡献收入20%"）
- "影响"：外部因素影响了某指标（如 "汇率影响收入-5%"）

## 输出格式
每条边必须包含：
- source: 主体（节点名称）
- target: 目标（节点名称）
- relationship: 关系类型
- value: 数值（必须）
- fiscal_period: 财务期间

## 源文本:
"""

# ==============================================================================
# 3. 模板类
# ==============================================================================


class FinancialDataTemporalGraph(
    AutoTemporalGraph[FinancialDataEntity, FinancialDataEdge]
):
    """
    适用文档: SEC 10-K 年度报告、10-Q 季度报告、20-F 外国发行人年报、
    包含多期财务报表的年度报告、分部披露。

    模板用于从 SEC 申报文件构建财务数据时序知识图谱。
    与 FilingFinancialSnapshot（单期扁平提取）不同，本模板保留了**时间维度**——
    将公司、业务分部和财务指标建模为节点，通过带有精确数值和财务期间标签的
    时序边进行连接，支持多期趋势分析和跨期对比。

    使用示例:
        >>> graph = FinancialDataTemporalGraph(llm_client=llm, embedder=embedder)
        >>> filing = "2024年度，苹果公司报告营收3943亿美元，较FY2023年的3658亿美元增长7.8%..."
        >>> graph.feed_text(filing)
        >>> graph.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: str | None = None,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化财务数据时序图谱模板。

        Args:
            llm_client (BaseChatModel): 用于财务数据提取的 LLM。
            embedder (Embeddings): 用于去重和语义检索的嵌入模型。
            observation_time (str): 用于解析相对时间表达式的参考日期，未指定时默认为当前日期。
            extraction_mode (str): "one_stage" 或 "two_stage"（默认 "two_stage"）。
            chunk_size (int): 每个文本分块的最大字符数。
            chunk_overlap (int): 相邻分块之间的重叠字符数。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoTemporalGraph 的其他参数。
        """
        if observation_time is None:
            observation_time = datetime.now().strftime("%Y-%m-%d")

        super().__init__(
            node_schema=FinancialDataEntity,
            edge_schema=FinancialDataEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: (
                f"{x.source}|{x.relationship}|{x.target}"
            ),
            time_in_edge_extractor=lambda x: x.fiscal_period or "",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
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
        使用 OntoSight 可视化财务数据时序图谱。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的数据边数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的数据边数。默认 3。
        """

        def node_label_extractor(node: FinancialDataEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: FinancialDataEdge) -> str:
            if edge.value is None:
                return f"{edge.relationship}"
            return f"{edge.relationship} ({edge.value})"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
