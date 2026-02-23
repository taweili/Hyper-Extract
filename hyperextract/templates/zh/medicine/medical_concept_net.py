"""医学概念网络 - 提取医学术语及其关联属性（如：属于、定义为）。

适用于医学教科书与专著中关于医学术语和概念的内容。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class MedicalConcept(BaseModel):
    """医学概念节点"""

    name: str = Field(description="概念名称，如医学术语、疾病名称、解剖部位等")
    category: str = Field(
        description="概念类型：疾病、解剖部位、生理过程、药物、症状、体征等"
    )
    definition: str = Field(description="概念定义", default="")


class MedicalRelation(BaseModel):
    """医学概念关系边"""

    source: str = Field(description="源概念")
    target: str = Field(description="目标概念")
    relationType: str = Field(
        description="关系类型：属于、定义为、包含、组成、位于、导致、治疗等"
    )
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的医学术语专家，请从文本中提取医学术语及其关联属性，构建医学概念网络。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指医学概念，包括疾病、解剖部位、生理过程、药物、症状、体征等类型，用于表示医学领域的基本术语。
- **边 (Edge)**：本模板中的"边"指医学概念之间的关系，包括属于、定义为、包含、组成、位于、导致、治疗等关系类型。

## 提取规则
### 节点提取规则
1. 提取所有医学术语和概念：疾病名称、解剖部位、生理过程、药物名称、症状、体征等
2. 为每个概念指定类型：疾病、解剖部位、生理过程、药物、症状、体征等
3. 为每个概念添加定义（如果文本中提供）

### 关系提取规则
1. 仅从提取的概念中创建关系边
2. 关系类型包括：属于、定义为、包含、组成、位于、导致、治疗等
3. 为每个关系添加详细描述（如果文本中提供）

### 约束条件
- 每条边必须连接已提取的节点
- 不要创建未在文本中提及的概念或关系
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的医学术语识别专家，请从文本中提取所有医学术语和概念作为节点。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指医学概念，包括疾病、解剖部位、生理过程、药物、症状、体征等类型，用于表示医学领域的基本术语。

## 提取规则
1. 提取所有医学术语和概念：疾病名称、解剖部位、生理过程、药物名称、症状、体征等
2. 为每个概念指定类型：疾病、解剖部位、生理过程、药物、症状、体征等
3. 为每个概念添加定义（如果文本中提供）

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的医学概念关系提取专家，请从给定医学概念列表中提取概念之间的关系。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指医学概念，作为关系的参与者。
- **边 (Edge)**：本模板中的"边"指医学概念之间的关系，包括属于、定义为、包含、组成、位于、导致、治疗等关系类型。

## 提取规则
1. 仅从下方已知概念列表中提取边
2. 关系类型包括：属于、定义为、包含、组成、位于、导致、治疗等
3. 为每个关系添加详细描述（如果文本中提供）

### 约束条件
1. 不要创建未列出的概念
2. 每条边必须连接已提取的节点

"""


class MedicalConceptNet(AutoGraph[MedicalConcept, MedicalRelation]):
    """
    适用文档: 医学教科书、医学专著、医学词典

    功能介绍:
    提取医学术语及其关联属性（如：属于、定义为），构建医学概念网络。

    Example:
        >>> template = MedicalConceptNet(llm_client=llm, embedder=embedder)
        >>> template.feed_text("慢性阻塞性肺疾病是一种以持续气流受限为特征的疾病...")
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
        初始化医学概念网络模板。

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
            node_schema=MedicalConcept,
            edge_schema=MedicalRelation,
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
        展示医学概念网络。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: MedicalConcept) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: MedicalRelation) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
