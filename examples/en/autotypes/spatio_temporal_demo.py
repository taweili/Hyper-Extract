"""
Spatio-Temporal Graph Demo - Tesla Biography

Extract spatio-temporal relationships using AutoSpatioTemporalGraph.
This demo shows how to understand both time and space together.

Usage:
    python examples/en/autotypes/spatio_temporal_demo.py
"""

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperextract.types import AutoSpatioTemporalGraph

project_root = Path(__file__).resolve().parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "en" / "tesla.md"
QUESTION_FILE = project_root / "en" / "tesla_question.md"


class Entity(BaseModel):
    """Entity node"""
    name: str = Field(description="Entity name")
    category: str = Field(description="Category", default="person")


class SpatioTemporalEvent(BaseModel):
    """Spatio-temporal event"""
    source: str = Field(description="Source entity")
    target: str = Field(description="Target entity")
    action: str = Field(description="Action or relationship")
    time: Optional[str] = Field(description="When", default=None)
    location: Optional[str] = Field(description="Where", default=None)


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  Spatio-Temporal Graph Demo")
    print("=" * 60)
    print("Extracting spatio-temporal events...")

    graph = AutoSpatioTemporalGraph[Entity, SpatioTemporalEvent](
        node_schema=Entity,
        edge_schema=SpatioTemporalEvent,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.source}-{x.action}-{x.target}",
        nodes_in_edge_extractor=lambda x: (x.source, x.target),
        time_in_edge_extractor=lambda x: x.time or "",
        location_in_edge_extractor=lambda x: x.location or "",
        llm_client=llm,
        embedder=embedder,
        observation_location="United States",
    )

    graph.feed_text(text)

    print(f"\nExtracted {len(graph.nodes)} entities and {len(graph.edges)} events")

    sorted_edges = sorted(graph.edges, key=lambda x: x.time or "")
    for edge in sorted_edges[:5]:
        time_info = f" ({edge.time})" if edge.time else ""
        loc_info = f" in {edge.location}" if edge.location else ""
        print(f"  {edge.source} --[{edge.action}]--> {edge.target}{time_info}{loc_info}")

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

    graph.show(node_label_extractor=lambda x: x.name, edge_label_extractor=lambda x: f"{x.action}@{x.time}")
