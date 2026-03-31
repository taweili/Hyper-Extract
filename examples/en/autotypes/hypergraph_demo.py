"""
Hypergraph Demo - Tesla Biography

Extract hyper-relationships from text using AutoHyperGraph.
This demo shows how to capture multi-entity relationships.

Usage:
    python examples/en/autotypes/hypergraph_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from hyperextract.types import AutoHyperGraph


class Entity(BaseModel):
    """Entity node"""
    name: str = Field(description="Entity name")
    type: str = Field(description="Type: person/location/invention", default="person")


class HyperEdge(BaseModel):
    """Hyper-edge (multi-entity relationship)"""
    description: str = Field(description="Relationship description")
    members: list[str] = Field(description="Entities involved")
    type: str = Field(description="Relationship type")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "en" / "tesla.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  Hypergraph Demo")
    print("=" * 60)
    print("Extracting multi-entity relationships...")

    graph = AutoHyperGraph[Entity, HyperEdge](
        node_schema=Entity,
        edge_schema=HyperEdge,
        llm_client=llm,
        embedder=embedder,
    )

    graph.feed_text(text)

    print(f"\nExtracted {len(graph.nodes)} entities and {len(graph.edges)} hyper-edges")

    for edge in graph.edges[:5]:
        print(f"\n{edge.type}: {edge.description}")
        print(f"  Members: {', '.join(edge.members)}")

    graph.build_index()

    for q in ["War of Currents", "inventions", "collaboration"]:
        print(f"\nQuery: {q}")
        nodes, edges = graph.search(q, top_k_nodes=3, top_k_edges=3)
        print(f"  Found {len(edges)} related hyper-edges")


if __name__ == "__main__":
    main()
