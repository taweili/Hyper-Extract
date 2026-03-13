"""关键位点模型 - 从蛋白质结构文献中提取活性位点、结合位点的残基信息。

适用于蛋白质结构文献、药物设计报告、酶学研究。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class ResidueDetail(BaseModel):
    """残基详情"""

    position: str = Field(description="残基位置编号，如Asp204、Phe286")
    amino_acid: str = Field(description="氨基酸名称，如天冬氨酸、苯丙氨酸")
    role: str = Field(description="在位点中的角色：配体结合、催化、结构支撑")


class BindingSite(BaseModel):
    """蛋白质关键位点模型"""

    protein_name: str = Field(description="蛋白质名称，如β2-肾上腺素受体")
    site_type: str = Field(
        description="位点类型：活性位点、结合位点、修饰位点、别构位点"
    )
    residue_numbers: str = Field(description="关键残基编号范围，如Asp169-Lys210")
    residue_details: List[ResidueDetail] = Field(description="关键残基详情列表")
    chemical_properties: str = Field(
        description="化学性质描述，如疏水口袋、氢键网络、金属离子结合位点"
    )
    function_annotation: str = Field(
        description="功能注解，如配体识别、底物特异性、信号转导"
    )
    ligand_info: str = Field(description="配体信息，如结合的配体分子或药物", default="")


_PROMPT = """## 角色与任务
你是一位专业的结构生物学专家，请从文本中提取蛋白质的关键位点信息。

## 提取规则
### 核心约束
1. 识别文本中描述的核心蛋白质及其位点
2. 提取位点的类型（活性位点、结合位点、修饰位点等）
3. 提取关键残基的编号、化学性质和功能

### 领域特定规则
- 残基编号：使用标准编号系统，如Asp204表示第204位天冬氨酸
- 氨基酸中文名称：天冬氨酸(Asp)、苯丙氨酸(Phe)、赖氨酸(Lys)、精氨酸(Arg)等
- 位点类型：活性位点（直接参与催化）、结合位点（结合底物或配体）、修饰位点（可被修饰）
- 化学性质：疏水、亲水、极性、带电荷等

## 蛋白质结构描述源文本:
{source_text}
"""


class BindingSiteModel(AutoModel[BindingSite]):
    """
    适用文档: 蛋白质结构文献、药物设计报告、酶学研究

    功能介绍:
    提取蛋白质活性位点、结合位点的残基编号、化学性质及功能注解。
    适用于药物设计、位点突变分析和酶学研究。

    Example:
        >>> template = BindingSiteModel(llm_client=llm, embedder=embedder)
        >>> template.feed_text("β2-AR的配体结合口袋位于TM螺旋核心，Asp204与配体形成盐桥...")
        >>> print(template.data.protein_name)
        >>> print(template.data.residue_details)
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
        初始化关键位点模型模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            data_schema=BindingSite,
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
        展示关键位点信息。

        Args:
            top_k: 问答使用的条目数量，默认为 3
        """

        def label_extractor(item: BindingSite) -> str:
            return f"{item.protein_name} - {item.site_type}"

        super().show(
            label_extractor=label_extractor,
            top_k=top_k,
        )
