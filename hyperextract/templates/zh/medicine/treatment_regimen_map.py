"""综合治疗方案图 - 提取由"药物组合+理疗+生活干预"构成的多因素治疗方案。

适用于临床诊疗指南中关于治疗方案的内容。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class TreatmentEntity(BaseModel):
    """治疗实体节点"""

    name: str = Field(description="实体名称，如药物、理疗方法、生活干预等")
    category: str = Field(description="实体类型：药物、理疗、生活干预、检查、手术等")
    description: str = Field(description="简要描述", default="")


class TreatmentHyperedge(BaseModel):
    """治疗方案超边"""

    name: str = Field(description="超边名称，如治疗方案、康复计划等")
    nodes: List[str] = Field(description="参与超边的节点列表")
    disease: str = Field(description="针对的疾病")
    details: str = Field(description="详细描述，如具体的治疗方案内容")


_PROMPT = """## 角色与任务
你是一位专业的临床医生，请从文本中提取由"药物组合+理疗+生活干预"构成的多因素治疗方案，构建综合治疗方案图。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指治疗实体，包括药物、理疗方法、生活干预、检查、手术等类型，用于表示治疗方案中的基本要素。
- **边 (Edge)**：本模板中的"边"指治疗方案超边，连接多个节点，表达完整的治疗方案。

## 提取规则
### 节点提取规则
1. 提取所有治疗相关实体：药物名称、理疗方法、生活干预措施、检查项目、手术方式等
2. 为每个实体指定类型：药物、理疗、生活干预、检查、手术等
3. 为每个实体添加简要描述

### 超边提取规则
1. 仅从提取的实体中创建超边
2. 超边应表示完整的治疗方案，包含药物组合、理疗和生活干预等多个要素
3. 为每个超边指定针对的疾病
4. 为每个超边添加详细描述，说明具体的治疗方案内容

### 约束条件
- 每条超边必须连接多个已提取的节点
- 不要创建未在文本中提及的实体或关系
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的治疗实体识别专家，请从文本中提取与治疗方案相关的所有关键实体作为节点。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指治疗实体，包括药物、理疗方法、生活干预、检查、手术等类型，用于表示治疗方案中的基本要素。

## 提取规则
1. 提取所有治疗相关实体：药物名称、理疗方法、生活干预措施、检查项目、手术方式等
2. 为每个实体指定类型：药物、理疗、生活干预、检查、手术等
3. 为每个实体添加简要描述

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的治疗方案提取专家，请从给定实体列表中提取完整的治疗方案，构建治疗方案超边。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指治疗实体，作为治疗方案的组成部分。
- **边 (Edge)**：本模板中的"边"指治疗方案超边，连接多个节点，表达完整的治疗方案。

## 提取规则
1. 仅从下方已知实体列表中创建超边
2. 超边应表示完整的治疗方案，包含药物组合、理疗和生活干预等多个要素
3. 为每个超边指定针对的疾病
4. 为每个超边添加详细描述，说明具体的治疗方案内容

### 约束条件
1. 不要创建未列出的实体
2. 每条超边必须连接多个节点

"""


class TreatmentRegimenMap(AutoHypergraph[TreatmentEntity, TreatmentHyperedge]):
    """
    适用文档: 临床诊疗指南、治疗方案手册

    功能介绍:
    提取由"药物组合+理疗+生活干预"构成的多因素治疗方案，适用于肿瘤化疗方案、慢病管理。

    Example:
        >>> template = TreatmentRegimenMap(llm_client=llm, embedder=embedder)
        >>> template.feed_text("2型糖尿病的治疗方案包括二甲双胍、饮食控制和运动...")
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
        初始化综合治疗方案图模板。

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
            node_schema=TreatmentEntity,
            edge_schema=TreatmentHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.name,
            nodes_in_edge_extractor=lambda x: x.nodes,
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
        展示综合治疗方案图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: TreatmentEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: TreatmentHyperedge) -> str:
            return f"{edge.name} - {edge.disease}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
