"""判例法要旨库 - 提取和索引法律判例。

通过自动合并来自多个来源关于同一案件的信息来构建可搜索的法律判例数据库。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

class PrecedentSchema(BaseModel):
    case_citation: str = Field(..., description="官方案号/引用")
    court_name: Optional[str] = Field(None, description="做出决定的法院")
    judgment_year: Optional[str] = Field(None, description="判决年份")
    legal_issues: Optional[str] = Field(None, description="提出的法律问题")
    holding: Optional[str] = Field(None, description="法院的判决和法律原则")
    cited_statutes: Optional[str] = Field(None, description="判决中引用的法律")
    presiding_judges: Optional[str] = Field(None, description="做出决定的法官")
    impact_assessment: Optional[str] = Field(None, description="对后续法律的影响")

_PROMPT = """你是一位法律研究专家。
提取判例案件信息：
1. case_citation：官方案名/案号
2. court_name：审理的法院
3. judgment_year：判决年份
4. legal_issues：法律问题
5. holding：法院的判决和原则
6. cited_statutes：适用法律
7. presiding_judges：做出裁定的法官
8. impact_assessment：对未来案件的影响

### 源文本：
"""

class CasePrecedentLibrary(AutoSet[PrecedentSchema]):
    """适用于：法院判决、法律数据库、案例法报告

    通过自动合并来自多个来源的案件信息来提取和索引法律判例，
    成为统一的可搜索库。
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
            item_schema=PrecedentSchema,
            llm_client=llm_client,
            embedder=embedder,
            key_extractor=lambda x: x.case_citation.strip().lower(),
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(self, *, top_k_for_search: int = 3, top_k_for_chat: int = 3) -> None:
        def label_extractor(item: PrecedentSchema) -> str:
            year = f" ({item.judgment_year})" if item.judgment_year else ""
            return f"{item.case_citation}{year}"
        super().show(
            item_label_extractor=label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
