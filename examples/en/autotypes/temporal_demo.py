"""
Temporal Graph Demo - Tesla Biography

Extract temporal relationships from text using AutoTemporalGraph.
This demo shows how to understand time-based relationships.

Usage:
    python examples/en/autotypes/temporal_demo.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from hyperextract.types import AutoTemporalGraph

project_root = Path(__file__).resolve().parent.parent.parent

load_dotenv()

INPUT_FILE = project_root / "en" / "tesla.md"
QUESTION_FILE = project_root / "en" / "tesla_question.md"


class Entity(BaseModel):
    """Entity node"""
    name: str = Field(description="Entity name")
    type: str = Field(description="Type: person/location/invention", default="person")


class TimelineEvent(BaseModel):
    """Timeline event"""
    time: str = Field(description="Time (year or date)")
    event: str = Field(description="Event description")
    entities: list[str] = Field(description="Entities involved")


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()
    with open(QUESTION_FILE, encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    print("\n" + "=" * 60)
    print("  Temporal Graph Demo")
    print("=" * 60)
    print("Extracting temporal relationships...")

    graph = AutoTemporalGraph[Entity, TimelineEvent](
        node_schema=Entity,
        edge_schema=TimelineEvent,
        node_key_extractor=lambda x: x.name,
        edge_key_extractor=lambda x: f"{x.time}-{x.event}",
        nodes_in_edge_extractor=lambda x: tuple(x.entities) if x.entities else (),
        time_in_edge_extractor=lambda x: x.time,
        llm_client=llm,
        embedder=embedder,
    )

    graph.feed_text(text)

    print(f"\nExtracted {len(graph.nodes)} entities and {len(graph.edges)} events")

    sorted_events = sorted(graph.edges, key=lambda x: x.time)
    for event in sorted_events[:5]:
        print(f"  {event.time}: {event.event}")

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

    graph.show(node_label_extractor=lambda x: x.name, edge_label_extractor=lambda x: f"{x.event}@{x.time}")
