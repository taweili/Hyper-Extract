"""Diplomatic Event Hypergraph - Extracts multi-party historical events.

Models complex diplomatic events where multiple nations participate simultaneously,
such as treaties and international conferences.
"""

from typing import Any, Optional, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class CountrySchema(BaseModel):
    entity_id: str = Field(..., description="Unique identifier")
    country_name: str = Field(..., description="Name of the country/nation")


class DiplomaticEventSchema(BaseModel):
    hyperedge_id: str = Field(..., description="Unique identifier")
    event_type: str = Field(..., description="'Treaty', 'Conference', 'Alliance', etc.")
    event_name: str = Field(
        ..., description="Name of the event (e.g., 'Treaty of Versailles')"
    )
    member_countries: List[str] = Field(
        default_factory=list, description="All participating countries"
    )
    details: Optional[str] = Field(
        None, description="Signing date, key terms, leading countries, and outcomes."
    )


_PROMPT = """Extract nodes (countries) and hyperedges (diplomatic events) from the text.
A hyperedge connects multiple countries participating in a single event.

### Source Text:
"""

_NODE_PROMPT = """Extract all country/nation names mentioned in the text."""

_EDGE_PROMPT = """Extract diplomatic events involving multiple countries.
For each event, list all participating countries in member_countries.
Combine key terms, signing date, and outcomes into the 'details' field."""


class DiplomaticEventHypergraph(AutoHypergraph[CountrySchema, DiplomaticEventSchema]):
    """Applicable to: Treaties, International conference records, Diplomatic history

    Extracts multi-party diplomatic events as hyperedges connecting multiple nations
    simultaneously. Perfect for modeling complex international agreements.
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
            return f"{edge.event_type}: {edge.event_name}"

        super().show(
            node_label_extractor=node_label,
            edge_label_extractor=edge_label,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
