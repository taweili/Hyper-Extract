"""
KGGenGraph Demo: Knowledge Graph Generation

This demo shows how to use KGGenGraph to extract simple triple knowledge graphs from unstructured text.
KGGenGraph is a specialized wrapper for AutoGraph, optimized with prompts and data structures for triple extraction.

Usage:
    python examples/methods/kg_gen_demo.py
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract.methods.typical import KG_Gen

load_dotenv()

INPUT_FILE = project_root / "examples" / "inputs" / "sci_fi_story.md"


if __name__ == "__main__":
    print("=" * 80)
    print("Initializing KG_Gen System...")
    print("=" * 80)

    print(f"\n📄 Reading input file: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"✅ Loaded {len(content)} characters")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedder = OpenAIEmbeddings()

    kg = KG_Gen(
        llm_client=llm,
        embedder=embedder,
    )

    print("\nGenerating knowledge graph...")
    kg.feed_text(content)
    print("✓ Generation completed\n")

    print("=" * 80)
    print("EXTRACTED ENTITIES")
    print("=" * 80)

    for i, node in enumerate(kg.nodes, 1):
        print(f"\n{i}. {node.name} (Type: {node.type})")
        print(f"   Description: {node.description}")

    print(f"\n✓ Total entities: {len(kg.nodes)}\n")

    print("=" * 80)
    print("EXTRACTED RELATIONS")
    print("=" * 80)

    for i, edge in enumerate(kg.edges, 1):
        print(f"\n{i}. {edge.source} -> {edge.target}")
        print(f"   Relation: {edge.relation}")

    print(f"\n✓ Total relations: {len(kg.edges)}\n")

    print("=" * 80)
    print("Building Index...")
    print("=" * 80)

    kg.build_index()
    print("✓ Index built\n")

    print("=" * 80)
    print("Q&A: KNOWLEDGE SEARCH")
    print("=" * 80)

    queries = [
        "Who are the main characters?",
        "What is the story about?",
    ]

    for query in queries:
        print(f"\n❓ Query: {query}")
        try:
            nodes, edges = kg.search(query, top_k=3)
            print("  Entities:")
            for n in nodes[:3]:
                print(f"    - {n.name}")
            print("  Relations:")
            for e in edges[:3]:
                print(f"    - {e.source} -> {e.target}")
        except Exception as e:
            print(f"  Error: {str(e)}")

    print("\n" + "=" * 80 + "\n")
