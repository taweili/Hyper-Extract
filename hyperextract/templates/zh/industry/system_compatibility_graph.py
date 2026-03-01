"""系统兼容性超图 - 从技术规格书中提取设备与环境、介质的对应关系。

适用于选型辅助、设备匹配分析、技术规格书等文本。
"""

from typing import Optional, Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class CompatibilityEntity(BaseModel):
    """
    系统兼容性实体节点。
    """

    name: str = Field(
        description="实体名称（例如：离心泵P-101、不锈钢304、高温环境等）。"
    )
    category: str = Field(description="类型：设备、材质、介质、环境、连接方式。")
    description: Optional[str] = Field(
        None, description="描述（例如：15kW离心泵、适用于清水、适用于常温）。"
    )


class CompatibilityEdge(BaseModel):
    """
    系统兼容性超边，连接多个实体。
    """

    nodes: List[str] = Field(
        description="参与兼容性关系的节点列表：[设备, 材质/介质/环境1, 材质/介质/环境2, ...]"
    )
    compatibility_type: str = Field(
        description="兼容性类型：材质兼容、介质适用、环境适用、连接匹配。"
    )
    compatibility_note: Optional[str] = Field(
        None, description="兼容性说明或限制条件（例如：需加装过滤器、建议使用O型圈）。"
    )


_NODE_PROMPT = """## 角色与任务
你是一位工业设备选型专家，请从技术规格书中提取所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的设备、材质、介质、环境等实体
- **边 (Edge)**：连接多个节点，表达设备与环境、介质的兼容性关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别设备（离心泵、压缩机、阀门、换热器）
- 识别材质（不锈钢304、铸铁、铝合金、碳钢）
- 识别介质（清水、污水、油品、酸碱溶液）
- 识别环境（高温环境、低温环境、防爆区域、腐蚀性环境）
- 识别连接方式（法兰连接、螺纹连接、焊接）

## 技术规格书:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
你是一位工业设备选型专家，请从已知实体列表中提取设备与环境、介质的兼容性关系作为超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的设备、材质、介质、环境等实体
- **边 (Edge)**：连接多个节点，表达设备与环境、介质的兼容性关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 识别设备与材质的兼容性（不锈钢泵适用于清水）
- 识别设备与介质的适用性（化工泵适用于酸碱溶液）
- 识别设备对环境的要求（防爆电机适用于防爆区域）
- 识别连接方式的匹配
- 边的 nodes 字段应包含所有参与该兼容性关系的实体

## 已知实体列表:
{known_nodes}

## 技术规格书:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位工业设备选型专家，请从技术规格书中提取实体和设备与环境、介质的兼容性关系作为超边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的设备、材质、介质、环境等实体
- **边 (Edge)**：连接多个节点，表达设备与环境、介质的兼容性关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体

### 领域特定规则
- 识别设备（离心泵、压缩机、阀门、换热器）
- 识别材质（不锈钢304、铸铁、铝合金、碳钢）
- 识别介质（清水、污水、油品、酸碱溶液）
- 识别环境（高温环境、低温环境、防爆区域、腐蚀性环境）
- 识别连接方式（法兰连接、螺纹连接、焊接）
- 建立设备与材质、介质、环境的兼容性关系

## 技术规格书:
{source_text}
"""


class SystemCompatibilityGraph(AutoHypergraph[CompatibilityEntity, CompatibilityEdge]):
    """
    适用文档: 技术规格书、设备选型手册、
    产品数据表。

    模板用于从技术规格书中提取设备与环境、介质的对应关系，
    支持选型辅助和设备匹配分析。

    使用示例:
        >>> compat = SystemCompatibilityGraph(llm_client=llm, embedder=embedder)
        >>> doc = "离心泵适用于清水、污水及类似介质，材质为不锈钢304..."
        >>> compat.feed_text(doc)
        >>> compat.show()
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
        初始化系统兼容性超图模板。

        Args:
            llm_client (BaseChatModel): 用于兼容性提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoHypergraph 的其他参数。
        """
        super().__init__(
            node_schema=CompatibilityEntity,
            edge_schema=CompatibilityEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.compatibility_type}_{sorted(x.nodes)}",
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
        使用 OntoSight 可视化系统兼容性超图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的兼容性关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的兼容性关系数。默认 3。
        """

        def node_label_extractor(node: CompatibilityEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: CompatibilityEdge) -> str:
            return edge.compatibility_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
