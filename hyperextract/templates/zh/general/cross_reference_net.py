"""交叉引用网络 - 映射概念之间的超链接或相互引用关系。

适用于百科内链、跨词条关联图等。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class ReferenceNode(BaseModel):
    """引用节点"""
    name: str = Field(description="概念/条目名称")
    type: str = Field(description="节点类型：条目、章节、概念、人物、地点、其他")
    description: str = Field(description="简要描述", default="")


class ReferenceRelation(BaseModel):
    """引用关系边"""
    source: str = Field(description="源条目/概念")
    target: str = Field(description="被引用条目/概念")
    relationType: str = Field(description="关系类型：Hyperlink（超链接）、Reference（引用）、SeeAlso（参见）、Related（相关）、Other（其他）")
    context: str = Field(description="引用上下文描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的知识网络分析专家，请从文本中提取概念/条目及其相互引用关系，构建交叉引用网络。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指概念或条目单元，包括条目、章节、概念、人物、地点等类型，用于表示知识网络中的实体。
- **边 (Edge)**：本模板中的"边"指概念/条目之间的引用关系，包括 Hyperlink（超链接）、Reference（引用）、SeeAlso（参见）、Related（相关）等二元关系。

## 提取规则
### 节点提取规则
1. 提取所有被提及的概念或条目
2. 为每个节点指定类型：条目、章节、概念、人物、地点、其他
3. 为每个节点添加简要描述

### 关系提取规则
1. 仅从提取的节点中创建边
2. 关系类型包括：
   - Hyperlink：超链接关系
   - Reference：引用关系
   - SeeAlso：参见关系
   - Related：相关关系
   - Other：其他关系
3. 记录引用的上下文描述

### 约束条件
- 每条边必须连接已提取的节点
- 不要创建未在文本中提及的节点或关系
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的条目识别专家，请从文本中提取所有概念或条目作为节点。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指概念或条目单元，包括条目、章节、概念、人物、地点等类型，用于表示知识网络中的实体。

## 提取规则
1. 提取所有被提及的概念或条目
2. 为每个节点指定类型：条目、章节、概念、人物、地点、其他
3. 为每个节点添加简要描述

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的引用关系提取专家，请从给定节点列表中提取节点之间的相互引用关系。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指概念或条目单元，作为引用关系的参与者。
- **边 (Edge)**：本模板中的"边"指概念/条目之间的引用关系，包括 Hyperlink（超链接）、Reference（引用）、SeeAlso（参见）、Related（相关）等二元关系。

## 提取规则
### 关系类型说明
- Hyperlink：超链接关系
- Reference：引用关系
- SeeAlso：参见关系
- Related：相关关系
- Other：其他关系

### 约束条件
1. 仅从下方已知节点列表中提取边
2. 不要创建未列出的节点

"""


class CrossReferenceNet(AutoGraph[ReferenceNode, ReferenceRelation]):
    """
    适用文档: 维基百科条目、知识库文档、带内链的网页内容

    功能介绍:
    映射概念之间的超链接或相互引用关系。适用于百科内链、跨词条关联图等。

    Example:
        >>> template = CrossReferenceNet(llm_client=llm, embedder=embedder)
        >>> template.feed_text("机器学习（Machine Learning）是人工智能的一个分支...")
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
        初始化交叉引用网络模板。
        
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
            node_schema=ReferenceNode,
            edge_schema=ReferenceRelation,
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
        展示交叉引用网络。
        
        Args:
            top_k_for_search: 语义检索返回的节点/边数量，默认为 3
            top_k_for_chat: 问答使用的节点/边数量，默认为 3
        """
        def node_label_extractor(node: ReferenceNode) -> str:
            return f"{node.name} ({node.type})"
        
        def edge_label_extractor(edge: ReferenceRelation) -> str:
            return edge.relationType
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
