"""安全管控图谱 - 提取危险源、风险点和管控措施，构建安全管控关系，识别安全风险与管控责任的对应关系。

适用于安全规程、安全风险评估报告、职业健康安全手册等文本。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class SafetyEntity(BaseModel):
    """安全管控实体，包括危险源、风险点、管控措施、责任人等。"""

    name: str = Field(description="实体名称（如：数控加工中心、烫伤风险、佩戴防护用品、安全主管等）。")
    category: str = Field(description="类别：危险源、风险点、管控措施、责任人。")
    description: Optional[str] = Field(default=None, description="对该实体的描述。")
    risk_level: Optional[str] = Field(default=None, description="风险等级：重大风险、较大风险、一般风险，仅对风险点类别有效。")


class SafetyRelation(BaseModel):
    """安全管控关系。"""

    source: str = Field(description="源实体名称（危险源或风险点或管控措施）。")
    target: str = Field(description="目标实体名称（风险点或管控措施或责任人）。")
    relationType: str = Field(description="关系类型：导致、需要、管控、负责。")
    hazard_factor: Optional[str] = Field(default=None, description="危险因素（如：高温部件、旋转部件、高压液体等）。")
    possible_consequence: Optional[str] = Field(default=None, description="可能导致后果（如：烫伤、机械伤害、触电等）。")


_NODE_PROMPT = """## 角色与任务
你是一位工业安全管理分析专家，请从文本中提取所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括危险源、风险点、管控措施、责任人
- **边 (Edge)**：安全管控关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 识别危险源名称（如数控加工中心、工业机械臂、冷却系统、液压站、电气控制柜等）
- 识别风险点名称（如烫伤风险、机械伤害风险、触电风险、摔伤风险等）
- 识别管控措施名称（如佩戴防护用品、设置安全围栏、定期检修、通风换气等）
- 识别责任人名称（如安全主管、设备负责人、班组长、电工等）
- 为每个实体指定类别（危险源/风险点/管控措施/责任人）
- 为风险点指定风险等级（重大风险、较大风险、一般风险）

## 安全规程文档:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取安全管控关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：安全管控关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 识别从危险源到风险点的关联（关系类型：导致）
- 识别从风险点到管控措施的关联（关系类型：需要/管控）
- 识别从管控措施到责任人的关联（关系类型：负责）
- 记录危险因素和可能导致后果
- 关系类型使用：导致、需要、管控、负责

## 已知实体列表:
{known_nodes}

## 安全规程文档:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位工业安全管理分析专家，请从文本中提取危险源、风险点和管控措施，构建安全管控关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体，包括危险源、风险点、管控措施、责任人
- **边 (Edge)**：安全管控关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 领域特定规则
- 识别危险源（如数控加工中心、工业机械臂、冷却系统、液压站、电气控制柜等）
- 识别风险点（如烫伤风险、机械伤害风险、触电风险、摔伤风险等）
- 识别管控措施（如佩戴防护用品、设置安全围栏、定期检修、通风换气等）
- 识别责任人（如安全主管、设备负责人、班组长、电工等）
- 为风险点指定风险等级（重大风险、较大风险、一般风险）
- 建立从危险源→风险点→管控措施→责任人的完整管控链条

## 安全规程文档:
{source_text}
"""


class SafetyControlGraph(AutoGraph[SafetyEntity, SafetyRelation]):
    """
    适用文档: 安全规程、安全风险评估报告、职业健康安全手册

    功能介绍:
    从安全规程中提取危险源、风险点和管控措施，构建安全管控关系，
    识别安全风险与管控责任的对应关系，为安全管理提供参考。

    Example:
        >>> template = SafetyControlGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("数控加工中心存在烫伤风险，风险等级为重大风险。需佩戴防护眼镜和防护手套，由设备负责人负责监督检查...")
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
        初始化安全管控图谱模板。

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
            node_schema=SafetyEntity,
            edge_schema=SafetyRelation,
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
        展示安全管控图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: SafetyEntity) -> str:
            risk = f" [{node.risk_level}]" if node.risk_level else ""
            return f"{node.name} ({node.category}){risk}"

        def edge_label_extractor(edge: SafetyRelation) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
