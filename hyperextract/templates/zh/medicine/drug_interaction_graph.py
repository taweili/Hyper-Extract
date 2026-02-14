from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================

class MedicalSubstance(BaseModel):
    """药品、有效成分或膳食补充剂。"""
    name: str = Field(description="药物成分的通用名或主要商品名（如‘阿司匹林’、‘维C’）。")
    category: str = Field(description="药物类别（如‘非甾体抗炎药’、‘抗凝药’）。")
    description: Optional[str] = Field(description="该药物的主要功能或适应症。")

class DrugInteraction(BaseModel):
    """两种药物/成分之间的相互作用属性。"""
    source: str = Field(description="首个药物/成分名称。")
    target: str = Field(description="第二个药物/成分名称。")
    interaction_type: str = Field(description="作用类型（如：禁忌、慎用、协同、拮抗）。")
    severity: str = Field(description="严重程度（如：严重、中等、轻微）。")
    mechanism: str = Field(description="相互作用的药理机制描述（如‘代谢酶竞争导致血药浓度升高’）。")
    recommendation: str = Field(description="临床操作建议（如‘严禁联用’、‘监测血药浓度’）。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位专业的临床药理学家。你的任务是从医药文献、说明书或临床指南中提取药物间的相互作用关系。\n\n"
    "提取准则：\n"
    "1. **成分标准化**：优先提取通用名。若只有商品名，请记录商品名。\n"
    "2. **严谨映射**：准确提取相互作用的性质、严重程度及其背后的医学机制。\n"
    "3. **操作指导**：必须保留文中提及的临床建议选项。\n"
    "- 确保提取的互动关系仅存在于已识别的药物列表中。"
)

_NODE_PROMPT = (
    "请从医药文本中提取所有提及的药物成分、化学名称或补充剂。明确它们的分类和主要药理作用。"
)

_EDGE_PROMPT = (
    "在给定的药物列表之间，基于文本提取明确的相互作用（Interaction）。请详细说明互动类型、分级严重程度以及具体的医学机制。"
)

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================

class DrugInteractionGraph(AutoGraph[MedicalSubstance, DrugInteraction]):
    """
    适用于：[药品说明书, 药典, 临床实践指南, 医学期刊]

    用于构建药物禁忌与协同作用网络的图谱模板。

    该模板通过双阶段提取，从专业医药文献中梳理出严谨的药物相互作用图谱，为临床决策支持提供结构化数据支持。

    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # 初始化模板
        >>> drug_map = DrugInteractionGraph(llm_client=llm, embedder=embedder)
        >>> # 输入说明书文本
        >>> text = "华法林与阿司匹林联用会显著增加出血风险（高度危险）。建议避免同时使用。"
        >>> drug_map.feed_text(text)
        >>> drug_map.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any
    ):
        """
        初始化 DrugInteractionGraph 模板。

        Args:
            llm_client: 用于提取的语言模型客户端。
            embedder: 用于实体去重和索引的嵌入模型。
            extraction_mode: 默认为 one_stage 以获取快速初步图谱，专业场景建议 two_stage。
            chunk_size: 文本块大小。
            chunk_overlap: 文本块重叠大小。
            max_workers: 最大并行工作线程数。
            verbose: 是否开启详细日志。
            **kwargs: 其他传给 AutoGraph 的参数。
        """
        super().__init__(
            node_schema=MedicalSubstance,
            edge_schema=DrugInteraction,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """
        可视化药物相互作用图谱。

        Args:
            top_k_for_search: 搜索时找回的相关节点/边数量。
            top_k_for_chat: 聊天时找回的相关节点/边数量。
        """
        def node_label_extractor(node: MedicalSubstance) -> str:
            return node.name

        def edge_label_extractor(edge: DrugInteraction) -> str:
            return f"{edge.interaction_type} ({edge.severity})"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
