"""
Spatial Graph Demo - Tesla Biography

Extract spatial relationships from text using AutoSpatialGraph.
This demo shows how to understand location-based relationships.

Usage:
    python examples/en/autotypes/spatial_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperextract.types import AutoSpatialGraph

project_root = Path(__file__).resolve().parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "en" / "tesla.md"
QUESTION_FILE = project_root / "en" / "tesla_question.md"


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


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  Spatial Graph Demo")
    print("=" * 60)
    print("Extracting spatial relationships...")

    graph = AutoSpatialGraph[Location, SpatialRelation](
        node_schema=Location,
        edge_schema=SpatialRelation,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}-{x.relation}-{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        location_in_edge_extractor=lambda x: x.target,
        llm_client=llm,
        embedder=embedder,
        observation_location="United States",
    )

    graph.feed_text(text)

    print(f"\nExtracted {len(graph.nodes)} locations and {len(graph.edges)} relations")

    for node in graph.nodes[:5]:
        print(f"  {node.name}")

    graph.build_index()

    print("-" * 60)
    print("Q&A")
    print("-" * 60)
    for q in questions:
        print(f"\nQ: {q}")
        try:
            result = graph.chat(q)
            print(f"A: {result.content}")
        except Exception as e:
            print(f"Error: {e}")

    graph.show(node_label_extractor=lambda x: x.name, edge_label_extractor=lambda x: x.relation)
