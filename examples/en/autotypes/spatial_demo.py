"""
Spatial Graph Demo - Tesla Biography

Extract spatial relationships from text using AutoSpatialGraph.
This demo shows how to understand location-based relationships.

Usage:
    python examples/en/autotypes/spatial_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from hyperextract.types import AutoSpatialGraph


class Location(BaseModel):
    """Location entity"""
    name: str = Field(description="Location name")
    category: str = Field(description="Category: university/corporate/historical", default="historical")
    description: str = Field(description="Brief description", default="")


class SpatialRelation(BaseModel):
    """Spatial relationship"""
    source: str = Field(description="Source location")
    target: str = Field(description="Target location")
    relation: str = Field(description="Spatial relationship type")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "en" / "tesla.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  Spatial Graph Demo")
    print("=" * 60)
    print("Extracting spatial relationships...")

    graph = AutoSpatialGraph[Location, SpatialRelation](
        node_schema=Location,
        edge_schema=SpatialRelation,
        llm_client=llm,
        embedder=embedder,
        observation_location="United States",
    )

    graph.feed_text(text)

    print(f"\nExtracted {len(graph.nodes)} locations and {len(graph.edges)} relations")

    for node in graph.nodes[:5]:
        print(f"  {node.name}")

    graph.build_index()

    for q in ["New York", "Colorado Springs", "labs"]:
        print(f"\nQuery: {q}")
        nodes, edges = graph.search(q, top_k_nodes=3, top_k_edges=3)
        print(f"  Locations: {[n.name for n in nodes]}")


if __name__ == "__main__":
    main()
