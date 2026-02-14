"""考古文物档案 - 从历史文献中提取文物信息。

通过合并博物馆目录、考古报告和文物描述中的数据来构建统一的文物知识库。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

class ArtifactSchema(BaseModel):
    artifact_name: str = Field(..., description="文物的官方名称")
    period: Optional[str] = Field(None, description="历史时期、朝代或大概年份")
    location: Optional[str] = Field(None, description="出土地点、发现处及当前所属博物馆")
    physical_traits: Optional[str] = Field(None, description="材质、尺寸、重量及工艺特征")
    significance: Optional[str] = Field(None, description="文化意义、用途描述及象征价值")

_PROMPT = """你是一位专业的考古学家。从文本中提取文物信息。

字段指南：
1. **artifact_name**：文物名称
2. **period**：所属的历史时期
3. **location**：合并出土地点和目前馆藏地
4. **physical_traits**：描述材质、大小和制作工艺
5. **significance**：描述文物的历史价值、用途和象征意义

仅提取明确提及的信息。

### 源文本：
"""

class CulturalArtifactRegistry(AutoSet[ArtifactSchema]):
    """适用于：博物馆目录、考古报告、文物文档

    通过自动合并来自多个历史来源的信息来提取全面的文物百科。
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
            item_schema=ArtifactSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.artifact_name.strip().lower(),
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(self, *, top_k_for_search: int = 3, top_k_for_chat: int = 3) -> None:
        def label_extractor(item: ArtifactSchema) -> str:
            period = f" ({item.period})" if item.period else ""
            return f"{item.artifact_name}{period}"
        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
