"""作物生长周期图 - 从农业技术手册中提取作物各生长阶段的农事操作与环境要求。

适用于农业技术手册、作物栽培技术规程、种植技术指南。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph


class CropGrowthNode(BaseModel):
    """作物生长周期节点"""

    name: str = Field(description="节点名称")
    category: str = Field(description="节点类型：生长阶段、农事操作、环境条件")
    description: str = Field(description="详细描述")


class CropGrowthEdge(BaseModel):
    """作物生长周期边（时序边）"""

    source: str = Field(description="源节点")
    target: str = Field(description="目标节点")
    time: str = Field(description="时间点或时间段")
    description: str = Field(description="关系描述")


_PROMPT = """## 角色与任务
你是一位专业的农业技术专家，请从农业技术手册中提取作物生长周期图。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括生长阶段、农事操作、环境条件等
- **边 (Edge)**：节点之间的时间顺序关系
- **时间**：作物生长阶段的时间点或时间段

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 边提取
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 时间提取指引
农业技术手册中，时间信息通常出现在以下位置：
1. **时间范围描述**：如"4月上旬至4月中旬"、"从出苗到3叶1心期，一般持续15-20天"
2. **生长阶段名称**：生长阶段本身包含时间语义，如"播种期"、"幼苗期"、"分蘖期"、"孕穗抽穗期"、"灌浆成熟期"
3. **相对时间表达**：如"播种后5-7天"、"移栽后5-7天"、"移栽后5-7天"
4. **农事操作时间**：如"2叶1心期每亩施尿素"、"倒2叶露尖时每亩施尿素"

### 领域特定规则
- 生长阶段：播种期、幼苗期、分蘖期、孕穗抽穗期、灌浆成熟期
- 农事操作：苗床准备、种子处理、移栽、水肥管理、病虫害防治
- 环境条件：温度、湿度、光照、水分

### 时间解析规则
当前观察日期: {observation_time}

1. 精确时间 → 保持原样，如"4月上旬"、"3叶1心期"、"分蘖期"
2. 生长阶段 → 视为时间标记，如"幼苗期"、"分蘖期"直接作为时间
3. 相对时间解析（基于观察日期）:
   - "播种后5-7天" → 相对于播种期的时间偏移
   - "移栽后5-7天" → 相对于移栽期的时间偏移
4. 时间缺失 → 留空，不要猜测

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的农业技术专家，请从文本中提取所有作物生长周期相关节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 生长阶段：如播种期、幼苗期、分蘖期、孕穗抽穗期、灌浆成熟期
- 农事操作：如苗床准备、种子处理、移栽、施肥、病虫害防治
- 环境条件：如温度、湿度、光照、水分要求

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知节点列表中提取作物生长阶段之间的时间顺序关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的农业实体（生长阶段、农事操作、环境条件）
- **边 (Edge)**：节点之间的时间顺序关系
- **时间**：作物生长阶段的时间点或时间段

## 提取规则
### 核心约束
1. 仅从已知实体列表中选择源节点和目标节点，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 时间提取指引
从文本的以下位置提取时间信息：
1. **明确的时间范围**：如"4月上旬至4月中旬"、"一般持续25-35天"
2. **生长阶段名称**：如"播种期"、"幼苗期"、"分蘖期"本身包含时间信息
3. **农事操作的时间标记**：如"2叶1心期"、"倒2叶露尖时"
4. **相对时间表达**：如"移栽后5-7天"

### 时间优先级
1. 精确日期/时间段 > 生长阶段名称 > 相对时间偏移 > 空
2. 同一文本中有多个时间表达时，选择最精确的一个
3. 时间缺失 → 留空，不要猜测

### 时间解析规则
当前观察日期: {observation_time}

1. 精确时间 → 保持原样，如"4月上旬"
2. 生长阶段名称 → 直接作为时间，如"幼苗期"、"分蘖期"
3. 相对时间解析（基于观察日期）:
   - "播种后5-7天" → 相对于播种期的时间偏移
   - "移栽后5-7天" → 相对于移栽期的时间偏移
4. 时间缺失 → 留空，不要猜测

"""


class CropGrowthCycle(AutoTemporalGraph[CropGrowthNode, CropGrowthEdge]):
    """
    适用文档: 农业技术手册、作物栽培技术规程、种植技术指南

    功能介绍:
    以时间为轴，提取作物各生长阶段（播种、分蘖、成熟等）对应的关键农事操作
    与环境要求，构建作物生长周期知识图谱。
    适用于种植日历生成、农事任务规划、智慧农业决策。

    Example:
        >>> template = CropGrowthCycle(llm_client=llm, embedder=embedder)
        >>> template.feed_text("水稻播种期在4月上旬，播种前需要进行种子处理...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        observation_time: str | None = None,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化作物生长周期图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            observation_time: 观察时间，用于解析相对时间表达，
                如未指定则使用当前日期
            chunk_size: 每个分块的最大字符数，默认为 2048
            chunk_overlap: 分块之间的重叠字符数，默认为 256
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=CropGrowthNode,
            edge_schema=CropGrowthEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.time}|{x.target}",
            time_in_edge_extractor=lambda x: x.time,
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
    ):
        """
        展示作物生长周期图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: CropGrowthNode) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: CropGrowthEdge) -> str:
            return f"{edge.time}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
