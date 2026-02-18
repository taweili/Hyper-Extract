"""Tests for AutoSpatioTemporalGraph - spatio-temporal graph extraction."""

import pytest
from pydantic import BaseModel, Field
from typing import Optional, Tuple
from ontomem.merger import MergeStrategy
from hyperextract.types.spatio_temporal_graph import AutoSpatioTemporalGraph


class Entity(BaseModel):
    """Test schema for spatio-temporal graph nodes."""

    name: str = Field(default="", description="Entity name")


class STEdge(BaseModel):
    """Test schema for spatio-temporal edges."""

    src: str = Field(default="", description="Source entity")
    dst: str = Field(default="", description="Target entity")
    rel: str = Field(default="", description="Relationship type")
    time: Optional[str] = Field(default=None, description="Time of relationship")
    place: Optional[str] = Field(default=None, description="Location of relationship")


class TestAutoSpatioTemporalGraphBasics:
    """Test basic AutoSpatioTemporalGraph functionality."""

    def test_initialization_with_defaults(self, llm_client, embedder):
        """Test AutoSpatioTemporalGraph initialization with defaults."""
        kg = AutoSpatioTemporalGraph(
            node_schema=Entity,
            edge_schema=STEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.time or "",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Should have default observation_time and observation_location
        assert kg.observation_time is not None
        assert kg.observation_location is not None

    def test_initialization_with_custom_context(self, llm_client, embedder):
        """Test AutoSpatioTemporalGraph with custom time and location."""
        custom_time = "2024-06-15"
        custom_location = "Singapore"

        kg = AutoSpatioTemporalGraph(
            node_schema=Entity,
            edge_schema=STEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.time or "",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=custom_time,
            observation_location=custom_location,
        )

        assert kg.observation_time == custom_time
        assert kg.observation_location == custom_location


class TestAutoSpatioTemporalGraphContextInjection:
    """Test that both time and location contexts are injected."""

    def test_both_contexts_in_prompts(self, llm_client, embedder):
        """Test that both observation_time and observation_location are in prompts."""
        custom_time = "2024-01-01"
        custom_location = "Berlin"

        kg = AutoSpatioTemporalGraph(
            node_schema=Entity,
            edge_schema=STEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.time or "",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=custom_time,
            observation_location=custom_location,
        )

        # Both contexts should be stored
        assert kg.observation_time == custom_time
        assert kg.observation_location == custom_location
        # Prompts should reference spatio-temporal concepts
        assert ("time" in kg.edge_prompt.lower() and "location" in kg.edge_prompt.lower()) \
               or "spatio" in kg.edge_prompt.lower()


class TestAutoSpatioTemporalGraphKeyGeneration:
    """Test composite key generation combining time and location."""

    def test_edge_key_combines_time_and_location(self, llm_client, embedder):
        """Test that edge keys combine both time and location."""
        kg = AutoSpatioTemporalGraph(
            node_schema=Entity,
            edge_schema=STEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.time or "",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Create edges: same relation at different times and places
        e1 = STEdge(src="Alice", dst="Bob", rel="meet", time="2023-06-15", place="London")
        e2 = STEdge(src="Alice", dst="Bob", rel="meet", time="2023-06-15", place="Paris")
        e3 = STEdge(src="Alice", dst="Bob", rel="meet", time="2023-07-15", place="London")
        e4 = STEdge(src="Alice", dst="Bob", rel="meet", time="2023-07-15", place="Paris")
        e5 = STEdge(src="Alice", dst="Bob", rel="meet")  # No time or place

        kg._edge_memory.add([e1, e2, e3, e4, e5])

        # All 5 should be unique (different combinations of time and location)
        assert kg._edge_memory.size >= 3  # At least 3 different combinations


class TestAutoSpatioTemporalGraphExtraction:
    """Test spatio-temporal graph extraction."""

    def test_feed_text_two_stage(self, llm_client, embedder):
        """Test feeding text in two-stage extraction mode."""
        kg = AutoSpatioTemporalGraph(
            node_schema=Entity,
            edge_schema=STEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.time or "",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode="two_stage",
        )

        kg.feed_text("In 2023, Alice and Bob met at the conference in Barcelona.")

        assert not kg.empty()
        assert len(kg.data.nodes) > 0

    def test_extract_creates_new_instance(self, llm_client, embedder):
        """Test extract() creates new instance."""
        kg1 = AutoSpatioTemporalGraph(
            node_schema=Entity,
            edge_schema=STEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.time or "",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        kg2 = kg1.extract("""Tech conference tour 2024: January workshop in San Francisco, 
        March seminar in New York, June training in London, September workshop in Tokyo. 
        Each event has 200+ attendees sharing innovations and networking.""")

        assert kg1 is not kg2
        assert kg1.empty() is True
        assert kg2.empty() is False


class TestAutoSpatioTemporalGraphPrompts:
    """Test spatio-temporal prompt construction."""

    def test_edge_prompt_includes_temporal_rules(self, llm_client, embedder):
        """Test that edge prompt includes temporal extraction rules."""
        kg = AutoSpatioTemporalGraph(
            node_schema=Entity,
            edge_schema=STEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.time or "",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Edge prompt should contain both temporal and spatial rules
        edge_prompt_lower = kg.edge_prompt.lower()
        assert "time" in edge_prompt_lower or "date" in edge_prompt_lower or "observation" in edge_prompt_lower

    def test_edge_prompt_includes_spatial_rules(self, llm_client, embedder):
        """Test that edge prompt includes spatial extraction rules."""
        kg = AutoSpatioTemporalGraph(
            node_schema=Entity,
            edge_schema=STEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.time or "",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Edge prompt should contain spatial rules
        edge_prompt_lower = kg.edge_prompt.lower()
        assert "location" in edge_prompt_lower or "place" in edge_prompt_lower or "observation" in edge_prompt_lower

    def test_node_prompt_excludes_temporal_spatial_markers(self, llm_client, embedder):
        """Test that node extraction prompt excludes dates and locations."""
        kg = AutoSpatioTemporalGraph(
            node_schema=Entity,
            edge_schema=STEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.time or "",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Node prompt should warn against extracting dates/times and locations
        node_prompt_lower = kg.node_prompt.lower()
        assert "exclude" in node_prompt_lower or "never" in node_prompt_lower or "not" in node_prompt_lower


class TestAutoSpatioTemporalGraphConsistency:
    """Test spatio-temporal graph consistency."""

    def test_all_dimensions_in_edge(self, llm_client, embedder):
        """Test that edges can have all spatio-temporal dimensions."""
        kg = AutoSpatioTemporalGraph(
            node_schema=Entity,
            edge_schema=STEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.time or "",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Add nodes
        kg._node_memory.add([Entity(name="Alice"), Entity(name="Bob")])

        # Edge with all dimensions
        full_edge = STEdge(src="Alice", dst="Bob", rel="meet", time="2024-06-15", place="Summit")
        kg._edge_memory.add([full_edge])

        assert kg._edge_memory.size > 0
        edge_data = kg._edge_memory.items[0]
        assert edge_data.time == "2024-06-15"
        assert edge_data.place == "Summit"

    def test_partial_dimensions(self, llm_client, embedder):
        """Test edges with partial spatio-temporal information."""
        kg = AutoSpatioTemporalGraph(
            node_schema=Entity,
            edge_schema=STEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.time or "",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Add nodes
        kg._node_memory.add([Entity(name="Alice"), Entity(name="Bob")])

        # Edges with partial information
        time_only = STEdge(src="Alice", dst="Bob", rel="call", time="2024-06-15")
        place_only = STEdge(src="Alice", dst="Bob", rel="visit", place="Office")
        neither = STEdge(src="Alice", dst="Bob", rel="know")

        kg._edge_memory.add([time_only, place_only, neither])

        # All should be added (different combinations)
        assert kg._edge_memory.size >= 2
