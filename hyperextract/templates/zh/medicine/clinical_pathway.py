"""临床路径图 - 提取"If 症状A Then 检查B Else 治疗C"的决策树结构。

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
    condition: str = Field(description="条件描述，如If 症状A Then")
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的临床医生，请从文本中提取"If 症状A Then 检查B Else 治疗C"的决策树结构，构建临床路径图。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指临床节点，包括症状、检查、治疗、诊断、决策点等类型，用于表示临床路径中的基本要素。
- **边 (Edge)**：本模板中的"边"指临床路径边，连接节点并包含条件描述，表达决策逻辑。

## 提取规则
### 节点提取规则
1. 提取所有临床相关节点：症状、检查项目、治疗方法、诊断结果、决策点等
2. 为每个节点指定类型：症状、检查、治疗、诊断、决策点等
3. 为每个节点添加简要描述

### 边提取规则
1. 仅从提取的节点中创建边
2. 边应包含条件描述，如"If 症状A Then"、"Else"等
3. 为每个边添加详细描述，说明具体的决策逻辑

### 约束条件
- 每条边必须连接已提取的节点
- 不要创建未在文本中提及的节点或边
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的临床节点识别专家，请从文本中提取所有临床相关节点。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指临床节点，包括症状、检查、治疗、诊断、决策点等类型，用于表示临床路径中的基本要素。

## 提取规则
1. 提取所有临床相关节点：症状、检查项目、治疗方法、诊断结果、决策点等
2. 为每个节点指定类型：症状、检查、治疗、诊断、决策点等
3. 为每个节点添加简要描述

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的临床路径提取专家，请从给定节点列表中提取决策树结构，构建临床路径边。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指临床节点，作为临床路径的组成部分。
- **边 (Edge)**：本模板中的"边"指临床路径边，连接节点并包含条件描述，表达决策逻辑。

## 提取规则
1. 仅从下方已知节点列表中提取边
2. 边应包含条件描述，如"If 症状A Then"、"Else"等
3. 为每个边添加详细描述，说明具体的决策逻辑

### 约束条件
1. 不要创建未列出的节点
2. 每条边必须连接已提取的节点

"""


class ClinicalPathway(AutoGraph[ClinicalNode, ClinicalEdge]):
    """
    适用文档: 临床诊疗指南、决策路径手册

    功能介绍:
    提取"If 症状A Then 检查B Else 治疗C"的决策树结构，适用于临床路径管理、诊疗规范化。

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
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        展示临床路径图。
        
        Args:
            top_k_for_search: 语义检索返回的节点/边数量，默认为 3
            top_k_for_chat: 问答使用的节点/边数量，默认为 3
        """
        def node_label_extractor(node: ClinicalNode) -> str:
            return f"{node.name} ({node.category})"
        
        def edge_label_extractor(edge: ClinicalEdge) -> str:
            return edge.condition
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )