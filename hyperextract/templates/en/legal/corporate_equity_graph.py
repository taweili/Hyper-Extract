"""Corporate Equity Graph - Extracts ownership and control relationships.

Builds a shareholding graph showing investment relationships, control structures,
and ultimate beneficial ownership through corporate pyramids.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

class EntitySchema(BaseModel):
    entity_id: str = Field(..., description="Unique identifier")
    entity_type: str = Field(..., description="'Company', 'Individual', or 'Fund'")
    entity_name: str = Field(..., description="Legal name")
    registration_number: Optional[str] = Field(None, description="Registration or ID number")

class EquityRelationshipSchema(BaseModel):
    source_entity: str = Field(..., description="Shareholder/owner name")
    target_entity: str = Field(..., description="Company/entity name")
    relationship_type: str = Field(..., description="'Owns_Shares', 'Controls', 'Serves_As_Officer'")
    stake_percentage: Optional[str] = Field(None, description="Ownership percentage")
    context: Optional[str] = Field(None, description="Additional context")

_PROMPT = """Extract corporate entities and their ownership/control relationships."""

_NODE_PROMPT = """Extract all entities: companies, individuals, funds mentioned."""

_EDGE_PROMPT = """Extract ownership and control relationships between entities.
Only connect entities from the known entity list."""

class CorporateEquityGraph(AutoGraph[EntitySchema, EquityRelationshipSchema]):
    """Applicable to: Due diligence reports, Prospectuses, Corporate filings

    Extracts corporate ownership structures and ultimate beneficial ownership through
    multi-level equity chains.
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
            type_icon = {"Company": "🏢", "Individual": "👤", "Fund": "💼"}
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
