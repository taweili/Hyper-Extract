from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================

class MedicalEvent(BaseModel):
    """临床诊疗路径中的单个医疗事件。"""
    event_name: str = Field(description="事件名称或诊断摘要（如‘入院诊断’、‘心电图检查’、‘脾切除术’）。")
    event_type: str = Field(description="事件类型（如：主诉、体格检查、实验室检查、诊断、用药、手术、出院）。")
    finding: Optional[str] = Field(description="该事件的具体发现、结果或处理详情（如‘血红蛋白 90g/L’、‘手术顺利’）。")

class ClinicalProgression(BaseModel):
    """医疗事件随时间的发展过程。"""
    source: str = Field(description="前序医疗事件名称。")
    target: str = Field(description="后续医疗事件名称。")
    time: str = Field(description="医疗事件发生的具体时间或相对于入院时间的偏移。你必须将模糊的相对时间（如‘数小时后’）根据上下文解析为绝对时间（2024-01-01 10:00）或标准偏移量（如‘术后6小时’）。")
    status_change: str = Field(description="病情变化或治疗反应（如‘好转’、‘病情恶化’、‘维持稳定’）。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位专业的临床文档分析专家。你的任务是从病历、病程记录或临床路径文档中提取诊疗演变过程。\n\n"
    "分析指南：\n"
    "1. **医疗事实提取**：记录每一项重要的医疗活动（检查、用药、手术）及其核心结果。\n"
    "2. **时间逻辑链**：严格按照病程顺序建立连接。利用文本中的时间标记（如‘术前半小时’、‘次晨’）来链接事件。\n"
    "3. **动态追踪**：侧重描述治疗干预后患者状态的演变（status_change）。\n"
)

_NODE_PROMPT = (
    "请提取病历中提及的所有关键诊疗节点。包括患者的主诉、关键体征检查、主要化验结果、诊断结论、用药操作及手术项目。"
)

_EDGE_PROMPT = (
    "在诊疗节点之间建立时序联系。请根据病历的时间描述，指出不同医疗事件发生的先后关系与时间间隔，并总结病情随干预产生的动态变化。"
)

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================

class ClinicalTreatmentTimeline(AutoTemporalGraph[MedicalEvent, ClinicalProgression]):
    """
    适用于：[电子病历 (EMR), 出院小结, 病例报告, 护理记录]

    用于还原患者临床诊疗全生命周期的时序路径模板。

    该模板利用 AutoTemporalGraph 的时序特性，专注于呈现“诊断-干预-反馈”的完整医学逻辑，适合对复杂病例进行回顾性分析。

    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # 初始化模板
        >>> pathway = ClinicalTreatmentTimeline(llm_client=llm, embedder=embedder)
        >>> # 输入病程记录
        >>> text = "2月10日患者入院。2月11日急行阑尾切除术。术后恢复良好，于2月15日出院。"
        >>> pathway.feed_text(text)
        >>> pathway.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        observation_time: Optional[str] = None,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any
    ):
        """
        初始化 ClinicalTreatmentTimeline 模板。

        Args:
            llm_client: 用于提取的语言模型客户端。
            embedder: 用于实体去重和索引的嵌入模型。
            observation_time: 入院日期或当前日期。
            extraction_mode: 默认使用 two_stage 以保证复杂病史的时序解析。
            chunk_size: 文本块大小。
            chunk_overlap: 文本块重叠大小。
            max_workers: 最大并行工作线程数。
            verbose: 是否开启详细日志。
            **kwargs: 其他传给 AutoTemporalGraph 的参数。
        """
        super().__init__(
            node_schema=MedicalEvent,
            edge_schema=ClinicalProgression,
            node_key_extractor=lambda x: x.event_name.strip(),
            edge_key_extractor=lambda x: f"{x.source}>>{x.target}",
            time_in_edge_extractor=lambda x: x.time,
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
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
        可视化临床诊疗全过程。

        Args:
            top_k_for_search: 搜索时找回的相关节点/边数量。
            top_k_for_chat: 聊天时找回的相关节点/边数量。
        """
        def node_label_extractor(node: MedicalEvent) -> str:
            return f"[{node.event_type}] {node.event_name}"

        def edge_label_extractor(edge: ClinicalProgression) -> str:
            return f"({edge.time}) {edge.status_change}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
