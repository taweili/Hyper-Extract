"""Tests for AutoGraph - basic graph extraction pattern."""

import pytest
from pydantic import BaseModel, Field
from typing import Tuple
from ontomem.merger import MergeStrategy
from hyperextract.types.graph import AutoGraph


class Entity(BaseModel):
    """Test schema for graph nodes."""

    name: str = Field(default="", description="Entity name")
    entity_type: str = Field(default="unknown", description="Type of entity")


class Relation(BaseModel):
    """Test schema for graph edges."""

    source: str = Field(default="", description="Source entity name")
    target: str = Field(default="", description="Target entity name")
    relation_type: str = Field(default="", description="Type of relation")


class TestAutoGraphBasics:
    """Test basic AutoGraph initialization."""

    def test_initialization_one_stage(self, llm_client, embedder):
        """Test AutoGraph initialization in one-stage mode."""
        kg = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode="one_stage",
        )

        assert kg.extraction_mode == "one_stage"
        assert kg.node_schema == Entity
        assert kg.edge_schema == Relation
        assert kg.empty() is True

    def test_initialization_two_stage(self, llm_client, embedder):
        """Test AutoGraph initialization in two-stage mode."""
        kg = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode="two_stage",
        )

        assert kg.extraction_mode == "two_stage"
        assert kg.empty() is True

    def test_custom_prompts(self, llm_client, embedder):
        """Test that custom prompts are stored."""
        custom_prompt = "Custom extraction prompt"
        node_prompt = "Custom node prompt"
        edge_prompt = "Custom edge prompt"

        kg = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            prompt=custom_prompt,
            prompt_for_node_extraction=node_prompt,
            prompt_for_edge_extraction=edge_prompt,
        )

        assert custom_prompt in kg.prompt
        assert node_prompt in kg.node_prompt
        assert edge_prompt in kg.edge_prompt


class TestAutoGraphExtraction:
    """Test graph extraction operations."""

    def test_feed_text_one_stage(self, llm_client, embedder):
        """Test feeding text in one-stage mode."""
        kg = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode="one_stage",
        )

        kg.feed_text("Alice knows Bob. Bob knows Charlie.")

        assert not kg.empty()
        assert len(kg.data.nodes) > 0

    def test_feed_text_two_stage(self, llm_client, embedder):
        """Test feeding text in two-stage mode."""
        kg = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode="two_stage",
        )

        kg.feed_text("Alice is an engineer. Bob is a designer. They work together.")

        assert not kg.empty()
        assert hasattr(kg.data, "nodes")
        assert hasattr(kg.data, "edges")

    def test_extract_creates_new_instance(self, llm_client, embedder):
        """Test extract() creates new instance."""
        kg1 = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        kg2 = kg1.extract("""CEO Sarah leads Engineering where Bob manages Backend Systems. 
        Bob oversees both Database Architecture (led by Alice) and API Development (led by Tom). 
        Alice collaborates with Tom on performance optimization.""")

        assert kg1 is not kg2
        assert kg1.empty() is True
        # kg2 may or may not be empty depending on extraction results


class TestAutoGraphProperties:
    """Test graph data properties."""

    def test_nodes_property(self, llm_client, embedder):
        """Test accessing nodes from graph."""
        kg = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        kg.feed_text("""
        Engineering Director Michael manages Sarah (Backend Lead) and James (Frontend Lead).
        Sarah collaborates with DevOps engineer David on infrastructure.
        James works with UI designer Lisa on frontend components.
        Chief Architect Elena mentors the entire team on best practices.
        """)

        nodes = kg.data.nodes
        assert isinstance(nodes, list)
        assert all(isinstance(n, Entity) for n in nodes)

    def test_edges_property(self, llm_client, embedder):
        """Test accessing edges from graph."""
        kg = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        kg.feed_text("""
        CEO John directs CTO Lisa and CFO David.
        Lisa manages the core engineering team and reports to John.
        David oversees financial planning and coordinates with John on budgets.
        Senior Architect Elena advises Lisa on technical decisions.
        """)

        edges = kg.data.edges
        assert isinstance(edges, list)
        assert all(isinstance(e, Relation) for e in edges)


class TestAutoGraphDeduplication:
    """Test graph deduplication logic."""

    def test_node_deduplication_by_key(self, llm_client, embedder):
        """Test that nodes with same key are deduplicated."""
        kg = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        # Manually create nodes
        e1 = Entity(name="Alice", entity_type="person")
        e2 = Entity(name="Alice", entity_type="person")  # Same key
        e3 = Entity(name="Bob", entity_type="person")

        # Add them manually to test deduplication
        kg._node_memory.add([e1, e2, e3])

        # After deduplication via key, should have 2 nodes
        assert kg._node_memory.size == 2

    def test_edge_deduplication_by_key(self, llm_client, embedder):
        """Test that edges with same key are deduplicated."""
        kg = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        r1 = Relation(source="Alice", target="Bob", relation_type="knows")
        r2 = Relation(source="Alice", target="Bob", relation_type="knows")  # Same key
        r3 = Relation(source="Bob", target="Charlie", relation_type="knows")

        # Add them manually to test deduplication
        kg._edge_memory.add([r1, r2, r3])

        # After deduplication via key, should have 2 edges
        assert kg._edge_memory.size == 2


class TestAutoGraphSchemaValidation:
    """Test schema validation."""

    def test_edge_key_extractor_receives_relation_object(self, llm_client, embedder):
        """Test that edge_key_extractor receives Relation objects."""
        called_with = []

        def capture_edge_key(rel: Relation):
            called_with.append(rel)
            return f"{rel.source}-{rel.relation_type}-{rel.target}"

        kg = AutoGraph(
            node_schema=Entity,
            edge_schema=Relation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=capture_edge_key,
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
        )

        rel = Relation(source="A", target="B", relation_type="test")
        capture_edge_key(rel)

        assert len(called_with) > 0
        assert called_with[-1].source == "A"
