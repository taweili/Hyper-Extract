"""通用知识图谱 - 从任意文本中提取实体与关系。

适用于任意文本、网页抓取内容等非结构化文档，提取通用实体及其关系。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class GeneralEntity(BaseModel):
    """通用实体节点"""
    name: str = Field(description="实体名称，如人名、机构名、产品名")
    category: str = Field(description="实体类型：人物、机构、地点、产品、概念、其他")
    description: str = Field(description="简要描述", default="")


class GeneralRelation(BaseModel):
    """通用关系边"""
    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    relationType: str = Field(description="关系类型：属于、位于、合作、竞争、发明、创建、相关等")
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的知识图谱提取专家，请从文本中提取所有实体（节点）和它们之间的关系（边）。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指通用实体，包括人物、机构、地点、产品、概念等类型，用于表示知识图谱中的基本实体。
- **边 (Edge)**：本模板中的"边"指实体之间的二元关系，包括属于、位于、合作、竞争、发明、创建、相关等关系类型。

## 提取规则
### 节点提取规则
1. 提取所有实体：人物、机构、地点、产品、概念等
2. 为每个实体指定类型：人物、机构、地点、产品、概念、其他
3. 保持实体名称与原文一致
4. 为每个实体添加简要描述

### 关系提取规则
1. 仅从提取的实体中创建边
2. 关系类型包括：属于、位于、合作、竞争、发明、创建、相关等

### 约束条件
- 每条边必须连接已提取的节点
- 不要创建未在文本中提及的实体或关系
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的实体识别专家，请从文本中提取所有关键实体作为节点。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指通用实体，包括人物、机构、地点、产品、概念等类型，用于表示知识图谱中的基本实体。

## 提取规则
1. 提取所有实体：人物、机构、地点、产品、概念等
2. 为每个实体指定类型：人物、机构、地点、产品、概念、其他
3. 保持实体名称与原文一致
4. 为每个实体添加简要描述

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的关系提取专家，请从给定实体列表中提取实体之间的关系。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指通用实体，作为关系的参与者。
- **边 (Edge)**：本模板中的"边"指实体之间的二元关系，包括属于、位于、合作、竞争、发明、创建、相关等关系类型。

## 提取规则
### 约束条件
1. 仅从下方已知实体列表中提取边
2. 不要创建未列出的实体
3. 关系类型包括：属于、位于、合作、竞争、发明、创建、相关等

"""


class KnowledgeGraph(AutoGraph[GeneralEntity, GeneralRelation]):
    """
    适用文档: 任意文本、网页抓取内容、博客文章、新闻报道

    功能介绍:
    从任意文本中提取通用实体及其关系，构建知识图谱。支持人物、机构、地点、产品、概念等多种实体类型。

    Example:
        >>> template = KnowledgeGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("银河星际宣布神舟-50首飞成功...")
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
        初始化通用知识图谱模板。
        
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
            node_schema=GeneralEntity,
            edge_schema=GeneralRelation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
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
        展示知识图谱。
        
        Args:
            top_k_for_search: 语义检索返回的节点/边数量，默认为 3
            top_k_for_chat: 问答使用的节点/边数量，默认为 3
        """
        def node_label_extractor(node: GeneralEntity) -> str:
            return f"{node.name} ({node.category})"
        
        def edge_label_extractor(edge: GeneralRelation) -> str:
            return edge.relationType
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
