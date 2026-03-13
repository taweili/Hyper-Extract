"""田间观测清单 - 从巡田报告中提取结构化的田间观测记录。

适用于巡田报告、田间调查记录、农作物病虫害调查记录。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class FieldObservation(BaseModel):
    """田间观测记录条目"""

    plot_id: str = Field(description="地块编号")
    crop: str = Field(description="作物种类和品种")
    growth_stage: str = Field(description="当前生长阶段")
    observation_date: str = Field(description="观测日期，统一格式为年-月-日（如2025-06-15）")
    issues: List[str] = Field(description="观测到的问题列表，如杂草、虫害、病害、生长异常")
    severity_level: str = Field(description="严重等级：轻微、中等、严重")
    recommendations: List[str] = Field(description="建议措施列表")


_PROMPT = """## 角色与任务
你是一位专业的农技人员，请从巡田报告中提取结构化的田间观测记录。

## 核心概念定义
- **条目 (Item)**：从文本中提取的每一次巡田记录，包含地块信息、作物状态、病虫害问题及建议措施

## 提取规则
### 核心约束
1. 每个地块的观测记录提取为一个独立的条目
2. 问题列表和建议措施列表必须完整提取
3. 严重等级必须明确提取

### 领域特定规则
- 地块编号：如D-001、A-12、光明村一组北畈等
- 生长阶段：播种期、幼苗期、分蘖期、孕穗抽穗期、灌浆成熟期
- 问题类型：杂草、虫害、病害、生长异常、肥害、药害
- 严重等级：轻微（可忽略或轻微影响）、中等（需要关注或部分影响）、严重（必须处理或严重影响）

## 巡田报告:
{source_text}
"""


class FieldObservationList(AutoList[FieldObservation]):
    """
    适用文档: 巡田报告、田间调查记录、农作物病虫害调查记录

    功能介绍:
    从巡田报告中提取结构化的田间观测记录，包含地块编号、作物种类、
    生长阶段、观测到的问题、严重等级及建议措施。
    适用于巡田日志数字化、病虫害预警、农情监测。

    Example:
        >>> template = FieldObservationList(llm_client=llm, embedder=embedder)
        >>> template.feed_text("地块D-001水稻处于分蘖期，发现稻飞虱约15头/百丛，严重等级轻微...")
        >>> print(template.data)
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
        初始化田间观测清单模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            chunk_size: 每个分块的最大字符数，默认为 2048
            chunk_overlap: 分块之间的重叠字符数，默认为 256
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=FieldObservation,
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
        可视化田间观测清单。

        Args:
            top_k_for_search (int): 检索的条目数。默认 3。
            top_k_for_chat (int): 对话上下文中的条目数。默认 3。
        """

        def item_label_extractor(item: FieldObservation) -> str:
            return f"{item.plot_id} | {item.crop} | {item.growth_stage}"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
