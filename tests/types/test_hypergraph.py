"""Tests for AutoHypergraph - hypergraph extraction pattern."""

import pytest
from pydantic import BaseModel, Field
from typing import List, Tuple
from ontomem.merger import MergeStrategy
from hyperextract.types.hypergraph import AutoHypergraph


class Person(BaseModel):
    """Test schema for hypergraph nodes."""

    name: str = Field(default="", description="Person's name")


class Event(BaseModel):
    """Test schema for hyperedges."""

    event_type: str = Field(default="", description="Type of event")
    participants: List[str] = Field(default_factory=list, description="Names of participants")


class TestAutoHypergraphBasics:
    """Test basic AutoHypergraph functionality."""

    def test_initialization(self, llm_client, embedder):
        """Test AutoHypergraph initialization."""
        hg = AutoHypergraph(
            node_schema=Person,
            edge_schema=Event,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.event_type}_{sorted(x.participants)}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode="two_stage",
        )

        assert hg.node_schema == Person
        assert hg.edge_schema == Event
        assert hg.extraction_mode == "two_stage"
        assert hg.empty() is True

    def test_default_extraction_mode_is_two_stage(self, llm_client, embedder):
        """Test that default extraction mode is two_stage."""
        hg = AutoHypergraph(
            node_schema=Person,
            edge_schema=Event,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.event_type}_{sorted(x.participants)}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
        )

        assert hg.extraction_mode == "two_stage"


class TestAutoHypergraphKeyGeneration:
    """Test key generation and deduplication logic."""

    def test_edge_key_with_sorted_participants(self, llm_client, embedder):
        """Test that edge keys are the same for same participants regardless of order."""
        # Define key extractor with sorting
        def edge_key(event: Event) -> str:
            sorted_participants = "-".join(sorted(event.participants))
            return f"{event.event_type}_{sorted_participants}"

        hg = AutoHypergraph(
            node_schema=Person,
            edge_schema=Event,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=edge_key,
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Two events with same type and participants but different order
        e1 = Event(event_type="meeting", participants=["Alice", "Bob", "Charlie"])
        e2 = Event(event_type="meeting", participants=["Charlie", "Alice", "Bob"])

        key1 = edge_key(e1)
        key2 = edge_key(e2)

        assert key1 == key2
        assert key1 == "meeting_Alice-Bob-Charlie"

    def test_hyperedge_participants_extractor(self, llm_client, embedder):
        """Test that nodes_in_edge_extractor returns all participants."""
        def participants_extractor(event: Event) -> Tuple[str, ...]:
            return tuple(event.participants)

        hg = AutoHypergraph(
            node_schema=Person,
            edge_schema=Event,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.event_type}_{sorted(x.participants)}",
            nodes_in_edge_extractor=participants_extractor,
            llm_client=llm_client,
            embedder=embedder,
        )

        event = Event(event_type="party", participants=["Alice", "Bob", "Dave"])
        participants = participants_extractor(event)

        assert len(participants) == 3
        assert "Alice" in participants
        assert "Bob" in participants
        assert "Dave" in participants


class TestAutoHypergraphExtraction:
    """Test hypergraph extraction."""

    def test_feed_text_populates_hypergraph(self, llm_client, embedder):
        """Test feeding text extracts nodes and hyperedges."""
        hg = AutoHypergraph(
            node_schema=Person,
            edge_schema=Event,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.event_type}_{sorted(x.participants)}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
        )

        hg.feed_text("Alice, Bob, and Charlie had a meeting. They collaborated on a project.")

        assert not hg.empty()
        assert len(hg.data.nodes) > 0

    def test_extract_creates_new_instance(self, llm_client, embedder):
        """Test extract() creates new instance."""
        hg1 = AutoHypergraph(
            node_schema=Person,
            edge_schema=Event,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.event_type}_{sorted(x.participants)}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
        )

        hg2 = hg1.parse("""Annual planning conference brings together CEO, CFO, CTO, 
        VP Marketing, and VP Sales to discuss Q2 revenue targets and product roadmap priorities.""")

        assert hg1 is not hg2
        assert hg1.empty() is True
        assert hg2.empty() is False


class TestAutoHypergraphDeduplication:
    """Test hyperedge deduplication."""

    def test_hyperedge_deduplication_ignores_participant_order(self, llm_client, embedder):
        """Test that hyperedges with same participants in different order are deduplicated."""
        hg = AutoHypergraph(
            node_schema=Person,
            edge_schema=Event,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.event_type}_{sorted(x.participants)}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Create events with same event_type and participants but different order
        e1 = Event(event_type="team_meeting", participants=["Alex", "Bailey", "Casey"])
        e2 = Event(event_type="team_meeting", participants=["Casey", "Alex", "Bailey"])
        e3 = Event(event_type="conference", participants=["Alex", "Bailey", "Casey"])

        # Manually add to edge memory to test deduplication
        hg._edge_memory.add([e1, e2])

        # Should deduplicate e1 and e2 to 1 edge
        assert hg._edge_memory.size == 1

        # Adding e3 should increase count (different event_type)
        hg._edge_memory.add([e3])
        assert hg._edge_memory.size == 2

    def test_multiple_hyperedges_with_different_participants(self, llm_client, embedder):
        """Test that hyperedges with different participants are kept separate."""
        hg = AutoHypergraph(
            node_schema=Person,
            edge_schema=Event,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.event_type}_{sorted(x.participants)}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
        )

        e1 = Event(event_type="meeting", participants=["Alice", "Bob"])
        e2 = Event(event_type="meeting", participants=["Alice", "Charlie"])

        hg._edge_memory.add([e1, e2])

        # Should have 2 different edges
        assert hg._edge_memory.size == 2


class TestAutoHypergraphProperties:
    """Test hypergraph data properties."""

    def test_nodes_property(self, llm_client, embedder):
        """Test accessing nodes from hypergraph."""
        hg = AutoHypergraph(
            node_schema=Person,
            edge_schema=Event,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.event_type}_{sorted(x.participants)}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
        )

        hg.feed_text("""
        Monthly Sync Meeting:
        CEO John, CTO Lisa, and Product Manager Sarah discussed Q2 roadmap.
        John, Lisa, and CFO David negotiated on budget allocation for infrastructure.
        Lisa, Sarah, and QA Lead Tom reviewed test coverage requirements.
        """)

        nodes = hg.data.nodes
        assert isinstance(nodes, list)
        assert all(isinstance(n, Person) for n in nodes)

    def test_edges_property(self, llm_client, embedder):
        """Test accessing edges from hypergraph."""
        hg = AutoHypergraph(
            node_schema=Person,
            edge_schema=Event,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.event_type}_{sorted(x.participants)}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
        )

        hg.feed_text("""
        Leadership Retreat Decisions:
        Board Members Alice, Bob, and Charlie approved the new strategic plan.
        Executives Alice, David, and Eve formed the new innovation committee.
        Department heads Frank, Grace, and Henry committed to cross-team collaboration.
        """)

        edges = hg.data.edges
        assert isinstance(edges, list)
        assert all(isinstance(e, Event) for e in edges)

    def test_edge_has_multiple_participants(self, llm_client, embedder):
        """Test that hyperedges contain multiple participants."""
        hg = AutoHypergraph(
            node_schema=Person,
            edge_schema=Event,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.event_type}_{sorted(x.participants)}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
        )

        event = Event(event_type="workshop", participants=["Person1", "Person2", "Person3", "Person4"])
        hg._edge_memory.add([event])

        assert len(hg.data.edges) > 0
        assert len(hg.data.edges[0].participants) >= 2
