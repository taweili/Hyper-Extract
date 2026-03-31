"""
Spatio-Temporal Graph Demo - Tesla Biography

Extract spatio-temporal relationships using AutoSpatioTemporalGraph.
This demo shows how to understand both time and space together.

Usage:
    python examples/en/autotypes/spatio_temporal_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from typing import Optional
from hyperextract.types import AutoSpatioTemporalGraph


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


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "en" / "tesla.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  Spatio-Temporal Graph Demo")
    print("=" * 60)
    print("Extracting spatio-temporal events...")

    graph = AutoSpatioTemporalGraph[Entity, SpatioTemporalEvent](
        node_schema=Entity,
        edge_schema=SpatioTemporalEvent,
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

    for q in ["New York", "Colorado Springs", "inventions"]:
        print(f"\nQuery: {q}")
        nodes, edges = graph.search(q, top_k_nodes=3, top_k_edges=3)
        print(f"  Found {len(nodes)} entities, {len(edges)} events")


if __name__ == "__main__":
    main()
