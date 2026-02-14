"""股权结构穿透 - 提取所有权和控制关系。

构建股权图显示投资关系、控制结构和通过企业金字塔的最终实益所有权。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

class EntitySchema(BaseModel):
    entity_id: str = Field(..., description="唯一标识符")
    entity_type: str = Field(..., description="'公司'、'个人'或'基金'")
    entity_name: str = Field(..., description="法人名称")
    registration_number: Optional[str] = Field(None, description="登记号或身份证号")

class EquityRelationshipSchema(BaseModel):
    source_entity: str = Field(..., description="股东/所有者名称")
    target_entity: str = Field(..., description="公司/实体名称")
    relationship_type: str = Field(..., description="'持股'、'控制'、'任职为'")
    stake_percentage: Optional[str] = Field(None, description="所有权百分比")
    context: Optional[str] = Field(None, description="附加背景信息")

_PROMPT = """提取企业实体及其所有权/控制关系。"""

_NODE_PROMPT = """提取所有实体：公司、个人、基金。"""

_EDGE_PROMPT = """提取实体之间的所有权和控制关系。仅连接已知实体列表中的实体。"""

class CorporateEquityGraph(AutoGraph[EntitySchema, EquityRelationshipSchema]):
    """适用于：尽职调查报告、招股说明书、企业备案

    通过多级股权链提取企业所有权结构和最终实益所有权。
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
            node_schema=EntitySchema,
            edge_schema=EquityRelationshipSchema,
            node_key_extractor=lambda x: x.entity_name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source_entity.lower()}|{x.relationship_type.lower()}|{x.target_entity.lower()}"
            ),
            nodes_in_edge_extractor=lambda x: (x.source_entity.lower(), x.target_entity.lower()),
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
        def node_label(node: EntitySchema) -> str:
            type_icon = {"公司": "🏢", "个人": "👤", "基金": "💼"}
            icon = type_icon.get(node.entity_type, "●")
            return f"{icon} {node.entity_name}"
        def edge_label(edge: EquityRelationshipSchema) -> str:
            pct = f" ({edge.stake_percentage})" if edge.stake_percentage else ""
            return f"{edge.relationship_type}{pct}"
        super().show(
            node_label_extractor=node_label,
            edge_label_extractor=edge_label,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
