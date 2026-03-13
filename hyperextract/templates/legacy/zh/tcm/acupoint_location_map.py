"""腧穴空间定位 - 基于人体解剖标志提取穴位的相对位置关系（如"脐旁2寸"）。

适用于针灸教学可视化、穴位图谱。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class AcupointNode(BaseModel):
    """穴位节点"""

    name: str = Field(description="穴位名称：如合谷、足三里、三阴交等")
    meridian: str = Field(description="所属经脉", default="")
    location: str = Field(description="位置描述：如脐旁2寸、腕横纹上3寸等")
    indications: str = Field(description="主治功能", default="")


class LocationRelation(BaseModel):
    """位置关系边"""

    source: str = Field(description="源穴位或解剖标志名称")
    target: str = Field(description="目标穴位名称")
    relationType: str = Field(description="关系类型：位于")
    relativePosition: str = Field(description="相对位置描述：如脐旁2寸、腕横纹上3寸等")


_PROMPT = """## 角色与任务
你是一位专业的针灸学专家，请从文本中提取穴位的相对位置关系。

## 核心概念定义
- **节点 (Node)**：穴位实体或解剖标志
- **边 (Edge)**：穴位之间的位置关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 穴位：针灸特定位置，如合谷、足三里、三阴交
- 解剖标志：人体解剖部位，如腕横纹、第2掌骨

## 针灸文献:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取穴位实体和解剖标志作为节点。

## 核心概念定义
- **节点 (Node)**：穴位实体或解剖标志

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 穴位：针灸特定位置
- 解剖标志：人体解剖部位

## 针灸文献:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知穴位列表中提取穴位的相对位置关系。

## 核心概念定义
- **边 (Edge)**：穴位之间的位置关系

## 提取规则
### 核心约束
1. 仅从已知穴位列表中提取边，不要创建未列出的穴位
2. 关系描述应与原文保持一致

## 已知穴位列表:
{known_nodes}

## 针灸文献:
{source_text}
"""


class AcupointLocationMap(AutoGraph[AcupointNode, LocationRelation]):
    """
    适用文档: 针灸学教材、穴位图谱、黄帝内经等

    功能介绍:
    基于人体解剖标志提取穴位的相对位置关系（如"脐旁2寸"），适用于针灸教学可视化、穴位图谱。

    Example:
        >>> template = AcupointLocationMap(llm_client=llm, embedder=embedder)
        >>> template.feed_text("合谷穴：在手背，第1、2掌骨间，当第2掌骨桡侧的中点处...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化腧穴空间定位模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            chunk_size: 每个分块的最大字符数，默认为 512（中医文本信息量大，需较小分块）
            chunk_overlap: 分块之间的重叠字符数，默认为 64
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=AcupointNode,
            edge_schema=LocationRelation,
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
        展示腧穴空间定位图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: AcupointNode) -> str:
            return node.name

        def edge_label_extractor(edge: LocationRelation) -> str:
            return f"{edge.relationType}: {edge.relativePosition}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
