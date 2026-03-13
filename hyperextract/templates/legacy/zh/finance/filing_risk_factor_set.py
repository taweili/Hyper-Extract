"""申报风险因素集 - 对 SEC 申报文件中的风险因素进行去重和归类。

从 10-K/10-Q 申报文件的第1A项中提取并规范化风险因素披露，
跟踪不同申报期间的新增和删除，用于风险演变监控。
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class RiskFactorItem(BaseModel):
    """
    SEC 申报文件中披露的单项风险因素。
    """

    risk_title: str = Field(
        description="风险因素的简明标题（例如 '网络安全漏洞风险'、'外汇敞口'）。"
    )
    risk_category: str = Field(
        description="类别：'市场'、'运营'、'监管'、'财务'、'战略'、'网络安全'、'ESG'、'法律'、'地缘政治'。"
    )
    description: str = Field(
        description="申报文件中披露的风险完整描述。"
    )
    potential_impact: Optional[str] = Field(
        None,
        description="所述的潜在财务或运营影响（例如 '对营收产生重大不利影响'）。",
    )
    affected_areas: Optional[List[str]] = Field(
        None,
        description="受影响的业务板块或职能（例如 ['国际业务', '供应链']）。",
    )
    mitigation_disclosed: Optional[str] = Field(
        None,
        description="公司已披露的任何缓解措施或管控手段。",
    )
    is_new: Optional[bool] = Field(
        None,
        description="与前期申报相比，该风险因素是否为新增。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = """## 角色与任务
你是一位专业的监管申报分析师，请从 SEC 申报文件的风险因素章节中提取并归类所有单项风险因素。

## 提取规则
### 核心约束
1. 每个元素对应一个独立的实体，禁止合并
2. 实体名称与原文保持一致

### 领域特定规则
- **规范化**: 将相关的风险描述归纳到一个简明的风险标题下
- **分类**: 将每项风险归入其主要类别
- **完整性**: 提取每一个不同的风险因素，即使只是简要提及
- **累积合并**: 如果同一风险在不同章节中出现了更多细节，则合并相关信息

## 源文本:
{source_text}
"""

# ==============================================================================
# 3. 模板类
# ==============================================================================


class FilingRiskFactorSet(AutoSet[RiskFactorItem]):
    """
    适用文档: SEC 10-K 第1A项（风险因素）、10-Q 风险因素更新、
    S-1 招股说明书风险章节、20-F 风险披露。

    模板用于从监管申报文件中构建去重的风险因素注册表。
    利用 AutoSet 的键值累积机制，将不同章节或不同申报期间的风险披露合并为
    全面的风险目录。

    使用示例:
        >>> risk_set = FilingRiskFactorSet(llm_client=llm, embedder=embedder)
        >>> filing = "第1A项 风险因素：我们面临重大网络安全风险..."
        >>> risk_set.feed_text(filing)
        >>> risk_set.show()
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
        初始化申报风险因素集模板。

        Args:
            llm_client (BaseChatModel): 用于风险因素提取的 LLM。
            embedder (Embeddings): 用于检索的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoSet 的其他参数。
        """
        super().__init__(
            item_schema=RiskFactorItem,
            key_extractor=lambda x: x.risk_title,
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
        可视化风险因素注册表。

        Args:
            top_k_for_search (int): 检索的条目数。默认 3。
            top_k_for_chat (int): 对话上下文中的条目数。默认 3。
        """

        def item_label_extractor(item: RiskFactorItem) -> str:
            return f"[{item.risk_category}] {item.risk_title}"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
