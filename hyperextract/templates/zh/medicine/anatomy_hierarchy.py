"""解剖层级树 - 构建解剖位置的包含 (Part-Of) 和毗邻 (Connected-To) 关系。

适用于医学教科书与专著中关于解剖学的内容。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class AnatomyEntity(BaseModel):
    """解剖实体节点"""
    name: str = Field(description="解剖结构名称，如器官、组织、血管等")
    category: str = Field(description="解剖类型：器官、组织、血管、神经、骨骼等")
    description: str = Field(description="简要描述", default="")


class AnatomyRelation(BaseModel):
    """解剖关系边"""
    source: str = Field(description="源解剖结构")
    target: str = Field(description="目标解剖结构")
    relationType: str = Field(description="关系类型：包含(Part-Of)、毗邻(Connected-To)、分支、供应等")
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的解剖学家，请从文本中提取解剖结构及其关系，构建解剖层级树。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指解剖实体，包括器官、组织、血管、神经、骨骼等类型，用于表示解剖学中的基本结构。
- **边 (Edge)**：本模板中的"边"指解剖结构之间的关系，包括包含(Part-Of)、毗邻(Connected-To)、分支、供应等关系类型。

## 提取规则
### 节点提取规则
1. 提取所有解剖结构：器官名称、组织、血管、神经、骨骼等
2. 为每个解剖结构指定类型：器官、组织、血管、神经、骨骼等
3. 为每个解剖结构添加简要描述

### 关系提取规则
1. 仅从提取的解剖结构中创建关系边
2. 关系类型包括：包含(Part-Of)、毗邻(Connected-To)、分支、供应等
3. 为每个关系添加详细描述

### 约束条件
- 每条边必须连接已提取的节点
- 不要创建未在文本中提及的解剖结构或关系
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的解剖结构识别专家，请从文本中提取所有解剖结构作为节点。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指解剖实体，包括器官、组织、血管、神经、骨骼等类型，用于表示解剖学中的基本结构。

## 提取规则
1. 提取所有解剖结构：器官名称、组织、血管、神经、骨骼等
2. 为每个解剖结构指定类型：器官、组织、血管、神经、骨骼等
3. 为每个解剖结构添加简要描述

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的解剖关系提取专家，请从给定解剖结构列表中提取它们之间的关系。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指解剖实体，作为解剖关系的参与者。
- **边 (Edge)**：本模板中的"边"指解剖结构之间的关系，包括包含(Part-Of)、毗邻(Connected-To)、分支、供应等关系类型。

## 提取规则
1. 仅从下方已知解剖结构列表中提取边
2. 关系类型包括：包含(Part-Of)、毗邻(Connected-To)、分支、供应等
3. 为每个关系添加详细描述

### 约束条件
1. 不要创建未列出的解剖结构
2. 每条边必须连接已提取的节点

"""


class AnatomyHierarchy(AutoGraph[AnatomyEntity, AnatomyRelation]):
    """
    适用文档: 医学教科书、医学专著、解剖学图谱

    功能介绍:
    构建解剖位置的包含 (Part-Of) 和毗邻 (Connected-To) 关系，适用于解剖学图谱、手术导航基础。

    Example:
        >>> template = AnatomyHierarchy(llm_client=llm, embedder=embedder)
        >>> template.feed_text("心脏位于胸腔内，分为左心房、左心室、右心房、右心室...")
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
        初始化解剖层级树模板。
        
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
            node_schema=AnatomyEntity,
            edge_schema=AnatomyRelation,
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
        展示解剖层级树。
        
        Args:
            top_k_for_search: 语义检索返回的节点/边数量，默认为 3
            top_k_for_chat: 问答使用的节点/边数量，默认为 3
        """
        def node_label_extractor(node: AnatomyEntity) -> str:
            return f"{node.name} ({node.category})"
        
        def edge_label_extractor(edge: AnatomyRelation) -> str:
            return edge.relationType
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )