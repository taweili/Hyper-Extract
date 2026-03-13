"""事故时序图 - 从事故调查报告中提取时间线，还原事故发生前后的操作与响应序列。

适用于事故报告、事故调查报告、安全事件记录等文本。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph


class SafetyTimelineEntity(BaseModel):
    """事故时序图中的实体节点。"""

    name: str = Field(description="实体名称")
    entity_type: str = Field(description="类型：人员、设备、设施等")
    description: Optional[str] = None


class SafetyTimelineEdge(BaseModel):
    """事故时序图中的时间边。"""

    source: str = Field(description="源实体名称")
    target: str = Field(description="目标实体名称")
    action: str = Field(description="操作动作")
    timestamp: Optional[str] = Field(None, description="动作发生时间")
    location: Optional[str] = Field(None, description="发生位置")
    status: Optional[str] = Field(None, description="状态描述")


_PROMPT = """## 角色与任务
你是一位工业安全事故调查专家，请从事故调查报告中提取时间线，还原事故发生前后的操作与响应序列。

## 核心概念定义
- **节点 (Node)**：从文档中提取的参与事故的人员、设备、位置等实体
- **边 (Edge)**：时间序列中的操作动作
- **时间**：操作发生的时间点

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别事故相关人员（操作工、班组长、安全员、管理人员）
- 识别相关设备（泵、电机、阀门、仪表）
- 识别操作动作（启动、停止、巡检、维修、发现异常）
- 识别环境状态（正常、异常、报警、危险）

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "事故前30分钟" → {observation_time} 前30分钟
   - "当天上午" → {observation_time} 当天上午
   - "随后" → 接续前一事件

2. 精确时间 → 保持原样
3. 时间缺失 → 留空，不要猜测

## 事故调查报告:
{source_text}
"""

_NODE_PROMPT = """## 角色
你是工业安全事故调查专家，从事故调查报告中提取参与事故的实体作为节点。

## 提取规则
### 核心约束
1. 每个节点对应一个独立实体
2. 实体名称与原文保持一致

### 提取范围
- 人员、设备、设施、岗位、位置等

## 事故调查报告:
{source_text}
"""

_EDGE_PROMPT = """## 角色
你是工业安全事故调查专家，从已知实体列表中提取事故时间线中的操作动作。

## 核心约束
1. **source 和 target 都必须是已知实体列表中的节点**
2. 每个操作动作都必须提取为一条边
3. 节点名称必须完全匹配

## 操作类型
- 启动、停止、开启、关闭
- 巡检、检查、排查
- 维修、检修、保养
- 发现、识别、报告
- 操作、使用、触发

## 输出格式
每条边必须包含：
- source: 源实体（节点名称）
- target: 目标实体（节点名称）
- action: 操作动作
- timestamp: 动作发生时间
- location: 发生位置
- status: 状态

# 已知实体列表：
{known_nodes}

## 事故调查报告:
{source_text}
"""


class SafetyTimeline(AutoTemporalGraph[SafetyTimelineEntity, SafetyTimelineEdge]):
    """
    适用文档: 事故调查报告、安全事件记录、
    事件分析报告。

    模板用于从事故调查报告中提取时间线，
    还原事故发生前后的操作与响应序列，
    支持事故复盘和原因分析。

    使用示例:
        >>> timeline = SafetyTimeline(llm_client=llm, embedder=embedder)
        >>> report = "14:30，操作工启动离心泵P-101；14:35，发现异常振动..."
        >>> timeline.feed_text(report)
        >>> timeline.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: str = "2024-01-01",
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化事故时序图模板。

        Args:
            llm_client (BaseChatModel): 用于时序提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            observation_time (str): 用于解析相对日期的参考时间。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoTemporalGraph 的其他参数。
        """
        super().__init__(
            node_schema=SafetyTimelineEntity,
            edge_schema=SafetyTimelineEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: (
                f"{x.source}|{x.action}|{x.target}"
            ),
            time_in_edge_extractor=lambda x: x.timestamp or "",
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
        使用 OntoSight 可视化事故时序图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的事件数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的事件数。默认 3。
        """

        def node_label_extractor(node: SafetyTimelineEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: SafetyTimelineEdge) -> str:
            date = f" [{edge.timestamp}]" if edge.timestamp else ""
            return f"{edge.action}{date}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
