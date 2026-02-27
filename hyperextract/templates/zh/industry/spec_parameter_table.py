"""核心规格表 - 从技术规格书中提取额定功率、材质、尺寸精度等关键技术指标。

适用于设备台账、技术规格书、产品数据表等文本。
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from ontomem.merger import MergeStrategy
from hyperextract.types import AutoModel


class SpecParameterTableSchema(BaseModel):
    """
    从技术规格书中提取的核心技术参数。
    """

    equipment_name: str = Field(
        ..., description="设备或产品名称（例如：数控加工中心、离心泵、变压器等）。"
    )
    model_number: Optional[str] = Field(None, description="型号或规格代号。")
    manufacturer: Optional[str] = Field(None, description="制造商或供应商。")
    rated_power: Optional[str] = Field(
        None, description="额定功率（例如：55kW、200kVA、15kW/20kW）。"
    )
    rated_voltage: Optional[str] = Field(
        None, description="额定电压（例如：380V、10kV、220V）。"
    )
    rated_current: Optional[str] = Field(
        None, description="额定电流（例如：100A、50Hz）。"
    )
    frequency: Optional[str] = Field(None, description="工作频率（例如：50Hz、60Hz）。")
    material: Optional[str] = Field(
        None, description="主要材质或材料（例如：不锈钢304、铸铁、铝合金）。"
    )
    dimensions: Optional[str] = Field(
        None, description="外形尺寸或安装尺寸（例如：2000×1500×1800mm）。"
    )
    weight: Optional[str] = Field(
        None, description="重量或质量（例如：2500kg、5.8t）。"
    )
    accuracy: Optional[str] = Field(
        None, description="精度等级或精度指标（例如：±0.01mm、IT7级）。"
    )
    temperature_range: Optional[str] = Field(
        None, description="工作温度范围（例如：-20℃~50℃、0~80℃）。"
    )
    pressure_range: Optional[str] = Field(
        None, description="工作压力范围（例如：0~1.6MPa、PN16）。"
    )
    flow_rate: Optional[str] = Field(
        None, description="流量参数（例如：100m³/h、50L/min）。"
    )
    speed: Optional[str] = Field(
        None, description="转速或速度（例如：1450rpm、0.5~2m/s）。"
    )
    capacity: Optional[str] = Field(
        None, description="容量或处理能力（例如：500L、10m³/h）。"
    )
    protection_level: Optional[str] = Field(
        None, description="防护等级（例如：IP65、IP55）。"
    )
    insulation_class: Optional[str] = Field(
        None, description="绝缘等级（例如：F级、H级）。"
    )
    other_parameters: Optional[List[str]] = Field(
        None, description="其他关键技术参数列表（如适用）。"
    )


_PROMPT = """## 角色与任务
你是一位工业设备技术专家，请从技术规格书中提取所有关键技术参数。

## 提取规则
### 核心约束
1. 每个对象对应一个独立的设备或产品，禁止合并
2. 参数值与原文保持一致

### 领域特定规则
- 提取设备名称、型号、制造商
- 提取电气参数：额定功率、额定电压、额定电流、频率
- 提取物理参数：材质、尺寸、重量、精度
- 提取工况参数：温度范围、压力范围、流量、转速
- 提取性能参数：容量、防护等级、绝缘等级
- 保留原始单位，不要换算

### 源文本:
"""


class SpecParameterTable(AutoModel[SpecParameterTableSchema]):
    """
    适用文档: 设备台账、技术规格书、产品数据表、
    设备出厂参数文档。

    模板用于从技术规格书中提取核心规格参数，
    整合为结构化数据对象，用于设备台账管理和选型参考。

    使用示例:
        >>> spec = SpecParameterTable(llm_client=llm, embedder=embedder)
        >>> spec_text = "数控加工中心：型号VMC-850，额定功率15kW，额定电压380V..."
        >>> spec.feed_text(spec_text)
        >>> print(spec.data)
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
        初始化核心规格表模板。

        Args:
            llm_client (BaseChatModel): 用于参数提取的 LLM。
            embedder (Embeddings): 用于索引的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoModel 的其他参数。
        """
        super().__init__(
            data_schema=SpecParameterTableSchema,
            llm_client=llm_client,
            embedder=embedder,
            strategy_or_merger=MergeStrategy.LLM.BALANCED,
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
        展示规格参数。

        Args:
            top_k (int): 展示的规格数量。
        """

        def label_extractor(data: SpecParameterTableSchema) -> str:
            return f"{data.equipment_name} ({data.model_number or ''})"

        super().show(label_extractor=label_extractor, top_k=top_k)
