"""
Temporal Graph Demo - Tesla Biography

Extract temporal relationships from text using AutoTemporalGraph.
This demo shows how to understand time-based relationships.

Usage:
    python examples/en/autotypes/temporal_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from hyperextract.types import AutoTemporalGraph


class Entity(BaseModel):
    """Entity node"""
    name: str = Field(description="Entity name")
    type: str = Field(description="Type: person/location/invention", default="person")


class TimelineEvent(BaseModel):
    """Timeline event"""
    time: str = Field(description="Time (year or date)")
    event: str = Field(description="Event description")
    entities: list[str] = Field(description="Entities involved")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "en" / "tesla.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  Temporal Graph Demo")
    print("=" * 60)
    print("Extracting temporal relationships...")

    graph = AutoTemporalGraph[Entity, TimelineEvent](
        node_schema=Entity,
        edge_schema=TimelineEvent,
        llm_client=llm,
        embedder=embedder,
    )

    graph.feed_text(text)

    print(f"\nExtracted {len(graph.nodes)} entities and {len(graph.edges)} events")

    sorted_events = sorted(graph.edges, key=lambda x: x.time)
    for event in sorted_events[:5]:
        print(f"  {event.time}: {event.event}")

    graph.build_index()

    for q in ["1884", "Colorado Springs", "Wardenclyffe"]:
        print(f"\nQuery: {q}")
        nodes, edges = graph.search(q, top_k_nodes=3, top_k_edges=3)
        print(f"  Events: {[e.time for e in edges]}")


if __name__ == "__main__":
    main()
