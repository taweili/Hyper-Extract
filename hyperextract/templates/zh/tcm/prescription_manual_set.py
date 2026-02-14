from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class PrescriptionManual(BaseModel):
    """方剂的完整使用说明书条目。"""

    prescription_name: str = Field(description="方剂的标准名称。")
    main_functions: List[str] = Field(
        description="核心功效（如：平肝潜阳、镇心安神）。"
    )
    indications: List[str] = Field(description="主治病症（如：高血压、头痛眩晕）。")
    contraindications: List[str] = Field(
        description="禁忌人群或情况（如：孕妇慎用、脾胃虚寒者忌）。"
    )
    modifications: List[str] = Field(
        description="随症加减的常见法则（如：兼有胸闷者加瓜蒌）。"
    )
    usage_method: Optional[str] = Field(description="服用方法或煎煮说明。")


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位致力于整理中医典籍的临床药理专家。你的任务是从各类文献中归纳并富集成标准的方剂说明书。\n\n"
    "### 知识累加规则：\n"
    "1. **信息聚合**：如果不同文本提到了同一个方剂，必须将新的主治功效、加减法或禁忌证补充到该条目中，形成富集后的详尽档案。\n"
    "2. **结构标准化**：将叙述性文字转化为结构化的列表。例如，在 `contraindications` 中明确区分生理禁忌（如孕妇）与病理禁忌。\n"
    "3. **加减法捕捉**：细致记录‘若...则加/减...’的化裁规律，这对方剂的动态应用至关重要。\n"
    "4. **安全性优先**：重点关注原文中提及的任何不良反应或服用警示信息。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class PrescriptionManualSet(AutoSet[PrescriptionManual]):
    """
    适用于：[中国药典, 药品说明书, 经典方剂汇编]

    一个用于从多源中医文本中综合合成方剂详细用药手册的知识累加器模板。

    Key Features:
    - 使用“方剂名称”作为唯一键来合并和丰富来自不同来源的数据。
    - 聚合多维信息，包括功效、主治病症、随症加减法和禁忌证。
    - 自动处理去重和增量知识更新。

    Example:
        >>> from hyperextract.templates.zh.tcm import PrescriptionManualSet
        >>> manual_set = PrescriptionManualSet(llm_client=llm, embedder=embedder)
        >>> text1 = "六味地黄丸，滋阴补肾，用于腰膝酸软。"
        >>> text2 = "六味地黄丸禁用于脾胃虚寒、食少便溏者。"
        >>> manual_set.feed_text(text1).feed_text(text2).show()
    """

    def __init__(self, llm_client: BaseChatModel, embedder: Embeddings, **kwargs: Any):
        """
        初始化 PrescriptionManualSet。

        Args:
            llm_client (BaseChatModel): 用于提取的语言模型客户端。
            embedder (Embeddings): 用于索引和检索的嵌入模型。
            **kwargs: 传递给 AutoSet 的额外参数。
        """
        super().__init__(
            schema=PrescriptionManual,
            # 以方剂名称作为唯一键进行归并
            key_extractor=lambda x: x.prescription_name.strip(),
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            **kwargs,
        )

    def show(self, **kwargs):
        """
        可视化富集后的方剂说明书集合。

        Args:
            **kwargs: 传递给基础 show() 方法的参数。
        """

        def label_func(item: PrescriptionManual) -> str:
            return f"【{item.prescription_name}】主治: {', '.join(item.indications[:3])}... | 禁忌: {', '.join(item.contraindications)}"

        super().show(label_extractor=label_func, **kwargs)
