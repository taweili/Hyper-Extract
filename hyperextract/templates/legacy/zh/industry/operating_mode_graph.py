"""工况切换图谱 - 提取工况类型和切换条件，识别不同工况之间的切换条件和步骤。

适用于运行规程、设备操作手册、工况切换说明书等文本。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class ModeEntity(BaseModel):
    """工况实体，包括工况和条件。"""

    name: str = Field(description="实体名称（如：自动运行模式、手动调试模式、待机模式、紧急停止模式、按下启动按钮、按下停止按钮、发生故障等）。")
    category: str = Field(description="类别：工况、条件。工况如自动运行、手动调试、待机等；条件如启动按钮、停止按钮、故障信号等。")
    description: Optional[str] = Field(default=None, description="对该实体的描述。")
    load_range: Optional[str] = Field(default=None, description="负荷范围（如：0-50%、50-80%、80-100%等），仅对工况类别有效。")


class ModeTransition(BaseModel):
    """工况与工况之间的切换关系，或条件与工况之间的触发关系。"""

    source: str = Field(description="源实体名称（工况或条件）。")
    target: str = Field(description="目标实体名称（工况或条件）。")
    relationType: str = Field(description="关系类型：切换到、触发。")
    transition_condition: Optional[str] = Field(default=None, description="切换条件（如：按下启动按钮、按下停止按钮、发生故障等）。")
    transition_procedure: Optional[str] = Field(default=None, description="切换步骤。")


_NODE_PROMPT = """## 角色与任务
你是一位工业设备工况分析专家，请从文本中提取所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括工况（如自动运行、待机）和条件（如启动按钮、故障）
- **边 (Edge)**：工况之间的切换关系或条件对工况的触发关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别工况名称（如自动运行模式、手动调试模式、待机模式、紧急停止模式等）
- 识别条件名称（如按下启动按钮、按下停止按钮、发生故障、恢复正常等）
- 为每个实体指定类别（工况/条件）
- 记录每种工况的负荷范围

## 运行规程文档:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取工况与条件之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：工况之间的切换关系或条件对工况的触发关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 识别工况之间的切换关系（源工况 切换到 目标工况）
- 识别条件对工况的触发关系（条件 触发 目标工况）
- 关系类型使用 切换到 或 触发

## 已知实体列表:
{known_nodes}

## 运行规程文档:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位工业设备工况分析专家，请从文本中提取工况和条件实体，以及它们之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括工况（如自动运行、待机）和条件（如启动按钮、故障）
- **边 (Edge)**：工况之间的切换关系或条件对工况的触发关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别各种运行模式（工况），如自动运行、手动调试、待机、紧急停止等
- 识别各种触发条件，如按下启动按钮、按下停止按钮、发生故障等
- 识别每种工况的适用条件和负荷范围
- 提取工况之间的切换关系（切换到）
- 提取条件触发工况的关系（触发）

## 运行规程文档:
{source_text}
"""


class OperatingModeGraph(AutoGraph[ModeEntity, ModeTransition]):
    """
    适用文档: 运行规程、设备操作手册、工况切换说明书

    功能介绍:
    从运行规程中提取工况类型和切换条件，识别不同工况之间的切换条件和步骤。

    Example:
        >>> template = OperatingModeGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("设备有两种运行模式：自动模式和手动模式。按下启动按钮从待机切换到自动模式...")
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
        初始化工况切换图谱模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            chunk_size: 每个分块的最大字符数，默认为 2048
            chunk_overlap: 分块之间的重叠字符数，默认为 256
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=ModeEntity,
            edge_schema=ModeTransition,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
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
    ):
        """
        展示工况切换图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: ModeEntity) -> str:
            load = f" [{node.load_range}]" if node.load_range else ""
            return f"{node.name} ({node.category}){load}"

        def edge_label_extractor(edge: ModeTransition) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
