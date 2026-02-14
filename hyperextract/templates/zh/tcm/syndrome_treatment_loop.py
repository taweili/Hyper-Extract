from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================

class TcmConceptNode(BaseModel):
    """中医诊疗过程中涉及的概念：症状体征、证型、治法、方药。"""
    name: str = Field(description="概念名称，如‘胁肋胀痛’(症状)、‘肝气郁结’(证型)、‘疏肝解郁’(治法)。")
    category: str = Field(description="实体类别：症状、证候、病机、治法、方剂、药物。")
    detail: Optional[str] = Field(description="对该概念的补充描述（如‘苔薄白、脉弦’）。")

class ClinicalLogic(BaseModel):
    """诊疗逻辑链条中的推导关系。"""
    source: str = Field(description="前导概念（如：某一症状）。")
    target: str = Field(description="推导出结论（如：某一证型）。")
    logic_type: str = Field(description="逻辑类型：辨证为、导致（病机）、确立（治法）、选用（方药）。")
    reasoning: str = Field(description="具体的推导依据或说明（如‘因舌苔白腻，故知湿困脾胃’）。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位临床经验丰富的中医学家。你的任务是从复杂的医案或古籍中逻辑化地提取‘辨证论治’全过程。\n\n"
    "### 核心提取规则：\n"
    "1. **逻辑链条**：必须构建‘症状 -> 证候/病机 -> 治法 -> 方药’的完整逻辑回路。\n"
    "2. **术语对齐**：使用标准的中医术语。例如，将‘不想吃饭’标准化为‘纳呆’，‘嗓子不舒服’标准化为‘咽干/咽痛’。\n"
    "3. **因果保留**：关键是要提取出‘为何得出此证’和‘为何立此法’的证据，保存在 `reasoning` 字段中。\n"
    "4. **主次分明**：识别主证（Key Symptoms）并将其与一般随见症状区分开。"
)

_NODE_PROMPT = (
    "你是一位中医知识图谱专家。请从医案中识别所有诊疗相关的核心概念。\n\n"
    "### 提取规则：\n"
    "1. **分类识别**：严格区分症状（Symptom）、证候（Syndrome）、治法（Therapy）与方药（Formula/Herb）。\n"
    "2. **细节捕捉**：舌相、脉相必须作为症状节点的 `detail` 属性进行提取。\n"
    "3. **实体统一**：确保同一个概念在不同句子中出现时使用统一的、标准化的名称。"
)

_EDGE_PROMPT = (
    "你是一位中医临床逻辑分析师。请根据已识别的概念，建立它们之间的诊疗映射关系。\n\n"
    "### 逻辑连接规则：\n"
    "1. **辨证连接**：将关键症状连接到其归纳出的证候（逻辑类型：‘辨证为’）。\n"
    "2. **立法连接**：将证候连接到根据病机确立的治法（逻辑类型：‘确立治法’）。\n"
    "3. **处方连接**：将治法连接到最终选用的方剂或主药（逻辑类型：‘选用方药’）。\n"
    "4. **证据关联**：在 `reasoning` 字段中详细解释该逻辑推导的具体依据。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class SyndromeTreatmentLoop(AutoGraph[TcmConceptNode, ClinicalLogic]):
    """
    适用于：[中医医案, 诊断学教材, 诊疗指南]

    一个专门逻辑化捕获“症状 -> 证候 -> 治法 -> 方药”这一核心中医诊疗过程的图谱模板。

    Key Features:
    - 完整提取中医辨证论治的因果逻辑链条。
    - 将散落的临床表现标准化为结构化的逻辑节点。
    - 保留每个诊疗结论背后的辨证依据。

    Example:
        >>> from hyperextract.templates.zh.tcm import SyndromeTreatmentLoop
        >>> loop = SyndromeTreatmentLoop(llm_client=llm, embedder=embedder)
        >>> text = "患者两胁胀痛，脉弦，此为肝气郁结，治宜疏肝理气，方用柴胡疏肝散。"
        >>> loop.feed_text(text).show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        **kwargs: Any
    ):
        """
        初始化 SyndromeTreatmentLoop。

        Args:
            llm_client (BaseChatModel): 用于提取的语言模型客户端。
            embedder (Embeddings): 用于索引的嵌入模型。
            extraction_mode (str): 提取模式，'one_stage' 或 'two_stage'。默认为 'two_stage'。
            **kwargs: 传递给 AutoGraph 的额外参数。
        """
        super().__init__(
            node_schema=TcmConceptNode,
            edge_schema=ClinicalLogic,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source}->{x.logic_type}->{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            extraction_mode=extraction_mode,
            **kwargs
        )

    def show(self, **kwargs):
        """
        可视化临床辨证论治逻辑闭环。

        Args:
            **kwargs: 传递给基础 show() 方法的参数。
        """
        def n_label(node: TcmConceptNode) -> str: return f"{node.name} [{node.category}]"
        def e_label(edge: ClinicalLogic) -> str: return f"[{edge.logic_type}]: {edge.reasoning}"
        super().show(node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs)
