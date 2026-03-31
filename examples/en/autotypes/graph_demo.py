"""
Graph Extraction Demo - Tesla Biography

Extract entities and relationships from text using AutoGraph.
This demo shows how to build a knowledge graph from unstructured text.

Usage:
    python examples/en/autotypes/graph_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from hyperextract.types import AutoGraph


class Entity(BaseModel):
    """Entity in the knowledge graph"""
    name: str = Field(description="Entity name")
    type: str = Field(description="Entity type: person/location/invention", default="person")


class Relation(BaseModel):
    """Relation between entities"""
    source: str = Field(description="Source entity")
    target: str = Field(description="Target entity")
    type: str = Field(description="Relation type: employer/partner/rival/invented")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "en" / "tesla.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  Graph Extraction Demo")
    print("=" * 60)
    print("Extracting entities and relationships from Tesla's biography...")

    graph = AutoGraph[Entity, Relation](
        node_schema=Entity,
        edge_schema=Relation,
        llm_client=llm,
        embedder=embedder,
    )

    graph.feed_text(text)

    print(f"\nExtracted {len(graph.nodes)} entities and {len(graph.edges)} relations")

    graph.build_index()

    for q in [
        "What are Tesla's major inventions?",
        "What was the War of Currents?",
        "Tesla's relationship with Edison",
    ]:
        print(f"\nQuery: {q}")
        nodes, edges = graph.search(q, top_k_nodes=3, top_k_edges=3)
        print(f"  Entities: {[n.name for n in nodes]}")
        print(f"  Relations: {[e.type for e in edges]}")


if __name__ == "__main__":
    main()
