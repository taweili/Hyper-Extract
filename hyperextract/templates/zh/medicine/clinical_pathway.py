"""临床路径图 - 提取"如果症状A则检查B否则治疗C"的决策树结构。

适用于临床诊疗指南中关于决策路径的内容。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class ClinicalNode(BaseModel):
    """临床节点"""

    name: str = Field(description="节点名称，如症状、检查、治疗等")
    category: str = Field(description="节点类型：症状、检查、治疗、诊断、决策点等")
    description: str = Field(description="简要描述", default="")


class ClinicalEdge(BaseModel):
    """临床路径边"""

    source: str = Field(description="源节点")
    target: str = Field(description="目标节点")
    condition: str = Field(description="条件描述，如如果症状A则")
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的临床医生，请从文本中提取"如果症状A则检查B否则治疗C"的决策树结构，构建临床路径图。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
#### _PROMPT（节点提取）
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

#### 边提取
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则
- 医学专业术语保持原文，如检查项目名称、药物名称
- 临床术语保持原文，如心电图、血常规

## 诊疗记录:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的临床节点识别专家，请从文本中提取所有临床相关节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 医学专业术语保持原文，如检查项目名称、药物名称、症状名称

## 诊疗记录:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的临床路径提取专家，请从给定节点列表中提取决策树结构，构建临床路径边。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 每条边必须连接已提取的节点
3. 关系描述应与原文保持一致

### 领域特定规则
- 医学专业术语保持原文

## 已知节点:
{known_nodes}

## 诊疗记录:
{source_text}
"""


class ClinicalPathway(AutoGraph[ClinicalNode, ClinicalEdge]):
    """
    适用文档: 临床诊疗指南、决策路径手册

    功能介绍:
    提取"如果症状A则检查B否则治疗C"的决策树结构，适用于临床路径管理、诊疗规范化。

    Example:
        >>> template = ClinicalPathway(llm_client=llm, embedder=embedder)
        >>> template.feed_text("如果患者出现胸痛，应进行心电图检查；否则，给予对症治疗...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化临床路径图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=ClinicalNode,
            edge_schema=ClinicalEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.condition}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
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
        展示临床路径图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: ClinicalNode) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: ClinicalEdge) -> str:
            return edge.condition

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
