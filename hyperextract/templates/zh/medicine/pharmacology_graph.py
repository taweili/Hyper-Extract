"""药理机制图 - 提取药物、受体、靶点及生理反应之间的相互作用路径。

适用于医学教科书与专著中关于药物药理机制的内容。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class PharmacologyEntity(BaseModel):
    """药理实体节点"""

    name: str = Field(description="实体名称，如药物、受体、靶点、生理反应等")
    category: str = Field(
        description="实体类型：药物、受体、靶点、生理反应、信号通路等"
    )
    description: str = Field(description="简要描述", default="")


class PharmacologyRelation(BaseModel):
    """药理机制关系边"""

    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    relationType: str = Field(
        description="关系类型：结合、激活、抑制、调节、诱导、抑制等"
    )
    details: str = Field(description="详细描述，如具体的作用机制")


_PROMPT = """## 角色与任务
你是一位专业的药理学家，请从文本中提取药物、受体、靶点及生理反应之间的相互作用路径，构建药理机制图。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指药理实体，包括药物、受体、靶点、生理反应、信号通路等类型，用于表示药理机制中的基本要素。
- **边 (Edge)**：本模板中的"边"指药理实体之间的关系，包括结合、激活、抑制、调节、诱导、抑制等关系类型。

## 提取规则
### 节点提取规则
1. 提取所有相关实体：药物名称、受体类型、靶点、生理反应、信号通路等
2. 为每个实体指定类型：药物、受体、靶点、生理反应、信号通路等
3. 为每个实体添加简要描述

### 关系提取规则
1. 仅从提取的实体中创建关系边
2. 关系类型包括：结合、激活、抑制、调节、诱导、抑制等
3. 为每个关系添加详细描述，说明具体的作用机制

### 约束条件
- 每条边必须连接已提取的节点
- 不要创建未在文本中提及的实体或关系
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的药理实体识别专家，请从文本中提取与药理机制相关的所有关键实体作为节点。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指药理实体，包括药物、受体、靶点、生理反应、信号通路等类型，用于表示药理机制中的基本要素。

## 提取规则
1. 提取所有相关实体：药物名称、受体类型、靶点、生理反应、信号通路等
2. 为每个实体指定类型：药物、受体、靶点、生理反应、信号通路等
3. 为每个实体添加简要描述

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的药理机制分析师，请从给定实体列表中提取它们之间的相互作用路径，构建药理机制关系边。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指药理实体，作为药理机制的参与者。
- **边 (Edge)**：本模板中的"边"指药理实体之间的关系，包括结合、激活、抑制、调节、诱导、抑制等关系类型。

## 提取规则
1. 仅从下方已知实体列表中提取边
2. 关系类型包括：结合、激活、抑制、调节、诱导、抑制等
3. 为每个关系添加详细描述，说明具体的作用机制

### 约束条件
1. 不要创建未列出的实体
2. 每条边必须连接已提取的节点

"""


class PharmacologyGraph(AutoGraph[PharmacologyEntity, PharmacologyRelation]):
    """
    适用文档: 医学教科书、医学专著、药理学教材

    功能介绍:
    提取药物、受体、靶点及生理反应之间的相互作用路径，构建药理机制图。

    Example:
        >>> template = PharmacologyGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("二甲双胍通过激活AMPK信号通路降低血糖...")
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
        初始化药理机制图模板。

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
            node_schema=PharmacologyEntity,
            edge_schema=PharmacologyRelation,
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
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ):
        """
        展示药理机制图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: PharmacologyEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: PharmacologyRelation) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
