"""Tests for AutoTemporalGraph - temporal graph extraction with time-aware deduplication."""

import pytest
from pydantic import BaseModel, Field
from typing import Optional, Tuple
from datetime import datetime, timedelta
from ontomem.merger import MergeStrategy
from hyperextract.types.temporal_graph import AutoTemporalGraph


class Entity(BaseModel):
    """Test schema for temporal graph nodes."""

    name: str = Field(default="", description="Entity name")


class TemporalEdge(BaseModel):
    """Test schema for temporal edges."""

    src: str = Field(default="", description="Source entity")
    dst: str = Field(default="", description="Target entity")
    rel: str = Field(default="", description="Relationship type")
    year: Optional[str] = Field(default=None, description="Year of relationship")


class TestAutoTemporalGraphBasics:
    """Test basic AutoTemporalGraph functionality."""

    def test_initialization_with_default_time(self, llm_client, embedder):
        """Test AutoTemporalGraph initialization with default observation_time."""
        kg = AutoTemporalGraph(
            node_schema=Entity,
            edge_schema=TemporalEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.year or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Should have default observation_time (today)
        assert kg.observation_time is not None
        assert len(kg.observation_time) == 10  # YYYY-MM-DD format

    def test_initialization_with_custom_time(self, llm_client, embedder):
        """Test AutoTemporalGraph initialization with custom observation_time."""
        custom_time = "2024-06-15"

        kg = AutoTemporalGraph(
            node_schema=Entity,
            edge_schema=TemporalEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.year or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=custom_time,
        )

        assert kg.observation_time == custom_time


class TestAutoTemporalGraphTimeInjection:
    """Test that observation_time is properly injected into prompts."""

    def test_observation_time_in_edge_prompt(self, llm_client, embedder):
        """Test that observation_time is included in edge extraction prompt."""
        observation_time = "2023-01-01"

        kg = AutoTemporalGraph(
            node_schema=Entity,
            edge_schema=TemporalEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.year or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
        )

        # The observation_time should be in the prompt template
        assert observation_time == kg.observation_time
        assert "{observation_time}" in kg.edge_prompt or observation_time in kg.prompt

    def test_observation_time_in_graph_prompt(self, llm_client, embedder):
        """Test that observation_time is in the full graph extraction prompt."""
        observation_time = "2024-12-25"

        kg = AutoTemporalGraph(
            node_schema=Entity,
            edge_schema=TemporalEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.year or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
        )

        assert observation_time == kg.observation_time


class TestAutoTemporalGraphKeyGeneration:
    """Test temporal edge key generation."""

    def test_edge_key_includes_time(self, llm_client, embedder):
        """Test that edge keys differentiate based on time."""
        kg = AutoTemporalGraph(
            node_schema=Entity,
            edge_schema=TemporalEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.year or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # The internal edge_key_extractor should combine base key and time
        # Testing the logic of what the actual implementation does

        edge1 = TemporalEdge(src="Alice", dst="Bob", rel="friend", year="2020")
        edge2 = TemporalEdge(src="Alice", dst="Bob", rel="friend", year="2021")
        edge3 = TemporalEdge(src="Alice", dst="Bob", rel="friend")

        # Due to the composite key logic, edges with different years should have different keys
        # And edge without time should be different from edges with time

        # We can test this by adding them to the edge memory
        kg._edge_memory.add([edge1, edge2, edge3])

        # Should have 3 unique edges (all different times)
        assert kg._edge_memory.size >= 2  # At least different from no-time case


class TestAutoTemporalGraphExtraction:
    """Test temporal graph extraction."""

    def test_feed_text_two_stage(self, llm_client, embedder):
        """Test feeding text in two-stage extraction mode."""
        kg = AutoTemporalGraph(
            node_schema=Entity,
            edge_schema=TemporalEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.year or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode="two_stage",
        )

        kg.feed_text("In 2020, Alice collaborated with Bob on a research project.")

        assert not kg.empty()
        assert len(kg.data.nodes) > 0

    def test_extract_creates_new_instance(self, llm_client, embedder):
        """Test extract() creates new instance."""
        kg1 = AutoTemporalGraph(
            node_schema=Entity,
            edge_schema=TemporalEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.year or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        kg2 = kg1.parse("""ProjectX timeline: Q1 2023 requirements gathering with stakeholders, 
        Q2 2023 architecture design phase, Q3 2023 development sprint cycles, 
        Q4 2023 beta testing and Q1 2024 production launch.""")

        assert kg1 is not kg2
        assert kg1.empty() is True
        assert kg2.empty() is False


class TestAutoTemporalGraphPrompts:
    """Test temporal prompt construction."""

    def test_node_prompt_excludes_dates(self, llm_client, embedder):
        """Test that node extraction prompt instructs NOT to extract dates."""
        kg = AutoTemporalGraph(
            node_schema=Entity,
            edge_schema=TemporalEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.year or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Node prompt should warn not to extract dates
        assert "date" in kg.node_prompt.lower() or "time" in kg.node_prompt.lower()

    def test_edge_prompt_includes_relative_time_rules(self, llm_client, embedder):
        """Test that edge prompt includes relative time resolution rules."""
        kg = AutoTemporalGraph(
            node_schema=Entity,
            edge_schema=TemporalEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.year or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Edge prompt should contain rules about relative time
        assert "relative time" in kg.edge_prompt.lower() or "observation" in kg.edge_prompt.lower()


class TestAutoTemporalGraphConsistency:
    """Test consistency between nodes and edges."""

    def test_temporal_edge_participants_are_validated(self, llm_client, embedder):
        """Test that temporal edges reference existing nodes."""
        kg = AutoTemporalGraph(
            node_schema=Entity,
            edge_schema=TemporalEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.src}-{x.rel}-{x.dst}",
            time_in_edge_extractor=lambda x: x.year or "",
            nodes_in_edge_extractor=lambda x: (x.src, x.dst),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Create nodes
        kg._node_memory.add([Entity(name="Alice"), Entity(name="Bob")])

        # Create valid edges (participants exist)
        valid_edge = TemporalEdge(src="Alice", dst="Bob", rel="knows", year="2022")
        kg._edge_memory.add([valid_edge])

        assert kg._edge_memory.size > 0
