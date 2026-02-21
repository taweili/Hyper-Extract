from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class ProceedsItem(BaseModel):
    """
    单项募集资金用途分配条目。
    """

    use_category: str = Field(
        description="资金用途类别（例如'研发投入'、'偿还债务'、'营运资金'、"
        "'收购'、'资本支出'、'一般企业用途'）。"
    )
    project_name: Optional[str] = Field(
        None,
        description="具体项目或计划名称（例如'弗吉尼亚新数据中心'、'平台 2.0 开发'）。",
    )
    allocated_amount: Optional[str] = Field(
        None,
        description="分配金额（例如'1.5 亿美元'、'约占净募集资金的 30%'）。",
    )
    percentage_of_proceeds: Optional[str] = Field(
        None,
        description="占总募集资金的百分比（例如'30%'、'约三分之一'）。",
    )
    timeline: Optional[str] = Field(
        None,
        description="预计资金使用时间表（例如'12-18 个月'、'2025-2026 财年'）。",
    )
    description: Optional[str] = Field(
        None,
        description="资金具体使用方式的详细说明。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是 IPO 分析师。从本招股说明书或发行文件中提取所有募集资金用途分配信息。\n\n"
    "规则:\n"
    "- 提取每一项资金用途类别和具体项目。\n"
    "- 捕捉分配金额和百分比。\n"
    "- 提取资金使用时间表（如有说明）。\n"
    "- 保留资金使用方式的详细描述。\n"
    "- 将每项分配作为独立条目提取。\n\n"
    "### 原文:\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class ProceedsUsage(AutoList[ProceedsItem]):
    """
    适用文档: S-1 招股说明书（募集资金用途部分）、债券发行备忘录、
    二次发行招股说明书、SPAC 委托声明书。

    模板用于从招股说明书和发行文件中提取资金分配明细。每项分配作为独立条目捕捉，
    便于 IPO 后监控和资金用途跟踪。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> proceeds = ProceedsUsage(llm_client=llm, embedder=embedder)
        >>> prospectus = "我们拟将约 1.5 亿美元用于研发，1 亿美元用于偿还债务..."
        >>> proceeds.feed_text(prospectus)
        >>> proceeds.show()
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
        初始化募集资金用途模板。

        Args:
            llm_client (BaseChatModel): 用于资金用途提取的 LLM。
            embedder (Embeddings): 用于索引的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoList 的其他参数。
        """
        super().__init__(
            item_schema=ProceedsItem,
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
        可视化募集资金用途列表。

        Args:
            top_k_for_search (int): 检索的条目数。默认 3。
            top_k_for_chat (int): 对话上下文中的条目数。默认 3。
        """

        def label_extractor(item: ProceedsItem) -> str:
            amount = f": {item.allocated_amount}" if item.allocated_amount else ""
            return f"{item.use_category}{amount}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
