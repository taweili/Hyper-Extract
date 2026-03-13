"""物种名录 - 从生物多样性调查报告中提取物种观测记录及种群数量信息。

适用于生物多样性调查报告、生态调查记录、物种观测清单。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet


class SpeciesRecord(BaseModel):
    """物种记录"""
    species_name: str = Field(description="物种中文名称")
    latin_name: str = Field(description="拉丁学名", default="")
    category: str = Field(description="类别：脊椎动物、无脊椎动物、植物、微生物")
    population_count: str = Field(description="种群数量，如约120只、约850只")
    protection_level: str = Field(description="保护级别：国家一级保护、国家二级保护、地方保护、无保护", default="无保护")
    habitat: str = Field(description="栖息地或分布区域", default="")
    observation_details: str = Field(description="观测详情，包括观测时间、地点和数量记录", default="")


_PROMPT = """## 角色与任务
你是一位专业的生态学专家，请从“调查报告”中提取所有物种观测记录，构建物种名录。

## 提取规则
### 核心约束
1. 每个物种只能对应一个唯一的记录，根据物种名称进行去重
2. 物种名称与原文保持一致
3. 汇总所有观测报告中提到的物种及其种群数量

### 领域特定规则
- 保护级别：国家一级保护、国家二级保护、地方保护、无保护
- 类别：脊椎动物（鱼类、两栖类、爬行类、鸟类、哺乳动物）、无脊椎动物（昆虫、螺类、蚌类等）、植物（高等植物、藻类、苔藓）
- 种群数量：使用原文中的数量描述，如"约120只"、"约850尾"

## 调查报告:
{source_text}
"""


class BiodiversityRegistry(AutoSet[SpeciesRecord]):
    """
    适用文档: 生物多样性调查报告、生态调查记录、物种观测清单

    功能介绍:
    去重汇总调查报告中观测到的所有物种及其种群数量信息。
    适用于物种清单制作、保护优先级评估和生物多样性监测。

    Example:
        >>> template = BiodiversityRegistry(llm_client=llm, embedder=embedder)
        >>> template.feed_text("本次调查共记录鸟类186种，其中国家一级保护鸟类7种...")
        >>> print(len(template.items))
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化物种名录模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=SpeciesRecord,
            key_extractor=lambda x: x.species_name,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k: int = 3,
    ):
        """
        展示物种名录。

        Args:
            top_k: 问答使用的条目数量，默认为 3
        """

        def label_extractor(item: SpeciesRecord) -> str:
            return f"{item.species_name} ({item.latin_name})"

        super().show(
            label_extractor=label_extractor,
            top_k=top_k,
        )
