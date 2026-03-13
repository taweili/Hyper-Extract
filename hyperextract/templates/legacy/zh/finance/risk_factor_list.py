"""风险因素列表 - 从股票研究报告中提取下行风险。

列出分析师识别的具体下行风险，包括监管、汇率、供应链等
风险类别，用于风险监控。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class RiskItem(BaseModel):
    """
    股票研究中识别的一项具体下行风险。
    """

    risk_name: str = Field(
        description="风险的简洁名称（例如 '欧盟监管收紧'、'强势美元带来的汇率逆风'）。"
    )
    risk_category: str = Field(
        description="类别：'监管'、'竞争'、'宏观经济'、'运营'、'汇率/货币'、"
        "'地缘政治'、'技术'、'法律/诉讼'、'ESG'、'执行'。"
    )
    description: str = Field(description="风险情景的详细描述。")
    potential_impact: Optional[str] = Field(
        None,
        description="估计的财务影响（例如 '收入下行 3-5%'、'每股收益风险 $0.50'）。",
    )
    probability: Optional[str] = Field(
        None,
        description="分析师的概率评估：'高'、'中等'、'低'。",
    )
    time_horizon: Optional[str] = Field(
        None,
        description="风险可能兑现的时间（例如 '近期'、'2025 年'、'12-18 个月'）。",
    )


_PROMPT = """## 角色与任务
你是一位专业的风险分析师，请从文本中提取所有下行风险和风险因素。

## 提取规则
### 核心约束
1. 每个条目对应一个独立的实体，禁止合并
2. 实体名称与原文保持一致

### 领域特定规则
- 提取每一个不同的风险因素
- 对每项风险进行适当分类
- 在提供量化影响估算时予以捕获
- 记录概率评估和时间范围

## 源文本:
{source_text}
"""


class RiskFactorList(AutoList[RiskItem]):
    """
    适用文档: 股票研究报告（风险章节）、投资委员会备忘录、投资组合风险评估、分析师降级笔记。

    模板用于从股票研究中提取下行风险。每项风险作为独立列表项捕获，
    用于风险监控和投资组合风险评估。

    使用示例:
        >>> risks = RiskFactorList(llm_client=llm, embedder=embedder)
        >>> report = "主要风险包括：1) 欧盟数字市场法合规成本..."
        >>> risks.feed_text(report)
        >>> risks.show()
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
        初始化风险因素列表模板。

        Args:
            llm_client (BaseChatModel): 用于风险提取的 LLM。
            embedder (Embeddings): 用于索引的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoList 的其他参数。
        """
        super().__init__(
            item_schema=RiskItem,
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
        可视化风险因素列表。

        Args:
            top_k_for_search (int): 检索的条目数。默认 3。
            top_k_for_chat (int): 对话上下文中的条目数。默认 3。
        """

        def label_extractor(item: RiskItem) -> str:
            return f"[{item.risk_category}] {item.risk_name}"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
