"""
AutoSet Demo - Tesla Related Entities

Extract a deduplicated set of entities from text using AutoSet.
This demo shows how to extract and deduplicate entities based on unique keys.

Usage:
    python examples/en/autotypes/set_demo.py
"""

import sys
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

from pydantic import BaseModel, Field
from hyperextract import AutoSet


class Entity(BaseModel):
    """Entity with unique key"""
    name: str = Field(description="Entity name")
    category: str = Field(description="Category: person/location/invention", default="person")
    description: str = Field(description="Brief description", default="")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")

    input_file = Path(__file__).parent.parent.parent / "en" / "tesla.md"
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("\n" + "=" * 60)
    print("  AutoSet Demo - Tesla Entities")
    print("=" * 60)
    print("Extracting and deduplicating entities...")

    entities = AutoSet[Entity](
        item_schema=Entity,
        llm_client=llm,
        embedder=embedder,
        key_extractor=lambda x: x.name,
    )

    entities.feed_text(text)

    print(f"\nExtracted {len(entities.items)} unique entities")

    categories = {}
    for e in entities.items:
        categories.setdefault(e.category, []).append(e)

    for cat, items in sorted(categories.items()):
        print(f"\n{cat.upper()}:")
        for item in items[:5]:
            print(f"  - {item.name}")

    entities.build_index()

    for q in ["Edison", "inventions", "Westinghouse"]:
        print(f"\nQuery: {q}")
        results = entities.search(q, top_k=3)
        for r in results:
            print(f"  {r.name} ({r.category})")


if __name__ == "__main__":
    main()
