"""判例引用网络 - 映射案件之间的引用、先例区分或先例推翻关系。

适用于判例研究、案例汇编、法律评注等文本。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class CaseNode(BaseModel):
    """判例节点"""
    case_name: str = Field(description="案件名称或案号，如指导案例140号、民法典第1165条")
    case_type: str = Field(description="案件类型：指导案例、公报案例、普通案例、司法解释、法律条文")
    court: Optional[str] = Field(description="审理法院", default=None)
    description: Optional[str] = Field(description="案件简要描述", default=None)


class CaseCitationEdge(BaseModel):
    """判例引用关系边"""
    source: str = Field(description="源案件名称")
    target: str = Field(description="被引用案件名称")
    citation_type: str = Field(
        description="引用类型：引用、依据、先例区分、先例推翻、参考、类案"
    )
    description: Optional[str] = Field(description="引用关系的具体描述", default=None)


_NODE_PROMPT = """## 角色与任务
你是一位专业的法学专家，请从文本中提取所有判例作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的判例或法律条文
- **边 (Edge)**：判例之间的引用或关联关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的判例，禁止将多个判例合并为一个节点
2. 判例名称与原文保持一致

### 领域特定规则
- 案件类型：指导案例、公报案例、普通案例、司法解释、法律条文
- 常见表达："根据《民法典》第X条"、"指导案例XX号"、"本案确立了..."

## 判例文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知判例列表中提取判例之间的引用或关联关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的判例或法律条文
- **边 (Edge)**：判例之间的引用或关联关系

## 提取规则
### 核心约束
1. 仅从已知判例列表中提取边，不要创建未列出的判例
2. 关系描述应与原文保持一致

### 关系类型
- 引用：后案引用前案作为裁判依据
- 依据：后案以前案确立的规则为法律依据
- 先例区分：后案认为前案与本案情形不同，不适用前案规则
- 先例推翻：后案推翻前案确立的规则
- 参考：后案参考前案的裁判思路
- 类案：后案与前案属于同类案件

## 已知判例列表:
{known_nodes}

## 判例文本:
{source_text}
"""

_PROMPT = """## 角色与任务
你是一位专业的法学专家，请从文本中提取所有判例以及它们之间的引用或关联关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的判例或法律条文
- **边 (Edge)**：判例之间的引用或关联关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的判例，禁止将多个判例合并为一个节点
2. 判例名称与原文保持一致
3. 仅从已知判例列表中提取边，不要创建未列出的判例
4. 关系描述应与原文保持一致

### 关系类型
- 引用：后案引用前案作为裁判依据
- 依据：后案以前案确立的规则为法律依据
- 先例区分：后案认为前案与本案情形不同
- 先例推翻：后案推翻前案确立的规则
- 参考：后案参考前案的裁判思路
- 类案：后案与前案属于同类案件

## 判例文本:
{source_text}
"""


class CaseLawCitationNet(AutoGraph[CaseNode, CaseCitationEdge]):
    """
    适用文档: 判例研究、案例汇编、法律评注、司法解释理解与适用

    功能介绍:
    映射案件之间的引用、先例区分或先例推翻关系，
    支持判例法研究、类案检索等应用场景。

    设计说明:
    - 节点（CaseNode）：存储判例信息，包括名称、类型、法院、描述
    - 边（CaseCitationEdge）：存储判例间的引用关系

    Example:
        >>> template = CaseLawCitationNet(llm_client=llm, embedder=embedder)
        >>> template.feed_text("指导案例140号确立了...")
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
        初始化判例引用网络模板。

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
            node_schema=CaseNode,
            edge_schema=CaseCitationEdge,
            node_key_extractor=lambda x: x.case_name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}|{x.citation_type}|{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
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
        展示判例引用网络图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: CaseNode) -> str:
            return f"{node.case_name}({node.case_type})"

        def edge_label_extractor(edge: CaseCitationEdge) -> str:
            return edge.citation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
