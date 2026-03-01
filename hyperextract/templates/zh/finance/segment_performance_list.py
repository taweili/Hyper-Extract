"""业务板块业绩列表 - 按业务板块提取营收和关键指标。

从 SEC 申报文件中按业务板块或地理区域提取营收、营业利润和关键指标，
用于板块层面的估值和敞口分析。
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class SegmentPerformanceItem(BaseModel):
    """
    单个业务板块或地理区域的业绩数据。
    """

    segment_name: str = Field(
        description="业务板块或地理区域名称（例如 '美洲'、'云服务'、'iPhone'）。"
    )
    segment_type: str = Field(
        description="类型：'业务板块'、'地理区域'、'产品线'、'经营分部'。"
    )
    revenue: Optional[str] = Field(
        None, description="该期间的板块营收（例如 '482亿美元'）。"
    )
    operating_income: Optional[str] = Field(
        None, description="板块营业利润或经营利润。"
    )
    revenue_growth: Optional[str] = Field(
        None,
        description="同比或环比营收增长率（例如 '+12%'、'-3% 同比'）。",
    )
    key_metrics: Optional[List[str]] = Field(
        None,
        description="板块特定的关键绩效指标（例如 ['订阅用户：2.3亿', 'ARPU：$14.99', '流失率：2.1%']）。",
    )
    commentary: Optional[str] = Field(
        None,
        description="管理层对板块业绩或展望的评论。",
    )


_PROMPT = """## 角色与任务
你是一位专业的财务分析师，请从 SEC 申报文件中提取每个业务板块或地理区域的业绩数据。

## 提取规则
### 核心约束
1. 每个条目对应一个独立的实体，禁止合并
2. 实体名称与原文保持一致

### 领域特定规则
- 提取每个可识别板块的营收和营业利润
- 捕获增长率和与前期的对比数据
- 提取板块特定的关键绩效指标和度量
- 保留管理层的板块评论

## 源文本:
{source_text}
"""


class SegmentPerformanceList(AutoList[SegmentPerformanceItem]):
    """
    适用文档: SEC 10-K/10-Q 分部披露（ASC 280）、年度报告、
    包含分部明细的业绩公告。

    模板用于从申报文件中提取板块层面的财务业绩数据。
    每个板块作为独立的列表条目捕获，用于对比分析和板块层面估值。

    使用示例:
        >>> segments = SegmentPerformanceList(llm_client=llm, embedder=embedder)
        >>> filing = "美洲地区板块营收为482亿美元，同比增长12%..."
        >>> segments.feed_text(filing)
        >>> segments.show()
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
        初始化业务板块业绩列表模板。

        Args:
            llm_client (BaseChatModel): 用于板块数据提取的 LLM。
            embedder (Embeddings): 用于索引的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoList 的其他参数。
        """
        super().__init__(
            item_schema=SegmentPerformanceItem,
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
        可视化业务板块业绩列表。

        Args:
            top_k_for_search (int): 检索的条目数。默认 3。
            top_k_for_chat (int): 对话上下文中的条目数。默认 3。
        """

        def label_extractor(item: SegmentPerformanceItem) -> str:
            rev = f" | {item.revenue}" if item.revenue else ""
            return f"{item.segment_name} ({item.segment_type}){rev}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
