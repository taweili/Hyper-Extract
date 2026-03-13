"""备件消耗清单 - 从设备维护记录中提取零件型号、数量、更换原因。

适用于备件管理、维护报告、维修工单等文本。
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList


class ReplacementItem(BaseModel):
    """
    单项备件更换记录。
    """

    part_name: str = Field(
        description="备件名称（例如：轴承、密封圈、滤芯、润滑油、刀片等）。"
    )
    part_number: Optional[str] = Field(
        None, description="备件型号或编号（例如：SKF-6205、GB/T1234-2010）。"
    )
    quantity: Optional[str] = Field(
        None, description="更换数量（例如：2件、5升、1套）。"
    )
    unit: Optional[str] = Field(
        None, description="计量单位（例如：件、个、套、升、公斤）。"
    )
    replacement_reason: Optional[str] = Field(
        None, description="更换原因（例如：磨损、老化、损坏、预防性更换）。"
    )
    equipment_name: Optional[str] = Field(
        None, description="所属设备名称（例如：离心泵P-101、空压机C-001）。"
    )
    maintenance_type: Optional[str] = Field(
        None, description="维护类型：例行保养、故障维修、计划检修、抢修。"
    )


_PROMPT = """## 角色与任务
你是一位设备维护管理专家，请从备件更换记录中提取所有备件消耗条目。

## 提取规则
### 核心约束
1. 每个条目对应一个独立的备件，禁止合并
2. 备件名称和型号与原文保持一致

### 领域特定规则
- 提取备件名称、型号、编号
- 提取更换数量和计量单位
- 提取更换原因（磨损、老化、损坏、预防性更换等）
- 提取所属设备名称
- 识别维护类型（例行保养、故障维修、计划检修、抢修）

## 备件更换记录:
{source_text}
"""


class PartReplacementList(AutoList[ReplacementItem]):
    """
    适用文档: 备件管理台账、维修工单、维护报告、
    设备检修记录。

    模板用于从设备维护记录中提取备件消耗清单，
    支持备件管理和采购计划制定。

    使用示例:
        >>> replacement = PartReplacementList(llm_client=llm, embedder=embedder)
        >>> record = "2024年3月15日，对离心泵P-101进行检修，更换轴承SKF-6205 2件..."
        >>> replacement.feed_text(record)
        >>> replacement.show()
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
        初始化备件消耗清单模板。

        Args:
            llm_client (BaseChatModel): 用于备件提取的 LLM。
            embedder (Embeddings): 用于索引的嵌入模型。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoList 的其他参数。
        """
        super().__init__(
            item_schema=ReplacementItem,
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
        可视化备件消耗清单。

        Args:
            top_k_for_search (int): 检索的条目数。默认 3。
            top_k_for_chat (int): 对话上下文中的条目数。默认 3。
        """

        def label_extractor(item: ReplacementItem) -> str:
            qty = f" x{item.quantity}" if item.quantity else ""
            return f"{item.part_name}{qty} ({item.replacement_reason or ''})"

        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
