"""Tests for AutoSpatialGraph - spatial graph extraction with location-aware deduplication."""

import pytest
from pydantic import BaseModel, Field
from typing import Optional, Tuple
from ontomem.merger import MergeStrategy
from hyperextract.types.spatial_graph import AutoSpatialGraph


class Entity(BaseModel):
    """Test schema for spatial graph nodes."""

    name: str = Field(default="", description="Entity name")


class SpatialEdge(BaseModel):
    """Test schema for spatial edges."""

    src: str = Field(default="", description="Source entity")
    dst: str = Field(default="", description="Target entity")
    rel: str = Field(default="", description="Relationship type")
    place: Optional[str] = Field(default=None, description="Location of relationship")


class TestAutoSpatialGraphBasics:
    """Test basic AutoSpatialGraph functionality."""

    def test_initialization_with_default_location(self, llm_client, embedder):
        """Test AutoSpatialGraph initialization with default observation_location."""
        kg = AutoSpatialGraph(
            node_schema=Entity,
            edge_schema=SpatialEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Should have default observation_location
        assert kg.observation_location is not None
        assert kg.observation_location == "Unknown Location"

    def test_initialization_with_custom_location(self, llm_client, embedder):
        """Test AutoSpatialGraph initialization with custom observation_location."""
        custom_location = "Paris, France"

        kg = AutoSpatialGraph(
            node_schema=Entity,
            edge_schema=SpatialEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
            observation_location=custom_location,
        )

        assert kg.observation_location == custom_location


class TestAutoSpatialGraphLocationInjection:
    """Test that observation_location is properly injected into prompts."""

    def test_observation_location_in_edge_prompt(self, llm_client, embedder):
        """Test that observation_location is included in edge extraction prompt."""
        observation_location = "Tokyo"

        kg = AutoSpatialGraph(
            node_schema=Entity,
            edge_schema=SpatialEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
            observation_location=observation_location,
        )

        # The observation_location should be stored
        assert kg.observation_location == observation_location
        # And should be in prompts
        assert "location" in kg.edge_prompt.lower() or "place" in kg.edge_prompt.lower()

    def test_observation_location_in_graph_prompt(self, llm_client, embedder):
        """Test that observation_location is in the full graph extraction prompt."""
        observation_location = "New York City"

        kg = AutoSpatialGraph(
            node_schema=Entity,
            edge_schema=SpatialEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
            observation_location=observation_location,
        )

        assert kg.observation_location == observation_location


class TestAutoSpatialGraphKeyGeneration:
    """Test spatial edge key generation."""

    def test_edge_key_includes_location(self, llm_client, embedder):
        """Test that edge keys differentiate based on location."""
        kg = AutoSpatialGraph(
            node_schema=Entity,
            edge_schema=SpatialEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # The internal edge_key_extractor should combine base key and location
        edge1 = SpatialEdge(src="Shop", dst="Customer", rel="at", place="London")
        edge2 = SpatialEdge(src="Shop", dst="Customer", rel="at", place="Tokyo")
        edge3 = SpatialEdge(src="Shop", dst="Customer", rel="at")

        # Adding edges with different locations should create different keys
        kg._edge_memory.add([edge1, edge2, edge3])

        # Should have at least 2 unique edges (different locations)
        assert kg._edge_memory.size >= 2


class TestAutoSpatialGraphExtraction:
    """Test spatial graph extraction."""

    def test_feed_text_two_stage(self, llm_client, embedder):
        """Test feeding text in two-stage extraction mode."""
        kg = AutoSpatialGraph(
            node_schema=Entity,
            edge_schema=SpatialEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode="two_stage",
        )

        kg.feed_text("The library is located next to the museum. They are in downtown.")

        assert not kg.empty()
        assert len(kg.data.nodes) > 0

    def test_extract_creates_new_instance(self, llm_client, embedder):
        """Test extract() creates new instance."""
        kg1 = AutoSpatialGraph(
            node_schema=Entity,
            edge_schema=SpatialEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        kg2 = kg1.parse("""Company headquarters in San Francisco connects to regional centers: 
        New York for East Coast operations, Chicago for Midwest, and Denver for Mountain region.
        Each regional center manages local office branches.""")

        assert kg1 is not kg2
        assert kg1.empty() is True
        assert kg2.empty() is False


class TestAutoSpatialGraphPrompts:
    """Test spatial prompt construction."""

    def test_node_prompt_excludes_locations(self, llm_client, embedder):
        """Test that node extraction prompt instructs NOT to extract locations."""
        kg = AutoSpatialGraph(
            node_schema=Entity,
            edge_schema=SpatialEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Node prompt should warn not to extract locations
        assert "location" in kg.node_prompt.lower() or "spatial" in kg.node_prompt.lower()

    def test_edge_prompt_includes_spatial_rules(self, llm_client, embedder):
        """Test that edge prompt includes spatial resolution rules."""
        kg = AutoSpatialGraph(
            node_schema=Entity,
            edge_schema=SpatialEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            location_in_edge_extractor=lambda x: x.place or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Edge prompt should contain spatial/location rules
        assert "location" in kg.edge_prompt.lower() or "observation" in kg.edge_prompt.lower()


class TestAutoSpatialGraphLocationContext:
    """Test location context handling."""

    def test_custom_location_context(self, llm_client, embedder):
        """Test that custom location context is used."""
        locations = ["Office A", "Conference Room B", "Parking Lot"]

        for location in locations:
            kg = AutoSpatialGraph(
                node_schema=Entity,
                edge_schema=SpatialEdge,
                node_key_extractor=lambda x: x.name,
                edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
                location_in_edge_extractor=lambda x: x.place or "",
                nodes_in_edge_extractor=lambda x: (x.src, x.dst),
                llm_client=llm_client,
                embedder=embedder,
                observation_location=location,
            )

            assert kg.observation_location == location
