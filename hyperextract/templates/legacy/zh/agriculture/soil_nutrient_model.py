"""土壤养分模型 - 从土壤检测报告中提取核心理化指标。

适用于土壤检测报告、测土配方施肥报告、地力评价报告。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class SoilNutrient(BaseModel):
    """土壤养分模型"""

    plot_id: str = Field(description="地块编号")
    soil_type: Optional[str] = Field(description="土壤类型")
    ph: Optional[float] = Field(description="pH值")
    ph_level: Optional[str] = Field(
        description="pH丰缺等级：酸性、弱酸性、中性、弱碱性、碱性"
    )
    organic_matter: Optional[float] = Field(description="有机质含量，单位g/kg")
    organic_matter_level: Optional[str] = Field(description="有机质丰缺等级")
    nitrogen: Optional[float] = Field(description="碱解氮含量，单位mg/kg")
    nitrogen_level: Optional[str] = Field(description="氮素丰缺等级")
    phosphorus: Optional[float] = Field(description="有效磷含量，单位mg/kg")
    phosphorus_level: Optional[str] = Field(description="磷素丰缺等级")
    potassium: Optional[float] = Field(description="速效钾含量，单位mg/kg")
    potassium_level: Optional[str] = Field(description="钾素丰缺等级")
    calcium: Optional[float] = Field(description="交换性钙含量，单位mg/kg")
    magnesium: Optional[float] = Field(description="交换性镁含量，单位mg/kg")
    sulfur: Optional[float] = Field(description="有效硫含量，单位mg/kg")
    iron: Optional[float] = Field(description="有效铁含量，单位mg/kg")
    manganese: Optional[float] = Field(description="有效锰含量，单位mg/kg")
    copper: Optional[float] = Field(description="有效铜含量，单位mg/kg")
    zinc: Optional[float] = Field(description="有效锌含量，单位mg/kg")
    boron: Optional[float] = Field(description="有效硼含量，单位mg/kg")


_PROMPT = """## 角色与任务
你是一位专业的土壤肥料专家，请从土壤检测报告中提取土壤养分指标。

## 核心概念定义
- **对象 (Object)**：从文本中提取的土壤养分数据，包含pH、有机质、大量元素、中微量元素等指标

## 提取规则
### 核心约束
1. 每个文档只提取一个土壤养分模型对象
2. 检测值和丰缺等级必须同时提取
3. 数值保留原始精度，单位按照原文

### 领域特定规则
- 土壤类型：潴育性水稻土、淹育型水稻土、潜育型水稻土、红壤、黄壤等
- 丰缺等级：缺乏、偏低、适宜、丰富、极丰富
- pH等级：酸性（<6.0）、弱酸性（6.0-6.5）、中性（6.5-7.0）、弱碱性（7.0-7.5）、碱性（>7.5）

## 土壤检测报告:
{source_text}
"""


class SoilNutrientModel(AutoModel[SoilNutrient]):
    """
    适用文档: 土壤检测报告、测土配方施肥报告、地力评价报告

    功能介绍:
    从土壤检测报告中提取核心理化指标，包括pH、有机质、大量元素（N-P-K）、
    中量元素（Ca、Mg、S）、微量元素（Fe、Mn、Cu、Zn、B）等，
    适用于测土配方施肥、地力等级评价。

    Example:
        >>> template = SoilNutrientModel(llm_client=llm, embedder=embedder)
        >>> template.feed_text("土壤检测报告显示：pH值5.2，有机质18.5g/kg...")
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
        初始化土壤养分模型模板。

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
            data_schema=SoilNutrient,
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
        top_k: int = 3,
    ):
        """
        展示土壤养分信息。

        Args:
            top_k: 问答使用的条目数量，默认为 3
        """

        def label_extractor(item: SoilNutrient) -> str:
            parts = [f"pH: {item.ph} ({item.ph_level})" if item.ph else "pH: N/A"]
            if item.organic_matter:
                parts.append(f"有机质: {item.organic_matter}g/kg")
            if item.nitrogen:
                parts.append(f"碱解氮: {item.nitrogen}mg/kg")
            if item.phosphorus:
                parts.append(f"有效磷: {item.phosphorus}mg/kg")
            if item.potassium:
                parts.append(f"速效钾: {item.potassium}mg/kg")
            return f"{item.plot_id} | {item.soil_type} | " + " | ".join(parts)

        super().show(
            label_extractor=label_extractor,
            top_k=top_k,
        )
