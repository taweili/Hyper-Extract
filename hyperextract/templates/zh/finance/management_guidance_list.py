from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class GuidanceItem(BaseModel):
    """
    管理层的单项前瞻性指引声明。
    """

    guidance_topic: str = Field(
        description="指引主题（例如'第四季度收入'、'2025 财年资本支出'、'毛利率展望'、'招聘计划'）。"
    )
    guidance_type: str = Field(
        description='类型："定量"、"定性"、"战略"、"运营"。'
    )
    guidance_value: str = Field(
        description="指引内容或预测值（例如'950-970 亿美元'、'将拓展 5 个新市场'、"
        "'预计下半年利润率改善'）。"
    )
    prior_guidance: Optional[str] = Field(
        None,
        description="同一指标的前次指引（如有修订，例如'900-930 亿美元'）。",
    )
    direction: Optional[str] = Field(
        None,
        description="相对前次指引或一致预期的方向：'上调'、'下调'、'维持'、'首次发布'。",
    )
    time_period: Optional[str] = Field(
        None,
        description="指引覆盖的时间段（例如'2024 年第四季度'、'2025 财年'、'未来 12 个月'）。",
    )
    confidence_language: Optional[str] = Field(
        None,
        description="管理层的确信程度措辞（例如'我们预计'、'我们有信心'、'我们预期'）。",
    )
    speaker: Optional[str] = Field(
        None,
        description="指引发布者（例如'CEO'、'CFO'、'COO'）。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是跟踪财报电话会议管理层指引的分析师。"
    "从本会议记录中提取所有前瞻性声明和业绩指引。\n\n"
    "规则:\n"
    "- 提取每一项指引条目（定量数据、战略规划、展望声明）。\n"
    "- 注明指引相较前次是上调、下调还是维持不变。\n"
    "- 捕捉每项指引覆盖的时间段。\n"
    "- 保留管理层的确信程度措辞。\n"
    "- 识别每项指引的发布者。\n"
    "- 将每项指引声明作为独立条目提取。\n\n"
    "### 原文:\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class ManagementGuidanceList(AutoList[GuidanceItem]):
    """
    适用文档: 财报电话会议记录、投资者日演示材料、
    业绩指引更新、管理层评论部分。

    模板用于从财报电话会议和管理层报告中提取前瞻性指引。每项指引条目
    独立捕捉，便于跟踪修订和管理预期。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> guidance = ManagementGuidanceList(llm_client=llm, embedder=embedder)
        >>> transcript = "对于第四季度，我们预计收入在 950 至 970 亿美元之间..."
        >>> guidance.feed_text(transcript)
        >>> guidance.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化管理层指引列表模板。

        Args:
            llm_client (BaseChatModel): 用于指引提取的 LLM。
            embedder (Embeddings): 用于索引的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoList 的其他参数。
        """
        super().__init__(
            item_schema=GuidanceItem,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """
        可视化管理层指引列表。

        Args:
            top_k_for_search (int): 检索的条目数。默认 3。
            top_k_for_chat (int): 对话上下文中的条目数。默认 3。
        """

        def label_extractor(item: GuidanceItem) -> str:
            direction = f" [{item.direction}]" if item.direction else ""
            return f"{item.guidance_topic}{direction}: {item.guidance_value[:50]}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
