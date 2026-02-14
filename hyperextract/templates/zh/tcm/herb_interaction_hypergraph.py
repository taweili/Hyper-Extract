from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================

class HerbNode(BaseModel):
    """单味中药材。"""
    name: str = Field(description="药材标准名称。")
    nature_flavor: str = Field(description="性味归经（如：苦寒，归胃经）。")

class InteractionHyperEdge(BaseModel):
    """
    描述多味中药材之间复杂的相互作用关系。
    这不仅仅是一对一的药对，也可能是多味药的协同（如：反佐、十八反）。
    """
    herbs_involved: List[str] = Field(description="参与该相互作用的所有药材名称列表。")
    interaction_type: str = Field(description="交互类型：七情配伍（相须、相使、相畏...）、十八反、十九畏、协同增强、拮抗减毒。")
    mechanism: str = Field(description="具体的药理机制或配伍效果描述（如：生姜与半夏相畏，能解其毒）。")
    clinical_significance: Optional[str] = Field(description="临床指导意义（如：用于妊娠呕吐，或绝对禁止同用）。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位深谙中药理论及现代药理学的药剂师。你的任务是分析文献中提到的药物配伍相互作用（包括但不限于七情、十八反）。\n\n"
    "### 核心提取规则：\n"
    "1. **多向识别**：某些配伍涉及多味药（如一种药同时‘相恶’多种药，或多方药联合导致的毒性变化），必须建立涉及所有方的超边。\n"
    "2. **七情辨识**：精准区分协同作用（相须、相使）、减毒作用（相畏、相杀）、减效作用（相恶）和增毒作用（相反）。\n"
    "3. **机制还原**：在 `mechanism` 字段中详细描述为何会产生此反应（如‘生姜能消除半夏的刺激性毒性’）。\n"
    "4. **安全警示**：对于禁忌类配伍，在 `clinical_significance` 中明确标注‘严禁同用’等字样。"
)

_NODE_PROMPT = (
    "你是一位中药药性研究专家。请识别文本中提到的所有中药材实体。\n\n"
    "### 提取规则：\n"
    "1. **实体规范**：统一使用《药典》标准名称。\n"
    "2. **药性关联**：尽可能标注每味药的典型性味归经属性。"
)

_EDGE_PROMPT = (
    "你是一位精准药理交互分析师。请在已识别的药材间分析复杂的相互关系。\n\n"
    "### 逻辑连接规则：\n"
    "1. **集合聚合**：将所有同时参与一个反应或配伍原则的药材归为一个列表（herbs_involved）。\n"
    "2. **关系定性**：根据‘七情合和’理论给交互类型定性（如‘相使’）。\n"
    "3. **效果量化**：描述该组合是增强了主药功效，还是抑制了副反应。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class HerbInteractionHypergraph(AutoHypergraph[HerbNode, InteractionHyperEdge]):
    """
    适用于：[本草纲目等药典, 药理学论文, 配伍禁忌预警]

    一个基于传统“七情”理论及现代药理学，用于分析多种中药间复杂非线性相互作用的超图模板。

    Key Features:
    - 捕获涉及两个以上实体的多药相互作用关系。
    - 对传统的交互类型（如“相畏”、“相杀”）进行分类。
    - 保留对安全性至关重要的机制解释和临床意义。

    Example:
        >>> from hyperextract.templates.zh.tcm import HerbInteractionHypergraph
        >>> hyper = HerbInteractionHypergraph(llm_client=llm, embedder=embedder)
        >>> text = "半夏与生姜相畏，生姜能解半夏毒；乌头反半夏、贝母、瓜蒌。"
        >>> hyper.feed_text(text).show()
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
        初始化 HerbInteractionHypergraph。

        Args:
            llm_client (BaseChatModel): 用于提取的语言模型客户端。
            embedder (Embeddings): 用于索引的嵌入模型。
            extraction_mode (str): 提取模式，'one_stage' 或 'two_stage'。默认为 'two_stage'。
            **kwargs: 传递给 AutoHypergraph 的额外参数。
        """
        super().__init__(
            node_schema=HerbNode,
            edge_schema=InteractionHyperEdge,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{sorted(x.herbs_involved)}-{x.interaction_type}",
            nodes_in_edge_extractor=lambda x: x.herbs_involved,
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
        可视化中药相互作用超图。

        Args:
            **kwargs: 传递给基础 show() 方法的参数。
        """
        def n_label(node: HerbNode) -> str: return node.name
        def e_label(edge: InteractionHyperEdge) -> str:
            return f"[{edge.interaction_type}] {edge.mechanism}"
        super().show(node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs)
