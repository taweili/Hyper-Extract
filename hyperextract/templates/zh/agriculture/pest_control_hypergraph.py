"""病虫害防治超图 - 从农业技术手册中提取病虫害与防治措施的复杂关联关系。

适用于农业技术手册、病虫害防治指南、植保技术手册。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class AgriculturalEntity(BaseModel):
    """农业实体节点"""

    name: str = Field(description="实体名称（病虫害名、药剂名、作物名、生长阶段名）")
    entity_type: str = Field(description="实体类型：病虫害、药剂、作物、生长阶段")
    description: str = Field(description="详细描述")


class PestControlEdge(BaseModel):
    """病虫害防治超边"""

    crop: str = Field(description="作物名称")
    stage: str = Field(description="生长阶段")
    pest: str = Field(description="病虫害名称")
    pesticide: str = Field(description="推荐药剂")
    dosage: str = Field(description="亩用量")
    safety_interval: str = Field(description="安全间隔期")


_PROMPT = """## 角色与任务
你是一位专业的植物保护专家，请从农业技术手册中提取病虫害防治超图。

## 核心概念定义
- **节点 (Node)**：从文档中提取的农业实体
- **边 (Edge)**：连接多个实体的超边，表示病虫害防治关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 超边提取约束
1. 超边连接作物、生长阶段、病虫害、药剂等多类实体
2. 每条超边必须包含作物、生长阶段、病虫害、药剂等要素

### 领域特定规则
- 病虫害类型：虫害、病害、草害
- 药剂类型：杀虫剂、杀菌剂、除草剂
- 病虫害名称：稻飞虱、稻纵卷叶螟、纹枯病、稻瘟病等
- 药剂名称：25%噻嗪酮可湿性粉剂、20%氯虫苯甲酰胺悬浮剂等
- 安全间隔期：最后一次施药至收获的天数

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的植物保护专家，请从文本中提取所有农业实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的农业实体

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 病虫害：如稻飞虱、稻纵卷叶螟、纹枯病、稻瘟病
- 药剂：如25%噻嗪酮可湿性粉剂、20%氯虫苯甲酰胺悬浮剂
- 作物：如水稻、小麦、玉米
- 生长阶段：如播种期、分蘖期、孕穗期、灌浆期

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知实体列表中提取病虫害防治超边关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的农业实体
- **边 (Edge)**：连接多个实体的超边，表示病虫害防治关系

## 提取规则
### 核心约束
1. 超边连接作物、生长阶段、病虫害、药剂等多类实体
2. 仅从已知实体列表中选择参与者，不要创建未列出的实体
3. 每条超边必须包含作物、生长阶段、病虫害、药剂、剂量、安全间隔期

### 领域特定规则
- 超边格式：《作物 + 生长阶段 + 病虫害 -> 药剂 + 剂量 + 安全间隔期》
- 病虫害名称保持原文
- 药剂名称保持原文，包括商品名和有效成分

"""


class PestControlHypergraph(AutoHypergraph[AgriculturalEntity, PestControlEdge]):
    """
    适用文档: 农业技术手册、病虫害防治指南、植保技术手册

    功能介绍:
    从农业技术手册中提取复杂的病虫害防治逻辑，建模
    {作物, 阶段, 不良诱因} -> {防治对象, 推荐药剂, 剂量, 安全间隔期}
    的超图关系。
    适用于智能植保系统、农药推荐、植保决策支持。

    Example:
        >>> template = PestControlHypergraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("分蘖期防治稻飞虱，可用25%噻嗪酮可湿性粉剂30-40克/亩，安全间隔期14天...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化病虫害防治超图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            chunk_size: 每个分块的最大字符数，默认为 2048
            chunk_overlap: 分块之间的重叠字符数，默认为 256
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=AgriculturalEntity,
            edge_schema=PestControlEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.crop}_{x.stage}_{x.pest}_{x.pesticide}",
            nodes_in_edge_extractor=lambda x: tuple(
                [x.crop, x.stage, x.pest, x.pesticide]
            ),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
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
        展示病虫害防治超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: AgriculturalEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: PestControlEdge) -> str:
            return f"{edge.crop} （{edge.stage}）"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
