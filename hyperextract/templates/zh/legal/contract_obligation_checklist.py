"""法定义务审查 - 从合同中提取义务和禁止条款。

通过提取所有义务、责任和限制而无去重来构建全面的合规清单，保留完整的审计记录。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList

class ObligationSchema(BaseModel):
    obligated_party: str = Field(..., description="负责履行的当事人")
    obligation_type: str = Field(..., description="'必须'(要求)或'不得'(禁止)")
    action_description: str = Field(..., description="具体行动或要求")
    trigger_condition: Optional[str] = Field(None, description="何时/何种情况下义务适用")
    breach_penalty: Optional[str] = Field(None, description="不履行的后果")
    clause_reference: Optional[str] = Field(None, description="原合同条款号")

_PROMPT = """你是一位合同律师和合规审计员。
从合同中提取所有义务和限制：
1. obligated_party：谁必须履行
2. obligation_type：必须(要求)或不得(禁止)
3. action_description：具体行动/要求
4. trigger_condition：义务何时适用
5. breach_penalty：不合规罚款
6. clause_reference：合同条款号

独立提取每个义务。无合并。

### 源文本：
"""

class ContractObligationChecklist(AutoList[ObligationSchema]):
    """适用于：合同、服务条款、协议、合规文件

    提取完整的合规清单，保留每个义务单独存在，用于全面的审计和风险分析。
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        super().__init__(
            item_schema=ObligationSchema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(self, *, top_k_for_search: int = 3, top_k_for_chat: int = 3) -> None:
        def label_extractor(item: ObligationSchema) -> str:
            return f"{item.obligation_type}：{item.action_description[:50]}"
        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
