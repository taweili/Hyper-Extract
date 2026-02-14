"""外交事件与条约 - 提取多方历史事件。

模型化多个国家同时参与的复杂外交事件，如条约和国际会议。
"""

from typing import Any, Optional, Tuple, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph

class CountrySchema(BaseModel):
    entity_id: str = Field(..., description="唯一标识符")
    country_name: str = Field(..., description="国家/民族名称")

class DiplomaticEventSchema(BaseModel):
    hyperedge_id: str = Field(..., description="唯一标识符")
    event_type: str = Field(..., description="'条约'、'会议'、'联盟'等")
    event_name: str = Field(..., description="事件名称，如'凡尔赛条约'")
    signing_date: Optional[str] = Field(None, description="事件日期")
    member_countries: List[str] = Field(default_factory=list, description="所有参与国")
    key_terms: Optional[str] = Field(None, description="关键条款摘要")
    leading_country: Optional[str] = Field(None, description="主导或发起国")

_PROMPT = """从文本中提取节点（国家）和超边（外交事件）。
超边连接参与单一事件的多个国家。

### 源文本：
"""

_NODE_PROMPT = """提取文本中提到的所有国家/民族名称。"""

_EDGE_PROMPT = """提取涉及多个国家的外交事件。为每个事件在member_countries字段列出所有参与国。"""

class DiplomaticEventHypergraph(AutoHypergraph[CountrySchema, DiplomaticEventSchema]):
    """适用于：条约、国际会议记录、外交史

    提取进行多方外交事件为同时连接多个国家的超边。非常适合建模复杂的国际协议。
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        super().__init__(
            node_schema=CountrySchema,
            edge_schema=DiplomaticEventSchema,
            node_key_extractor=lambda x: x.country_name.strip().lower(),
            edge_key_extractor=lambda x: f"{x.event_name.lower()}",
            nodes_in_edge_extractor=lambda x: tuple(
                c.strip().lower() for c in x.member_countries
            ),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(self, *, top_k_for_search: int = 5, top_k_for_chat: int = 5) -> None:
        def node_label(node: CountrySchema) -> str:
            return f"🏛️ {node.country_name}"
        def edge_label(edge: DiplomaticEventSchema) -> str:
            return f"{edge.event_type}：{edge.event_name}"
        super().show(
            node_label_extractor=node_label,
            edge_label_extractor=edge_label,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
