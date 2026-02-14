from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================

class HerbNode(BaseModel):
    """中药方剂中的核心实体：方剂名或单味药材。"""
    name: str = Field(description="方剂名称（如‘麻黄汤’）或药材名称（如‘桂枝’）。")
    category: str = Field(description="实体类别（如：方剂、解表药、补气药）。")
    nature_flavor: Optional[str] = Field(description="药材的性味归经（如：辛温，归肺膀胱经）。对于方剂可留空。")

class CompositionRole(BaseModel):
    """描述方剂中药材的配伍地位（君臣佐使）及具体用法。"""
    source: str = Field(description="所属方剂名称。")
    target: str = Field(description="组成该方剂的药材名称。")
    role: str = Field(description="配伍角色：君药、臣药、佐药、使药。如未明确指出，可填‘组成’。")
    dosage: Optional[str] = Field(description="药材的剂量（如：三钱、9g）。保留原单位。")
    preparation: Optional[str] = Field(description="特殊炮制或煎煮方法（如：先煎、后下、蜜炙、去皮）。")
    explanation: str = Field(description="该药在方中的具体功效解释（如：发汗解表以散风寒）。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位精通‘君臣佐使’理论的中医方剂学家。你的任务是从方剂学教材或古籍中解析方剂的严密组方结构及配伍内涵。\n\n"
    "### 核心提取规则：\n"
    "1. **角色界定**：必须准确识别君药（核心治疗）、臣药（辅助）、佐药（兼治/制约）、使药（引经/调和）。\n"
    "2. **细节保留**：严禁遗漏剂量和炮制要求（如‘生用’、‘酒炒’），这些对方剂的安全性和有效性至关重要。\n"
    "3. **术语标准**：提取药名时去除琐碎修饰词，但炮制信息应放入 `preparation` 字段。\n"
    "4. **逻辑解释**：在 `explanation` 中总结该药为何处于此配伍地位及其发挥的具体药理作用。"
)

_NODE_PROMPT = (
    "你是一位资深中医文档分析师。请识别文本中出现的方剂名和单味药材名称。\n\n"
    "### 提取要求：\n"
    "1. **节点去重**：同一方剂名在文中多次出现时应视为一个节点。\n"
    "2. **性味补充**：尽可能利用文本线索补充药材的‘性味归经’属性。\n"
    "3. **实体边界**：药名应简洁，例如‘炙甘草’提取为药名‘甘草’，炮制属性‘炙’记录在后期连接环节。"
)

_EDGE_PROMPT = (
    "你是一位精通方剂配伍理论的分析师。请在已识别的方剂与药材间建立‘组方关系’。\n\n"
    "### 关系提取要求：\n"
    "1. **角色属性**：依据文本中‘为君’、‘辅助’、‘兼见’等表述，映射到标准的‘君、臣、佐、使’角色。\n"
    "2. **剂量解析**：准确识别数量及单位（如‘三钱’、‘12g’）。\n"
    "3. **煎服法捕捉**：捕捉‘先煎’、‘后下’、‘烊化’等特殊煎服法描述放入 `preparation`。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class PrescriptionCompositionGraph(AutoGraph[HerbNode, CompositionRole]):
    """
    适用于：[方剂学教材, 伤寒杂病论医案, 中药处方]

    一个基于“君臣佐使”理论对方剂结构进行层级解构的专用图谱模板。

    Key Features:
    - 提取方剂层级结构及具体的角色分配（君臣佐使）。
    - 捕获精确的剂量和炮制煎服方法。
    - 将药材与其在方剂环境下的药理解释相关联。

    Example:
        >>> from hyperextract.templates.zh.tcm import PrescriptionCompositionGraph
        >>> graph = PrescriptionCompositionGraph(llm_client=llm, embedder=embedder)
        >>> text = "麻黄汤中，麻黄为君，发汗解表；桂枝为臣，助麻黄解肌。"
        >>> graph.feed_text(text).show()
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
        初始化 PrescriptionCompositionGraph。

        Args:
            llm_client (BaseChatModel): 用于提取的语言模型客户端。
            embedder (Embeddings): 用于索引的嵌入模型。
            extraction_mode (str): 提取模式，'one_stage' 或 'two_stage'。默认为 'two_stage'。
            **kwargs: 传递给 AutoGraph 的额外参数。
        """
        super().__init__(
            node_schema=HerbNode,
            edge_schema=CompositionRole,
            node_key_extractor=lambda x: x.name.strip(),
            # 边的主键：方剂-角色-药材
            edge_key_extractor=lambda x: f"{x.source}-{x.role}-{x.target}",
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
        可视化方剂配伍结构。

        Args:
            **kwargs: 传递给基础 show() 方法的参数。
        """
        def n_label(node: HerbNode) -> str: return f"{node.name} [{node.category}]"
        def e_label(edge: CompositionRole) -> str:
            extra = f"({edge.dosage})" if edge.dosage else ""
            prep = f"[{edge.preparation}]" if edge.preparation else ""
            return f"{edge.role}{extra}{prep}: {edge.explanation}"
        super().show(node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs)
