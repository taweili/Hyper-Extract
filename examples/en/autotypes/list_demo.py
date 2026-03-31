"""
AutoList Demo - Tesla Timeline

Extract a list of items from text using AutoList.
This demo shows how to extract and merge items from multiple chunks.

Usage:
    python examples/en/autotypes/list_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from hyperextract import AutoList


class TimelineEvent(BaseModel):
    """Timeline event"""
    year: str = Field(description="Year of the event")
    title: str = Field(description="Event title")
    description: str = Field(description="Event description")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "en" / "tesla.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  AutoList Demo - Tesla Timeline")
    print("=" * 60)
    print("Extracting timeline events...")

    timeline = AutoList[TimelineEvent](
        item_schema=TimelineEvent,
        llm_client=llm,
        embedder=embedder,
    )

    timeline.feed_text(text)

    sorted_events = sorted(timeline.items, key=lambda x: x.year)
    print(f"\nExtracted {len(sorted_events)} events")

    for event in sorted_events[:5]:
        print(f"  {event.year}: {event.title}")

    timeline.build_index()

    for q in ["inventions", "Edison", "Colorado Springs"]:
        print(f"\nQuery: {q}")
        results = timeline.search(q, top_k=3)
        for r in results:
            print(f"  {r.year}: {r.title}")


if __name__ == "__main__":
    main()
